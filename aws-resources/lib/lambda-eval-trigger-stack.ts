import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class LambdaEvalTriggerStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // 创建 DynamoDB 表
        const stateTable = new dynamodb.Table(this, 'EvalTriggerState', {
            partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: cdk.RemovalPolicy.DESTROY, // 开发环境使用，生产环境应该改为 RETAIN
            timeToLiveAttribute: 'ttl'
        });

        // 创建 Lambda 函数
        const evalTriggerLambda = new lambda.Function(this, 'EvalTriggerFunction', {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'eval_trigger.handler',
            code: lambda.Code.fromAsset('lambda'),
            timeout: cdk.Duration.seconds(30),
            environment: {
                'DYNAMODB_TABLE': stateTable.tableName
            }
        });

        // 添加必要的 IAM 权限
        evalTriggerLambda.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'logs:GetLogEvents',
                'logs:FilterLogEvents'
            ],
            resources: ['arn:aws:logs:*:*:*']
        }));

        // 添加 ECS 权限
        evalTriggerLambda.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'ecs:UpdateService'
            ],
            resources: ['arn:aws:ecs:*:*:service/eval-cluster/EvalService']
        }));

        // 添加 DynamoDB 权限
        stateTable.grantReadWriteData(evalTriggerLambda);

        // 创建 CloudWatch 事件规则
        new events.Rule(this, 'EvalTriggerRule', {
            eventPattern: {
                source: ['aws.logs'],
                detailType: ['CloudWatch Logs Log Group'],
                detail: {
                    logGroupName: ['/aws/ecs/training-task']
                }
            },
            targets: [new targets.LambdaFunction(evalTriggerLambda)]
        });

        // 输出 DynamoDB 表名
        new cdk.CfnOutput(this, 'StateTableName', {
            value: stateTable.tableName,
            description: 'DynamoDB table name for state management'
        });
    }
} 