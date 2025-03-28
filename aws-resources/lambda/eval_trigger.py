import json
import boto3
import logging
from datetime import datetime, timedelta

# 设置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 初始化 AWS 客户端
cloudwatch = boto3.client('cloudwatch-logs')
lambda_client = boto3.client('lambda')
dynamodb = boto3.client('dynamodb')

def get_last_check_time():
    """从 DynamoDB 获取上次检查时间"""
    try:
        response = dynamodb.get_item(
            TableName='EvalTriggerState',
            Key={'id': {'S': 'last_check'}}
        )
        if 'Item' in response:
            return int(response['Item']['timestamp']['N'])
        return int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)
    except Exception as e:
        logger.error(f"Error getting last check time: {str(e)}")
        return int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

def update_last_check_time():
    """更新 DynamoDB 中的最后检查时间"""
    try:
        current_time = int(datetime.now().timestamp() * 1000)
        dynamodb.put_item(
            TableName='EvalTriggerState',
            Item={
                'id': {'S': 'last_check'},
                'timestamp': {'N': str(current_time)}
            }
        )
        return current_time
    except Exception as e:
        logger.error(f"Error updating last check time: {str(e)}")
        return None

def handler(event, context):
    """
    监控 CloudWatch 日志组中的特定日志
    当检测到成功运行评估任务时触发新的 Lambda 函数
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # 目标日志组
    log_group_name = '/aws/ecs/training-task'
    
    try:
        # 获取上次检查时间
        last_check_time = get_last_check_time()
        
        # 获取最新的日志事件
        response = cloudwatch.get_log_events(
            logGroupName=log_group_name,
            logStreamName=event['detail']['logStreamName'],
            limit=10,
            startFromHead=False
        )
        
        # 检查日志事件
        for log_event in response['events']:
            # 只处理上次检查时间之后的日志
            if log_event['timestamp'] <= last_check_time:
                continue
                
            log_message = log_event['message']
            
            # 检查是否包含成功运行评估任务的关键字
            if "Successfully ran task(asr)" in log_message:
                logger.info("Found successful evaluation task completion!")
                
                # 触发新的 Lambda 函数
                lambda_client.invoke(
                    FunctionName=context.function_name,
                    InvocationType='Event',
                    Payload=json.dumps({
                        'message': 'Evaluation task completed successfully',
                        'original_event': log_event,
                        'timestamp': log_event['timestamp']
                    })
                )
                
                # 更新最后检查时间
                update_last_check_time()
                
                return {
                    'statusCode': 200,
                    'body': json.dumps('Successfully triggered new process')
                }
        
        # 如果没有找到匹配的日志，也更新最后检查时间
        update_last_check_time()
        
        return {
            'statusCode': 200,
            'body': json.dumps('No matching logs found')
        }
        
    except Exception as e:
        logger.error(f"Error processing logs: {str(e)}")
        raise 