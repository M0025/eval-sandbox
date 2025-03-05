# 这个文件是CDK的入口文件

import aws_cdk as cdk
from ecr_stack import ECRStack
from codebuild_stack import CodeBuildStack

app = cdk.App()

# 创建ECR stack
ecr_stack = ECRStack(app, 'EvalSandboxECR')

# 创建CodeBuild stack
codebuild_stack = CodeBuildStack(app, 'EvalSandboxCodeBuild', ecr_stack.ecr_repo)

app.synth()