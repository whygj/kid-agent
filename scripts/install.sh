#!/bin/bash
# Kid-Agent 安装脚本

set -e

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "           Kid-Agent 安装脚本"
echo "=================================================="
echo ""

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo "检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3 命令${NC}"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

echo "Python 版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}错误: Python 版本过低，需要 3.8 或更高版本${NC}"
    exit 1
fi

echo -e "${GREEN}Python 版本符合要求${NC}"
echo ""

# 检查 venv
echo "检查虚拟环境..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}警告: 虚拟环境 .venv 已存在${NC}"
    read -p "是否删除并重新创建? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有虚拟环境..."
        rm -rf .venv
    else
        echo "跳过虚拟环境创建"
        source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
    fi
fi

# 创建 venv
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"

    # 激活虚拟环境
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
    echo -e "${GREEN}虚拟环境已激活${NC}"
    echo ""
fi

# 确保 pip 是最新版本
echo "升级 pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}pip 已更新${NC}"
echo ""

# 安装依赖
echo "安装依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}依赖安装完成${NC}"
else
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi
echo ""

# 创建必要目录
echo "创建目录结构..."
mkdir -p data logs config/prompts
echo -e "${GREEN}目录创建完成${NC}"
echo ""

# 检查 .env 文件
echo "检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "从 .env.example 复制配置..."
        cp .env.example .env
        echo -e "${GREEN}配置文件已创建: .env${NC}"
    elif [ -f "config/.env.example" ]; then
        echo "从 config/.env.example 复制配置..."
        cp config/.env.example .env
        echo -e "${GREEN}配置文件已创建: .env${NC}"
    else
        echo -e "${YELLOW}创建默认配置文件 .env${NC}"
        cat > .env << 'EOF'
# Kid-Agent 配置文件

# LLM 提供商 (glm 或 deepseek)
LLM_PROVIDER=glm

# GLM 配置
GLM_API_KEY=your_key_here
GLM_API_BASE=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=glm-4

# DeepSeek 配置
DEEPSEEK_API_KEY=
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# LLM 超时设置（秒）
LLM_TIMEOUT=60

# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# 数据库路径
DB_PATH=data/kid_agent.db
EOF
        echo -e "${GREEN}默认配置文件已创建${NC}"
    fi
else
    echo "配置文件已存在: .env"
fi
echo ""

# 设置权限
echo "设置脚本权限..."
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}权限设置完成${NC}"
echo ""

# 测试导入
echo "测试依赖..."
python3 -c "
import sys
try:
    import openai
    import sqlalchemy
    import aiosqlite
    import dotenv
    import rich
    print('所有依赖导入成功!')
except ImportError as e:
    print(f'导入失败: {e}')
    sys.exit(1)
"
echo ""

# 运行测试
echo "运行测试套件..."
read -p "是否运行测试? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}测试通过${NC}"
    else
        echo -e "${YELLOW}警告: 部分测试失败，请检查配置${NC}"
    fi
else
    echo "跳过测试"
fi
echo ""

# 完成
echo "=================================================="
echo -e "${GREEN}安装完成！${NC}"
echo "=================================================="
echo ""
echo "下一步:"
echo "  1. 编辑 .env 文件，配置你的 API 密钥"
echo "  2. 运行 ./scripts/start.sh 启动应用"
echo ""
echo "获取 API 密钥:"
echo "  - GLM: https://open.bigmodel.cn/"
echo "  - DeepSeek: https://platform.deepseek.com/"
echo ""
