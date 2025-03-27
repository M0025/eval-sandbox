import json
import boto3
import logging

# 设置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 初始化 AWS 客户端
cloudwatch = boto3.client('cloudwatch-logs')
lambda_client = boto3.client('lambda')

def handler(event, context):
    """
    监控 CloudWatch 日志组中的特定日志
    当检测到成功运行评估任务时触发新的 Lambda 函数
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # 目标日志组
    log_group_name = '/aws/ecs/eval-cluster'
    
    try:
        # 获取最新的日志事件
        response = cloudwatch.get_log_events(
            logGroupName=log_group_name,
            logStreamName=event['detail']['logStreamName'],
            limit=10,
            startFromHead=False
        )
        
        # 检查日志事件
        for event in response['events']:
            log_message = event['message']
            
            # 检查是否包含成功运行评估任务的关键字
            if "Successfully ran task(evaluation)" in log_message:
                logger.info("Found successful evaluation task completion!")
                
                # 触发新的 Lambda 函数
                lambda_client.invoke(
                    FunctionName=context.function_name,
                    InvocationType='Event',
                    Payload=json.dumps({
                        'message': 'Evaluation task completed successfully',
                        'original_event': event
                    })
                )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps('Successfully triggered new process')
                }
                
        return {
            'statusCode': 200,
            'body': json.dumps('No matching logs found')
        }
        
    except Exception as e:
        logger.error(f"Error processing logs: {str(e)}")
        raise 