import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';

export class LambdaEvalTriggerStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // 创建 Lambda 函数
        const evalTriggerLambda = new lambda.Function(this, 'EvalTriggerFunction', {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'eval_trigger.handler',
            code: lambda.Code.fromAsset('lambda'),
            timeout: cdk.Duration.seconds(30)
        });

        // 添加必要的 IAM 权限
        evalTriggerLambda.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'logs:GetLogEvents',
                'logs:FilterLogEvents',
                'lambda:InvokeFunction'
            ],
            resources: ['*'] // 在生产环境中应该限制为特定的资源
        }));

        // 创建 CloudWatch 事件规则
        const rule = new events.Rule(this, 'EvalTriggerRule', {
            eventPattern: {
                source: ['aws.logs'],
                detailType: ['CloudWatch Logs Log Group'],
                detail: {
                    logGroupName: ['/ecs/asr-evaluation-dev']
                }
            },
            targets: [new targets.LambdaFunction(evalTriggerLambda)]
        });
    }
} 