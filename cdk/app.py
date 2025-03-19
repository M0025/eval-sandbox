#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.ecr_stack import ECRStack
from stacks.codebuild_stack import CodeBuildStack
from stacks.ecs_stack import EcsStack
from stacks.s3_stack import S3Stack
from stacks.vpc_stack import VpcStack
from stacks.iam_stack import IamStack
from stacks.lambda_stack import LambdaStack

from stacks.cloudwatch_stack import CloudWatchStack

app = cdk.App()

# 创建 VPC stack
vpc_stack = VpcStack(app, 'EvalSandboxVPC')
cdk.Tags.of(vpc_stack).add("Application", "EvalSandbox")

# 创建 ECR stack
ecr_stack = ECRStack(app, 'EvalSandboxECR')
cdk.Tags.of(ecr_stack).add("Application", "EvalSandbox")

# 创建 S3 stack
s3_stack = S3Stack(app, 'EvalSandboxS3')
cdk.Tags.of(s3_stack).add("Application", "EvalSandbox")

# 创建 CloudWatch stack - 提前创建日志组
cloudwatch_stack = CloudWatchStack(app, "EvalSandboxCloudWatch")
cdk.Tags.of(cloudwatch_stack).add("Application", "EvalSandbox")

# 创建 IAM stack - 创建执行和任务角色
iam_stack = IamStack(app, 'EvalSandboxIAM')
cdk.Tags.of(iam_stack).add("Application", "EvalSandbox")

# 创建 ECS stack
ecs_stack = EcsStack(app, 'EvalSandboxECS', 
    ecr_repository=ecr_stack.ecr_repo,
    result_bucket=s3_stack.result_bucket,
    vpc=vpc_stack.vpc,
    task_role=iam_stack.task_role,
    execution_role=iam_stack.task_execution_role
)
cdk.Tags.of(ecs_stack).add("Application", "EvalSandbox")

# 创建 Lambda stack
lambda_stack = LambdaStack(app, "EvalSandboxLambda")
cdk.Tags.of(lambda_stack).add("Application", "EvalSandbox")

# 创建 CodeBuild stack
codebuild_stack = CodeBuildStack(
    app, 'EvalSandboxCodeBuild', 
    repository=ecr_stack.ecr_repo,
    task_role=iam_stack.task_role,
    execution_role=iam_stack.task_execution_role
)
cdk.Tags.of(codebuild_stack).add("Application", "EvalSandbox")

# 添加依赖关系
cloudwatch_stack.add_dependency(vpc_stack)
iam_stack.add_dependency(cloudwatch_stack)  # IAM依赖于CloudWatch（日志组先创建）
ecs_stack.add_dependency(vpc_stack)
ecs_stack.add_dependency(ecr_stack)
ecs_stack.add_dependency(s3_stack)
ecs_stack.add_dependency(iam_stack)  # ECS依赖于IAM
ecs_stack.add_dependency(cloudwatch_stack)  # ECS依赖于CloudWatch
codebuild_stack.add_dependency(ecs_stack)  # CodeBuild依赖于ECS
lambda_stack.add_dependency(ecs_stack)  # Lambda依赖于ECS

app.synth()