from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    CfnOutput,
)
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建 S3 存储桶用于存储结果
        self.result_bucket = s3.Bucket(
            self, "EvalResultBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True,  # 启用版本控制
            encryption=s3.BucketEncryption.S3_MANAGED,  # 使用 S3 管理的加密
        )

        # 输出存储桶名称
        CfnOutput(self, "ResultBucketName", 
            value=self.result_bucket.bucket_name,
            description="评估结果存储桶的名称"
        ) 