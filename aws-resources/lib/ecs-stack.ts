import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

interface EcsStackProps extends cdk.StackProps {
  ecrRepository: ecr.Repository;
  resultBucket: s3.IBucket;
  vpc: ec2.IVpc;
  taskRole?: iam.IRole;
  executionRole?: iam.IRole;
  logGroupName?: string;
}

export class EcsStack extends cdk.Stack {
  public readonly ecsCluster: ecs.Cluster;
  public readonly taskDefinition: ecs.FargateTaskDefinition;
  public readonly taskRole: iam.IRole;
  public readonly executionRole: iam.IRole;

  constructor(scope: Construct, id: string, props: EcsStackProps) {
    super(scope, id, props);

    // 创建 ECS 集群
    this.ecsCluster = new ecs.Cluster(this, 'EvalCluster', {
      vpc: props.vpc,
      clusterName: 'eval-cluster'
    });

    // 引用已存在的日志组
    const logGroup = logs.LogGroup.fromLogGroupName(
      this,
      'ImportedLogGroup',
      props.logGroupName || '/aws/ecs/eval-cluster'
    );

    // 创建任务定义
    const taskDefinitionProps: ecs.FargateTaskDefinitionProps = {
      cpu: 256, // 0.25 vCPU
      memoryLimitMiB: 512, // 0.5 GB
      taskRole: props.taskRole,
      executionRole: props.executionRole
    };

    // 创建任务定义
    this.taskDefinition = new ecs.FargateTaskDefinition(
      this,
      'EvalTaskDef',
      taskDefinitionProps
    );

    // 添加容器到任务定义
    const container = this.taskDefinition.addContainer('EvalContainer', {
      image: ecs.ContainerImage.fromEcrRepository(
        props.ecrRepository,
        process.env.IMAGE_TAG || 'latest'
      ),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'eval-container',
        logGroup: logGroup
      })
    });

    // 创建 Fargate 服务
    const fargateService = new ecs.FargateService(this, 'EvalService', {
      cluster: this.ecsCluster,
      taskDefinition: this.taskDefinition,
      desiredCount: 0,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC
      },
      securityGroups: [
        new ec2.SecurityGroup(this, 'EcsSecurityGroup', {
          vpc: props.vpc,
          description: 'Security group for ECS service in public subnet',
          allowAllOutbound: true
        })
      ],
      assignPublicIp: true
    });

    // 添加 ECR 拉取权限
    if (this.taskDefinition.taskRole) {
      props.ecrRepository.grantPull(this.taskDefinition.taskRole);
    }
    if (this.taskDefinition.executionRole) {
      props.ecrRepository.grantPull(this.taskDefinition.executionRole);
    }

    // 添加 S3 写入权限
    if (this.taskDefinition.taskRole) {
      props.resultBucket.grantWrite(this.taskDefinition.taskRole);
    }

    // 允许 CodeBuild 调用 ECS 任务
    if (this.taskDefinition.taskRole) {
      this.taskDefinition.taskRole.addToPrincipalPolicy(
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'ecs:RunTask',
            'ecs:StopTask',
            'ecs:DescribeTasks'
          ],
          resources: ['*']
        })
      );
    }

    // 输出重要信息
    new cdk.CfnOutput(this, 'ECSClusterName', {
      value: this.ecsCluster.clusterName
    });

    new cdk.CfnOutput(this, 'TaskDefinitionArn', {
      value: this.taskDefinition.taskDefinitionArn
    });

    if (this.taskDefinition.taskRole) {
      new cdk.CfnOutput(this, 'TaskRoleArn', {
        value: this.taskDefinition.taskRole.roleArn
      });
    }

    if (this.taskDefinition.executionRole) {
      new cdk.CfnOutput(this, 'ExecutionRoleArn', {
        value: this.taskDefinition.executionRole.roleArn
      });
    }

    // 保存供其他 Stack 使用的属性
    this.taskRole = this.taskDefinition.taskRole!;
    this.executionRole = this.taskDefinition.executionRole!;
  }
} 