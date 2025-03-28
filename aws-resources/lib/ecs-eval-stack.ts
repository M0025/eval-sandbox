import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class EcsEvalStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // 使用 EvalSandboxVPC
        const vpc = ec2.Vpc.fromLookup(this, 'EvalSandboxVPC', {
            vpcId: 'vpc-0bbcf1a5778475522'
        });

        // 使用现有的 ECS 集群
        const cluster = ecs.Cluster.fromClusterAttributes(this, 'ExistingCluster', {
            clusterName: 'eval-cluster',
            vpc,
            securityGroups: []
        });

        // 创建任务执行角色
        const taskExecutionRole = new iam.Role(this, 'EvalTaskExecutionRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });

        // 添加 ECR 拉取权限
        taskExecutionRole.addManagedPolicy(
            iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
        );

        // 创建任务角色
        const taskRole = new iam.Role(this, 'EvalTaskRole', {
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });

        // 引用已存在的日志组
        const logGroup = logs.LogGroup.fromLogGroupName(this, 'EvalLogGroup', '/ecs/asr-evaluation-dev');

        // 添加 CloudWatch Logs 权限
        taskRole.addToPolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'logs:CreateLogStream',
                'logs:PutLogEvents'
            ],
            resources: [logGroup.logGroupArn]
        }));

        // 创建任务定义
        const taskDefinition = new ecs.FargateTaskDefinition(this, 'EvalTaskDefinition', {
            memoryLimitMiB: 512,
            cpu: 256,
            taskRole,
            executionRole: taskExecutionRole,
            family: 'eval-task'
        });

        // 从指定的 ECR 获取镜像
        const repository = ecr.Repository.fromRepositoryName(
            this,
            'EvalRepository',
            'eval-sandbox-ecr'
        );

        // 添加容器到任务定义
        const container = taskDefinition.addContainer('EvalContainer', {
            image: ecs.ContainerImage.fromEcrRepository(repository, '89bbad6'),
            logging: ecs.LogDrivers.awsLogs({
                streamPrefix: 'eval',
                logGroup
            }),
            environment: {
                'AWS_REGION': this.region
            }
        });

        // 创建安全组
        const securityGroup = new ec2.SecurityGroup(this, 'EvalSecurityGroup', {
            vpc,
            description: 'Security group for ECS eval tasks',
            allowAllOutbound: true
        });

        // 创建 Fargate 服务
        const service = new ecs.FargateService(this, 'EvalService', {
            cluster,
            taskDefinition,
            desiredCount: 0,
            securityGroups: [securityGroup],
            assignPublicIp: true,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PUBLIC
            }
        });

        // 输出服务 URL
        new cdk.CfnOutput(this, 'ServiceUrl', {
            value: service.serviceName,
            description: 'ECS Service Name'
        });
    }
} 