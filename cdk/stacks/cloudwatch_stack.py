from aws_cdk import (
    Stack,
    aws_logs as logs,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class CloudWatchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 ecs_cluster_name: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 定义日志组名称
        log_group_name = f"/aws/ecs/{ecs_cluster_name}"
        
        # 直接引用现有的日志组，不尝试创建
        log_group = logs.LogGroup.from_log_group_name(
            self, "EcsLogGroup", 
            log_group_name
        )
        
        # 输出日志组名称
        CfnOutput(
            self, "LogGroupName",
            value=log_group.log_group_name
        ) 