from aws_cdk import (
    Stack,
    aws_logs as logs,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class CloudWatchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, ecs_cluster_name: str = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 引用已存在的日志组，而不是尝试创建新的
        log_group_name = "/aws/ecs/eval-cluster"
        self.ecs_log_group = logs.LogGroup.from_log_group_name(
            self, "EcsLogGroup",
            log_group_name
        )
        
        # 输出日志组名称
        CfnOutput(self, "EcsLogGroupName", value=self.ecs_log_group.log_group_name)