import platform
import socket
from typing import Dict, List

import docker
import psutil
import uvicorn
from fastapi import FastAPI

app = FastAPI()


# 获取本机IP地址
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


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
    local_ip = get_local_ip()
    client = docker.from_env()

    # 获取所有容器
    containers = client.containers.list()
    apps = []

    # 排除的支持类服务
    exclude_services = {
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

        # 获取端口映射
        ports = container.attrs['NetworkSettings']['Ports']
        http_port = None
        for internal_port, external in ports.items():
            if external and internal_port.startswith('80'):
                http_port = external[0]['HostPort']
                break
            elif external and internal_port.startswith('443'):
                http_port = external[0]['HostPort']
                break

        if http_port:
            apps.append({
                "name": service_name,
                "url": f"http://{local_ip}:{http_port}",
                "status": container.status
            })

    return apps


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
