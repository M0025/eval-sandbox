import * as cdk from "aws-cdk-lib";
import { aws_iam as iam } from "aws-cdk-lib";
import type { Construct } from "constructs";

// 测试环境:
const GITHUB_ORG = "M0025";
const REPOSITORY_NAME = "eval-sandbox";

export class GithubOidcRoleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const conditions: iam.Conditions = {
      StringEquals: {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      },
      StringLike: {
        // 👇 限定只允许 main 分支
        "token.actions.githubusercontent.com:sub": `repo:${GITHUB_ORG}/${REPOSITORY_NAME}:ref:refs/heads/main`,
      },
    };

    const provider = new iam.OpenIdConnectProvider(this, "GithubActionsOidcProvider", {
      url: "https://token.actions.githubusercontent.com",
      clientIds: ["sts.amazonaws.com"],
      thumbprints: ["ffffffffffffffffffffffffffffffffffffffff"],
    });

    const role = new iam.Role(this, "GitHubActionsOidcTestRole", {
      roleName: "github-oidc-role-test",
      assumedBy: new iam.WebIdentityPrincipal(
        provider.openIdConnectProviderArn,
        conditions
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("AdministratorAccess"),
      ],
      description: "Test role for GitHub Actions OIDC (M0025/eval-sandbox)",
      maxSessionDuration: cdk.Duration.hours(1),
    });

    new cdk.CfnOutput(this, "GithubOidcRoleArn", {
      value: role.roleArn,
      description: "IAM Role ARN for GitHub OIDC (test)",
      exportName: "GithubOidcTestRoleArn",
    });
  }
}