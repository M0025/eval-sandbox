import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';

export class TrainingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 创建 VPC，使用更经济的配置
    const vpc = new ec2.Vpc(this, 'TrainingVPC', {
      maxAzs: 1,  // 只使用一个可用区
      natGateways: 0,  // 不使用 NAT 网关
      subnetConfiguration: [
        {
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        }
      ],
      // 使用较小的 CIDR 范围
      cidr: '10.0.0.0/24',
    });

    // 创建安全组
    const securityGroup = new ec2.SecurityGroup(this, 'TrainingSecurityGroup', {
      vpc: vpc,
      description: 'Security group for training tasks',
      allowAllOutbound: true,  // 允许所有出站流量
    });

    // 创建 ECS 集群
    const cluster = new ecs.Cluster(this, 'TrainingCluster', {
      vpc: vpc,
      clusterName: 'training-cluster',
    });

    // 创建日志组
    const logGroup = new logs.LogGroup(this, 'TrainingLogGroup', {
      logGroupName: '/aws/ecs/training-task',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 创建任务执行角色
    const executionRole = new iam.Role(this, 'TrainingTaskExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });

    // 创建任务角色
    const taskRole = new iam.Role(this, 'TrainingTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });

    // 创建 Fargate 任务定义
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TrainingTaskDefinition', {
      memoryLimitMiB: 512,  // 降低内存限制
      cpu: 256,  // 降低 CPU 限制
      executionRole: executionRole,
      taskRole: taskRole,
    });

    // 添加容器到任务定义
    const container = taskDefinition.addContainer('TrainingContainer', {
      image: ecs.ContainerImage.fromRegistry('python:3.9-slim'),  // 使用官方 Python 镜像
      command: ['python', '-c', 'print("Successfully ran task(asr)")'],  // 直接执行 Python 命令
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'training',
        logGroup: logGroup,
      }),
      environment: {
        PYTHONUNBUFFERED: '1',
      },
    });

    // 创建 S3 存储桶用于存储训练结果
    const resultBucket = new s3.Bucket(this, 'TrainingResultBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // 添加 S3 访问权限到任务角色
    resultBucket.grantReadWrite(taskRole);

    // 输出一些有用的信息
    new cdk.CfnOutput(this, 'ClusterName', {
      value: cluster.clusterName,
      description: 'ECS Cluster Name',
    });

    new cdk.CfnOutput(this, 'TaskDefinitionArn', {
      value: taskDefinition.taskDefinitionArn,
      description: 'Task Definition ARN',
    });

    new cdk.CfnOutput(this, 'ResultBucketName', {
      value: resultBucket.bucketName,
      description: 'S3 Bucket for Training Results',
    });

    // 输出 VPC 信息
    new cdk.CfnOutput(this, 'VpcId', {
      value: vpc.vpcId,
      description: 'VPC ID',
    });

    // 输出子网信息
    new cdk.CfnOutput(this, 'SubnetIds', {
      value: vpc.publicSubnets.map(subnet => subnet.subnetId).join(','),
      description: 'Public Subnet IDs',
    });

    // 输出安全组信息
    new cdk.CfnOutput(this, 'SecurityGroupId', {
      value: securityGroup.securityGroupId,
      description: 'Security Group ID',
    });
  }
} 