from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ecr as ecr,
    CfnOutput,
)
from constructs import Construct
import os

class EcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 ecr_repository: ecr.Repository,
                 result_bucket: s3.IBucket,
                 vpc: ec2.IVpc,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建 ECS 集群
        cluster = ecs.Cluster(
            self, "EvalCluster",
            vpc=vpc,
            cluster_name="eval-cluster"
        )

        # 创建任务定义
        task_definition = ecs.FargateTaskDefinition(
            self, "EvalTaskDef",
            cpu=256,  # 0.25 vCPU
            memory_limit_mib=512,  # 0.5 GB
        )

        # 添加容器到任务定义
        container = task_definition.add_container(
            "EvalContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr_repository,
                tag=os.environ.get("IMAGE_TAG", "latest")
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="eval-container"
            ),
        )

        # 创建 Fargate 服务
        fargate_service = ecs.FargateService(
            self, "EvalService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=0,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_groups=[
                ec2.SecurityGroup(
                    self, "EcsSecurityGroup",
                    vpc=vpc,
                    description="Security group for ECS service in public subnet",
                    allow_all_outbound=True
                )
            ],
            assign_public_ip=True,
        )

        # 添加 ECR 拉取权限
        ecr_repository.grant_pull(task_definition.task_role)
        ecr_repository.grant_pull(task_definition.execution_role)
        
        # 添加 S3 写入权限
        result_bucket.grant_write(task_definition.task_role)

        # 允许 CodeBuild 调用 ECS 任务
        task_definition.task_role.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecs:RunTask",
                    "ecs:StopTask",
                    "ecs:DescribeTasks"
                ],
                resources=["*"]
            )
        )

        # 输出重要信息
        CfnOutput(self, "ECSClusterName", value=cluster.cluster_name)
        CfnOutput(self, "TaskDefinitionArn", value=task_definition.task_definition_arn)

        # 保存供其他 Stack 使用的属性
        self.ecs_cluster = cluster
        self.task_definition = task_definition
