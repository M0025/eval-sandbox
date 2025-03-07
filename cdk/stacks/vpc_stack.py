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
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
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
        
        CfnOutput(self, "PrivateSubnets", 
            value=",".join([subnet.subnet_id for subnet in self.vpc.private_subnets]),
            description="私有子网 IDs"
        ) 