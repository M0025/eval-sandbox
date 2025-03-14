from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
)
from constructs import Construct

class IamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建ECS任务执行角色（用于拉取镜像和发送日志）
        self.task_execution_role = iam.Role(
            self, "EcsTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="eval-task-execution-role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # 添加CloudWatch日志权限（使用通配符）
        self.task_execution_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "logs:DescribeLogGroups"
            ],
            resources=["*"]  # 使用通配符，不引用特定日志组
        ))

        # 创建ECS任务角色（用于任务运行时的权限）
        self.task_role = iam.Role(
            self, "EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="eval-task-role"
        )

        # 添加任务角色权限
        self.task_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=["*"]
        ))

        # 输出角色ARN便于引用
        CfnOutput(self, "TaskRoleArn", value=self.task_role.role_arn, export_name="EvalTaskRoleArn")
        CfnOutput(self, "TaskExecutionRoleArn", value=self.task_execution_role.role_arn, export_name="EvalTaskExecutionRoleArn")
