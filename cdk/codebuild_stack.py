from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_codecommit as codecommit,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)

from constructs import Construct

class CodeBuildStack(Stack):
    def __init__(self, scope: Construct, id: str, repository,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

         # 获取 GitHub token
        github_token = secretsmanager.Secret.from_secret_name_v2(
            self, 'GitHubToken',
            'github-oauth-token'
        )
        
        # 创建一个IAM角色,允许codebulid访问ECR
        # TODO:完全看不懂啊!!!
        self.codebuild_role = iam.Role(
            self, 'EvalSandboxCodeBuildRole',
            assumed_by=iam.ServicePrincipal('codebuild.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodeBuildDeveloperAccess'),
            ]
        )
        repository.grant_pull(self.codebuild_role)

        # 创建一个CodeBuild项目
        # Codebuild项目需要一个环境变量,指向ECR仓库
        # 需要一个环境变量,指向代码仓库
        # 需要一个环境变量,指向代码仓库的webhook
        # 需要一个环境变量,指向代码仓库的webhook过滤器

        self.codebuild_project = codebuild.Project(
            self, 'EvalSandboxCodeBuild',
            project_name='eval-sandbox-codebuild',
            source=codebuild.Source.git_hub(
                    owner='M0025',
                    repo='eval-sandbox',
                    webhook=True,
                    webhook_filters=[
                        codebuild.FilterGroup.in_event_of(
                            codebuild.EventAction.PUSH
                        ).and_branch_is('main')
                    ],
                    oauth_token=github_token.secret_value
                ),
            # 指定构建环境
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2023_4,
                privileged=True,
                environment_variables={
                    "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(
                        value=Stack.of(self).region
                    ),
                    "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                        value=Stack.of(self).account
                    ),
                    "REPOSITORY_URI": codebuild.BuildEnvironmentVariable(
                        value=repository.repository_uri
                    )
                }
            ),
            build_spec=codebuild.BuildSpec.from_source_filename('docker/buildspec.yml')
        )