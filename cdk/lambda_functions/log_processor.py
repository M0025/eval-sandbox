import json
import base64
import gzip
import io
import boto3
import os
from datetime import datetime, timedelta

def handler(event, context):
    print("收到CloudWatch日志事件")
    
    # 获取ECS客户端
    ecs = boto3.client('ecs')
    
    # 获取当前时间
    now = datetime.now()
    # 获取5分钟前的时间
    five_minutes_ago = now - timedelta(minutes=5)
    
    try:
        # 获取最近的任务
        recent_tasks = ecs.list_tasks(
            cluster=os.environ['ECS_CLUSTER_NAME'],
            family=os.environ['ECS_TASK_FAMILY'],
            desiredStatus='STOPPED',
            sort='DESC',
            maxResults=1
        )
        
        if recent_tasks['taskArns']:
            # 获取最近任务的详细信息
            task_info = ecs.describe_tasks(
                cluster=os.environ['ECS_CLUSTER_NAME'],
                tasks=[recent_tasks['taskArns'][0]]
            )
            if task_info['tasks']:
                last_task_time = task_info['tasks'][0]['stoppedAt']
                # 如果最后一次任务是在5分钟内，则不触发新的任务
                if last_task_time > five_minutes_ago:
                    print(f"最近一次任务是在 {last_task_time}，跳过触发")
                    return {
                        'statusCode': 200,
                        'body': json.dumps('跳过触发，因为最近有任务')
                    }
        
        # 处理CloudWatch日志事件
        for record in event['Records']:
            # 解码base64数据
            payload = base64.b64decode(record['kinesis']['data'])
            # 解压缩gzip数据
            decompressed_data = gzip.decompress(payload)
            # 解码为字符串并解析JSON
            log_data = json.loads(decompressed_data.decode('utf-8'))
            
            # 检查日志消息
            for log_event in log_data['logEvents']:
                if "TASK_COMPLETED" in log_event['message']:
                    print(f"检测到任务完成消息: {log_event['message']}")
                    
                    # 直接触发新的ECS任务
                    response = ecs.run_task(
                        cluster=os.environ['ECS_CLUSTER_NAME'],
                        taskDefinition=os.environ['ECS_TASK_FAMILY'],
                        networkConfiguration={
                            'awsvpcConfiguration': {
                                'subnets': os.environ['ECS_SUBNET_IDS'].split(','),
                                'securityGroups': os.environ['ECS_SECURITY_GROUP_IDS'].split(','),
                                'assignPublicIp': 'ENABLED'
                            }
                        }
                    )
                    task_arn = response['tasks'][0]['taskArn']
                    print(f"触发了新的ECS任务: {task_arn}")
                    
                    return {
                        'statusCode': 200,
                        'body': json.dumps(f'成功触发新的任务: {task_arn}')
                    }
        
        return {
            'statusCode': 200,
            'body': json.dumps('没有检测到任务完成消息')
        }
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'错误: {str(e)}')
        } 