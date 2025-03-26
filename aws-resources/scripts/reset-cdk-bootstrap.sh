#!/bin/bash

set -e

ACCOUNT_ID=783764605802
REGION=ap-northeast-1
BUCKET_NAME="cdk-hnb659fds-assets-$ACCOUNT_ID-$REGION"
STACK_NAME="CDKToolkit"

echo "🚨 Cleaning up CDK bootstrap resources in account: $ACCOUNT_ID, region: $REGION..."

# Step 1: Delete bootstrap S3 bucket
echo "🧹 Deleting S3 bucket: $BUCKET_NAME"
aws s3 rm s3://$BUCKET_NAME --recursive || true
aws s3 rb s3://$BUCKET_NAME --force || true

# Step 2: Detach policies and delete IAM roles
for roleType in deploy-role file-publishing-role image-publishing-role lookup-role; do
  ROLE_NAME="cdk-hnb659fds-${roleType}-${ACCOUNT_ID}-${REGION}"
  echo "🔍 Cleaning up IAM Role: $ROLE_NAME"

  # Detach managed policies
  attached_policies=$(aws iam list-attached-role-policies --role-name $ROLE_NAME --query 'AttachedPolicies[].PolicyArn' --output text)
  for policy_arn in $attached_policies; do
    echo "🔸 Detaching managed policy: $policy_arn"
    aws iam detach-role-policy --role-name $ROLE_NAME --policy-arn $policy_arn
  done

  # Delete inline policies
  inline_policies=$(aws iam list-role-policies --role-name $ROLE_NAME --query 'PolicyNames' --output text)
  for policy_name in $inline_policies; do
    echo "🔸 Deleting inline policy: $policy_name"
    aws iam delete-role-policy --role-name $ROLE_NAME --policy-name $policy_name
  done

  # Delete the role
  echo "🧨 Deleting IAM Role: $ROLE_NAME"
  aws iam delete-role --role-name $ROLE_NAME || true
done

# Step 3: Delete the CloudFormation stack
echo "🧯 Deleting CloudFormation stack: $STACK_NAME"
aws cloudformation delete-stack --stack-name $STACK_NAME || true

echo "✅ Cleanup completed!"