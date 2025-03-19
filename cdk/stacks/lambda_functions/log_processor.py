import os
import boto3
import json

def handler(event, context):
    # 解码并检查日志事件
    for log_event in event['awslogs']['data']:
        # 检查日志中是否包含"任务完成!"
        if "任务完成!" in log_event['message']:
            # 获取CodeBuild客户端
            codebuild = boto3.client('codebuild')
            
            # 启动CodeBuild项目
            response = codebuild.start_build(
                projectName=os.environ['CODEBUILD_PROJECT_NAME']
            )
            
            print(f"触发了新的CodeBuild构建: {response['build']['id']}")
            
    return {
        'statusCode': 200,
        'body': json.dumps('处理完成')
    } 