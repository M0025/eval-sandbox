# 这个文件是CDK的入口文件

import aws_cdk as cdk
from stacks.ecr_stack import ECRStack
from stacks.codebuild_stack import CodeBuildStack
from stacks.ecs_stack import EcsStack
from stacks.s3_stack import S3Stack
from stacks.vpc_stack import VpcStack
# from stacks.lambda_stack import LambdaStack
from stacks.ssm_stack import SystemsManagerStack
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

# 创建 CodeBuild stack
codebuild_stack = CodeBuildStack(app, 'EvalSandboxCodeBuild', ecr_stack.ecr_repo)
cdk.Tags.of(codebuild_stack).add("Application", "EvalSandbox")

# 创建 ECS stack
ecs_stack = EcsStack(app, 'EvalSandboxECS', 
    ecr_repository=ecr_stack.ecr_repo,
    result_bucket=s3_stack.result_bucket,
    vpc=vpc_stack.vpc
)
cdk.Tags.of(ecs_stack).add("Application", "EvalSandbox")

# # 创建 Lambda stack
# lambda_stack = LambdaStack(
#     app, "EvalSandboxLambda",
#     cluster=ecs_stack.ecs_cluster,
#     task_definition=ecs_stack.task_definition
# )
# cdk.Tags.of(lambda_stack).add("Application", "EvalSandbox")

# 创建 Systems Manager stack
ssm_stack = SystemsManagerStack(
    app, "EvalSandboxSSM",
    cluster_name=ecs_stack.ecs_cluster.cluster_name,
    task_definition_arn=ecs_stack.task_definition.task_definition_arn,
    # lambda_function_arn=lambda_stack.trigger_function.function_arn,
    ecr_repository_name=ecr_stack.ecr_repo.repository_name,
    s3_bucket_name=s3_stack.result_bucket.bucket_name,
    vpc_id=vpc_stack.vpc.vpc_id
)
cdk.Tags.of(ssm_stack).add("Application", "EvalSandbox")

# 创建 CloudWatch stack
cloudwatch_stack = CloudWatchStack(
    app, "EvalSandboxCloudWatch",
    ecs_cluster_name=ecs_stack.ecs_cluster.cluster_name
)
cdk.Tags.of(cloudwatch_stack).add("Application", "EvalSandbox")

# 添加依赖关系
ecs_stack.add_dependency(vpc_stack)  # ECS 依赖于 VPC
ecs_stack.add_dependency(ecr_stack)
ecs_stack.add_dependency(s3_stack)
ecs_stack.add_dependency(codebuild_stack)
# lambda_stack.add_dependency(ecs_stack)
ssm_stack.add_dependency(ecs_stack)
# ssm_stack.add_dependency(lambda_stack)
cloudwatch_stack.add_dependency(ecs_stack)

app.synth()