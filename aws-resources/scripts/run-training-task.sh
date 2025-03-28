#!/bin/bash

# 获取 CloudFormation 输出
CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name TrainingStack --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' --output text)
TASK_DEFINITION=$(aws cloudformation describe-stacks --stack-name TrainingStack --query 'Stacks[0].Outputs[?OutputKey==`TaskDefinitionArn`].OutputValue' --output text)
SUBNET_IDS=$(aws cloudformation describe-stacks --stack-name TrainingStack --query 'Stacks[0].Outputs[?OutputKey==`SubnetIds`].OutputValue' --output text)
SECURITY_GROUP_ID=$(aws cloudformation describe-stacks --stack-name TrainingStack --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroupId`].OutputValue' --output text)

# 运行任务
aws ecs run-task \
  --cluster "$CLUSTER_NAME" \
  --task-definition "$TASK_DEFINITION" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"

# 输出任务 ID
echo "Task started! You can check the logs in CloudWatch Logs under /aws/ecs/training-task" 