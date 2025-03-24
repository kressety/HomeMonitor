import platform
from typing import Dict, List

import docker
import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 你想要的固定IP地址
HOST_IP = "192.168.31.70"


@app.get("/system-info")
async def get_system_info() -> Dict:
    """获取系统负载和参数"""
    return {
        "cpu": {
            "count": psutil.cpu_count(),
            "usage_percent": psutil.cpu_percent(interval=1),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
        },
        "memory": {
            "total": psutil.virtual_memory().total / (1024 ** 3),  # GB
            "used": psutil.virtual_memory().used / (1024 ** 3),  # GB
            "free": psutil.virtual_memory().free / (1024 ** 3),  # GB
            "percent": psutil.virtual_memory().percent
        },
        "system": {
            "os": platform.system(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "uptime": psutil.boot_time()
        },
        "disk": {
            "total": psutil.disk_usage('/').total / (1024 ** 3),  # GB
            "used": psutil.disk_usage('/').used / (1024 ** 3),  # GB
            "free": psutil.disk_usage('/').free / (1024 ** 3),  # GB
            "percent": psutil.disk_usage('/').percent
        }
    }


@app.get("/compose-apps")
async def get_compose_apps() -> List[Dict]:
    """获取Docker Compose运行的应用列表及其HTTP地址"""
    client = docker.from_env()

    # 获取所有容器
    containers = client.containers.list()
    apps = []

    # 排除的支持类服务
    exclude_services = {
        'home-monitor',
        'nginx',
        'redis',
        'postgres',
        'watchtower',
        'tika',
        'hassio_multicast',
        'hassio_observer',
        'hassio_audio',
        'hassio_dns',
        'hassio_cli',
        'hassio_supervisor'
    }

    for container in containers:
        service_name = container.labels.get('com.docker.compose.service')
        if not service_name or service_name in exclude_services:
            continue

        # 获取所有端口映射
        ports = container.attrs['NetworkSettings']['Ports']
        exposed_port = None
        for internal_port, external in ports.items():
            # 检查是否有外部端口映射
            if external and len(external) > 0:
                exposed_port = external[0]['HostPort']
                # 如果是80或443开头，使用http或https协议，否则也记录下来
                protocol = "http"
                if internal_port.startswith('443'):
                    protocol = "https"
                apps.append({
                    "name": service_name,
                    "url": f"{protocol}://{HOST_IP}:{exposed_port}",
                    "status": container.status,
                    "internal_port": internal_port.split('/')[0]  # 添加内部端口信息用于调试
                })
                break  # 找到第一个映射端口后跳出

    return apps


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
