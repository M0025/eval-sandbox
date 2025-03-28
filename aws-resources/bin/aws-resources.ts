#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { TrainingStack } from '../lib/training-stack';
import { GithubOidcRoleStack } from '../lib/github-oidc-role-stack';
import { LambdaEvalTriggerStack } from '../lib/lambda-eval-trigger-stack';
import { EcsEvalStack } from '../lib/ecs-eval-stack';

const app = new cdk.App();

//创建训练stack 不要拉到生产上去 自己做测试
new TrainingStack(app, 'TrainingStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
});

// 这上边都不要拉到生产上去

new GithubOidcRoleStack(app, 'GithubOidcRoleStack');
// 创建评估触发 Lambda Stack
const lambdaEvalTriggerStack = new LambdaEvalTriggerStack(app, 'LambdaEvalTriggerStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

// 创建 ECS 评估 Stack
new EcsEvalStack(app, 'EcsEvalStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});