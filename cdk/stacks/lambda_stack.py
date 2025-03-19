from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_iam as iam,
    aws_logs_destinations as destinations,
    Duration,
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
            code=_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "lambda_functions")),
            timeout=Duration.seconds(30),
            environment={
                'CODEBUILD_PROJECT_NAME': 'EvalSandboxCodeBuild'  # CodeBuild项目名称
            }
        )

        # 添加启动CodeBuild的权限
        log_processor.add_to_role_policy(
            iam.PolicyStatement(
                actions=['codebuild:StartBuild'],
                resources=['*']  # 在实际应用中应该限制为特定的CodeBuild项目ARN
            )
        )

        # 创建日志订阅
        log_group = logs.LogGroup.from_log_group_name(
            self, "ECSLogGroup",
            log_group_name="/aws/ecs/eval-cluster"
        )

        # 创建订阅过滤器
        logs.SubscriptionFilter(
            self, "LogSubscription",
            log_group=log_group,
            destination=destinations.LambdaDestination(log_processor),
            filter_pattern=logs.FilterPattern.literal("TASK_COMPLETED")
        ) 