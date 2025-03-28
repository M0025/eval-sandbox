#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AwsResourcesStack } from '../lib/aws-resources-stack';
import { TrainingStack } from '../lib/training-stack';
import { GithubOidcRoleStack } from '../lib/github-oidc-role-stack';
import { LambdaEvalTriggerStack } from '../lib/lambda-eval-trigger-stack';

const app = new cdk.App();
new AwsResourcesStack(app, 'AwsResourcesStack', {
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */

  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },

  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
});
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