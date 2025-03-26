# Home Monitor

Home Monitor 是一个基于 FastAPI 开发的系统监控工具，可以实时监控系统资源使用情况，包括 CPU、内存、磁盘等指标。

## 功能特点

- 实时监控系统资源使用情况
- 支持 CPU、内存、磁盘等关键指标监控
- 提供 RESTful API 接口
- 支持 Docker 容器化部署
- 支持 AMD64 和 ARM64 架构

## 快速开始

### 使用 Docker 运行

```bash
docker run -d \
  --name home-monitor \
  -p 8000:8000 \
  --restart unless-stopped \
  arnocher/home-monitor
```

### 手动安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/home-monitor.git
cd home-monitor
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app/main.py
```

## 系统要求

- Python 3.12 或更高版本
- Docker（如果使用容器化部署）
