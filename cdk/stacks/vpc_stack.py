from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
)
from constructs import Construct

class VpcStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 创建 VPC
        self.vpc = ec2.Vpc(
            self, "EvalVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # 输出 VPC 信息
        CfnOutput(self, "VpcId", 
            value=self.vpc.vpc_id,
            description="VPC ID"
        )
        
        CfnOutput(self, "PublicSubnets", 
            value=",".join([subnet.subnet_id for subnet in self.vpc.public_subnets]),
            description="公共子网 IDs"
        )
