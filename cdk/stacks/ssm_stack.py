from aws_cdk import (
    Stack,
    aws_ssm as ssm,
    aws_resourcegroups as rg,
    CfnOutput,
    Tags,
)
from constructs import Construct

class SystemsManagerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 cluster_name: str,
                 task_definition_arn: str,
                #  lambda_function_arn: str,
                 ecr_repository_name: str,
                 s3_bucket_name: str,
                 vpc_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建应用程序的资源组
        resource_group = rg.CfnGroup(
            self, "EvalSandboxResourceGroup",
            name="eval-sandbox-resources",
            description="Resources for Eval Sandbox Application",
            resource_query={
                "Type": "TAG_FILTERS_1_0",
                "Query": {
                    "ResourceTypeFilters": [
                        "AWS::ECS::Cluster",
                        "AWS::ECS::TaskDefinition",
                        "AWS::ECR::Repository",
                        "AWS::S3::Bucket",
                        "AWS::EC2::VPC"
                    ],
                    "TagFilters": [
                        {
                            "Key": "Application",
                            "Values": ["EvalSandbox"]
                        }
                    ]
                }
            }
        )

        # 在 Parameter Store 中存储重要配置
        ssm.StringParameter(
            self, "ClusterNameParameter",
            parameter_name="/eval-sandbox/cluster-name",
            string_value=cluster_name,
            description="ECS Cluster Name"
        )

        ssm.StringParameter(
            self, "TaskDefinitionParameter",
            parameter_name="/eval-sandbox/task-definition",
            string_value=task_definition_arn,
            description="ECS Task Definition ARN"
        )

        # ssm.StringParameter(
        #     self, "LambdaTriggerParameter",
        #     parameter_name="/eval-sandbox/lambda-trigger",
        #     string_value=lambda_function_arn,
        #     description="Lambda Function ARN for triggering ECS tasks"
        # )

        ssm.StringParameter(
            self, "EcrRepositoryParameter",
            parameter_name="/eval-sandbox/ecr-repository",
            string_value=ecr_repository_name,
            description="ECR Repository Name"
        )

        ssm.StringParameter(
            self, "S3BucketParameter",
            parameter_name="/eval-sandbox/s3-bucket",
            string_value=s3_bucket_name,
            description="S3 Bucket Name for results"
        )

        ssm.StringParameter(
            self, "VpcIdParameter",
            parameter_name="/eval-sandbox/vpc-id",
            string_value=vpc_id,
            description="VPC ID"
        )

        # 创建运行手册
        ssm.CfnDocument(
            self, "EcsTaskManagement",
            content={
                "schemaVersion": "2.2",
                "description": "Operations for ECS Tasks",
                "parameters": {
                    "ClusterName": {
                        "type": "String",
                        "default": cluster_name,
                        "description": "ECS Cluster Name"
                    }
                },
                "mainSteps": [
                    {
                        "action": "aws:runShellScript",
                        "name": "ListRunningTasks",
                        "inputs": {
                            "runCommand": [
                                "aws ecs list-tasks --cluster {{ClusterName}}"
                            ]
                        }
                    },
                    {
                        "action": "aws:runShellScript",
                        "name": "GetCloudWatchLogs",
                        "inputs": {
                            "runCommand": [
                                "aws logs get-log-events --log-group-name /aws/ecs/eval-container --log-stream-name $(aws logs describe-log-streams --log-group-name /aws/ecs/eval-container --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text) --limit 100"
                            ]
                        }
                    }
                ]
            },
            document_type="Command",
            name="EvalSandbox-EcsTaskManagement"
        )

        # 输出资源组 ARN
        CfnOutput(
            self, "ResourceGroupArn",
            value=f"arn:aws:resource-groups:{self.region}:{self.account}:group/eval-sandbox-resources"
        ) 