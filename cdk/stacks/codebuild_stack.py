from aws_cdk import (
    Stack,
    SecretValue,
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
        
        # 创建一个IAM角色,允许codebuild访问ECR和ECS
        self.codebuild_role = iam.Role(
            self, 'EvalSandboxCodeBuildRole',
            assumed_by=iam.ServicePrincipal('codebuild.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodeBuildDeveloperAccess'),
            ]
        )

        # 添加访问 Secrets Manager 的权限
        self.codebuild_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'secretsmanager:GetSecretValue',
                'secretsmanager:DescribeSecret'
            ],
            resources=[github_token.secret_arn]
        ))

        # 添加 ECS 和 EC2 访问权限
        self.codebuild_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'ecs:RunTask',
                'ecs:StopTask',
                'ecs:DescribeTasks',
                'ecs:ListTasks',
                'ecs:DescribeTaskDefinition',
                'ecs:ListTaskDefinitions',
                'ecs:DescribeClusters',
                'ec2:DescribeSubnets',
                'ec2:DescribeVpcs',
                'ec2:DescribeSecurityGroups',
                'iam:PassRole'
            ],
            resources=['*']
        ))

        # 修改这里：添加 ECR 完整访问权限
        repository.grant_pull_push(self.codebuild_role)

        # 创建CodeBuild项目
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
                    ),
                    'GITHUB_TOKEN': codebuild.BuildEnvironmentVariable(
                        value=github_token.secret_arn, 
                        type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER
                    )
                }
            ),
            build_spec=codebuild.BuildSpec.from_source_filename('eval/docker/buildspec.yml'),
            role=self.codebuild_role
        )