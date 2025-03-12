import torch
import torch.nn as nn
import boto3
import os
# 一段没什么用只是为了测试的代码

# 1. 定义最简单的 PyTorch 网络
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )

    def forward(self, x):
        return self.fc(x)

# 2. 初始化模型并随机初始化
model = SimpleNN()
model.apply(lambda m: m.reset_parameters() if hasattr(m, 'reset_parameters') else None)

# 3. 保存模型到本地
model_path = "/tmp/random_model.pth"
torch.save(model.state_dict(), model_path)
print("model train success")  # 这条日志会被 CloudWatch 监控

# 4. 上传模型到 S3
s3 = boto3.client('s3')
bucket_name = os.getenv('S3_BUCKET_NAME', 'your-s3-bucket')
s3_key = 'models/random_model.pth'

s3.upload_file(model_path, bucket_name, s3_key)
print(f"Model uploaded to S3: s3://{bucket_name}/{s3_key}")

# 5. 关联到 MLflow（Databricks）
import mlflow
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/random_model_experiment")

with mlflow.start_run():
    mlflow.log_param("model_type", "SimpleNN")
    mlflow.log_artifact(model_path, artifact_path="models")

print("Model tracking completed in MLflow.")