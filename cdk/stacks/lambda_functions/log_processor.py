import os
import boto3
import json
import base64
import gzip
import io

def handler(event, context):
    # 解码CloudWatch日志数据
    compressed_data = base64.b64decode(event['awslogs']['data'])
    decompressed_data = gzip.GzipFile(fileobj=io.BytesIO(compressed_data)).read()
    log_data = json.loads(decompressed_data.decode('utf-8'))
    
    # 检查日志事件
    for log_event in log_data['logEvents']:
        # 检查日志中是否包含"TASK_COMPLETED"
        if "TASK_COMPLETED" in log_event['message']:
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