from aws_cdk import (
    Stack,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct

class CloudWatchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 ecs_cluster_name: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建 CloudWatch 日志组
        log_group = logs.LogGroup(
            self, "EcsLogGroup",
            log_group_name=f"/aws/ecs/{ecs_cluster_name}",
            retention=logs.RetentionDays.ONE_WEEK
        )

        # 输出日志组名称
        CfnOutput(
            self, "LogGroupName",
            value=log_group.log_group_name
        ) 