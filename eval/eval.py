#!/usr/bin/env python3
import os
import time
import datetime
import json
import random
import socket
import platform
import uuid

def run_task():
    """运行示例任务，显示系统信息并生成随机数据"""
    print("=" * 50)
    print("Python任务开始执行")
    print("=" * 50)
    
    # 获取系统信息
    system_info = {
        "当前时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "主机名": socket.gethostname(),
        "本地IP": socket.gethostbyname(socket.gethostname()),
        "Python版本": platform.python_version(),
        "系统平台": platform.platform(),
        "处理器架构": platform.machine(),
        "进程ID": os.getpid(),
        "任务ID": str(uuid.uuid4())
    }
    
    # 输出系统信息
    print("\n系统信息:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # 模拟任务处理
    print("\n开始处理任务...")
    total_steps = 5
    for step in range(1, total_steps + 1):
        # 生成随机数据
        random_data = {
            "步骤": step,
            "随机整数": random.randint(1, 1000),
            "随机浮点数": random.uniform(0, 100),
            "随机布尔值": random.choice([True, False])
        }
        
        # 输出数据
        print(f"\n步骤 {step}/{total_steps} 的数据:")
        print(json.dumps(random_data, indent=2, ensure_ascii=False))
        
        # 模拟处理时间
        time.sleep(1)
    
    # 输出总结
    print("\n" + "=" * 50)
    print("任务完成！")
    print("数据生成时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)

if __name__ == "__main__":
    run_task()