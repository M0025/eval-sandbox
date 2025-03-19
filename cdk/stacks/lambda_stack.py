from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
    aws_logs_destinations as destinations,
    Duration
)
from constructs import Construct
import os

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # 创建Lambda函数
        log_processor = _lambda.Function(
            self, "LogProcessor",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="log_processor.handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            timeout=Duration.seconds(30),
            environment={
                "ECS_CLUSTER_NAME": "eval-cluster",
                "ECS_TASK_FAMILY": "eval-python-task",
                "ECS_SUBNET_IDS": "subnet-0c0e3f387b7a2b9a4,subnet-0d0e3f387b7a2b9a5",  # 替换为实际的子网ID
                "ECS_SECURITY_GROUP_IDS": "sg-0c0e3f387b7a2b9a4"  # 替换为实际的安全组ID
            }
        )
        
        # 添加ECS权限
        log_processor.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecs:RunTask",
                    "ecs:ListTasks",
                    "ecs:DescribeTasks"
                ],
                resources=["*"]
            )
        )
        
        # 添加CloudWatch Logs权限
        log_processor.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        # 创建CloudWatch日志订阅过滤器
        logs.SubscriptionFilter(
            self, "LogSubscription",
            log_group=logs.LogGroup.from_log_group_name(
                self, "EcsLogGroup",
                log_group_name="/aws/ecs/eval-cluster"
            ),
            destination=destinations.LambdaDestination(log_processor),
            filter_pattern=logs.FilterPattern.literal("TASK_COMPLETED")
        ) 