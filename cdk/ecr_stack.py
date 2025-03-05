from aws_cdk import aws_ecr as ecr
from aws_cdk import Stack
from constructs import Construct

# 最开始引入基础的组件: 基本的ECR组件和 核心组件

# 接下来创建一个ECRStack类，继承自core.Stack

class ECRStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建一个ECR仓库
        self.ecr_repo = ecr.Repository(
            self, 'EvalSandboxECR',
            repository_name='eval-sandbox-ecr'
            )
        
        