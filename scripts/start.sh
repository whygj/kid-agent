#!/bin/bash
# Kid-Agent 启动脚本

set -e

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "           Kid-Agent 启动脚本"
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
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"
echo ""

# 检查 venv
echo "检查虚拟环境..."
if [ -d ".venv" ]; then
    echo "找到虚拟环境 .venv"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo -e "${GREEN}虚拟环境已激活${NC}"
    elif [ -f ".venv/Scripts/activate" ]; then
        # Windows Git Bash
        source .venv/Scripts/activate
        echo -e "${GREEN}虚拟环境已激活${NC}"
    else
        echo -e "${YELLOW}警告: 找不到激活脚本，请手动运行: source .venv/bin/activate${NC}"
    fi
else
    echo -e "${YELLOW}警告: 未找到虚拟环境 .venv${NC}"
    echo "运行 ./scripts/install.sh 安装依赖"
fi
echo ""

# 检查 .env 文件
echo "检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f "config/.env" ]; then
        echo -e "${YELLOW}提示: 使用 config/.env 作为配置文件${NC}"
    else
        echo -e "${RED}错误: 未找到 .env 配置文件${NC}"
        echo "请先运行: ./scripts/install.sh"
        exit 1
    fi
fi

# 检查 API Key
echo "检查 API 配置..."
GLM_KEY=$(grep "^GLM_API_KEY" .env 2>/dev/null | cut -d'=' -f2 | xargs)
DEEPSEEK_KEY=$(grep "^DEEPSEEK_API_KEY" .env 2>/dev/null | cut -d'=' -f2 | xargs)

if [ -z "$GLM_KEY" ] && [ -z "$DEEPSEEK_KEY" ]; then
    echo -e "${RED}错误: 未配置 API 密钥${NC}"
    echo "请在 .env 文件中设置 GLM_API_KEY 或 DEEPSEEK_API_KEY"
    echo ""
    echo "获取 API 密钥:"
    echo "  - GLM: https://open.bigmodel.cn/"
    echo "  - DeepSeek: https://platform.deepseek.com/"
    exit 1
fi

if [ -n "$GLM_KEY" ]; then
    PROVIDER="GLM"
    API_KEY="${GLM_KEY:0:4}...${GLM_KEY: -4}"
else
    PROVIDER="DeepSeek"
    API_KEY="${DEEPSEEK_KEY:0:4}...${DEEPSEEK_KEY: -4}"
fi

echo "API 提供商: $PROVIDER"
echo "API 密钥: $API_KEY"
echo ""

# 创建必要目录
echo "创建必要目录..."
mkdir -p data logs
echo -e "${GREEN}目录创建完成${NC}"
echo ""

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import openai" 2>/dev/null; then
    echo -e "${YELLOW}警告: 依赖未完全安装${NC}"
    echo "运行: pip install -r requirements.txt"
fi
echo ""

# 解析参数
STUDENT_ID=""

for arg in "$@"; do
    case $arg in
        --student=*)
            STUDENT_ID="${arg#*=}"
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --student=ID  指定学生ID"
            echo "  --help, -h    显示帮助信息"
            exit 0
            ;;
    esac
done

# 启动应用
echo "=================================================="
echo -e "${GREEN}正在启动 Kid-Agent...${NC}"
echo "=================================================="
echo ""

if [ -n "$STUDENT_ID" ]; then
    echo "学生ID: $STUDENT_ID"
    python3 -m src.main --student "$STUDENT_ID"
else
    python3 -m src.main
fi
