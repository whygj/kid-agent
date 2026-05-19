"""Kid Agent - 命令行入口"""

import asyncio
import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.agent.tutor import get_tutor_agent


async def cli_mode(student_id: str):
    """CLI模式运行"""
    console = Console()

    # 显示欢迎界面
    welcome = Text.assemble(
        ("Kid Agent", "bold blue"),
        (" — 小学数学教学助手", "white"),
    )
    console.print(Panel(welcome, border_style="blue"))
    console.print()

    # 初始化Agent
    console.print("正在初始化教学Agent...", style="dim")
    agent = await get_tutor_agent()

    # 开始会话
    console.print()
    greeting = await agent.start_session(student_id)
    console.print(greeting)
    console.print()

    # 对话循环
    while True:
        try:
            # 获取用户输入
            user_input = Prompt.ask(
                "[bold green]你[/bold green]",
                console=console,
            ).strip()

            if not user_input:
                continue

            # 退出命令
            if user_input.lower() in ["exit", "quit", "退出", "拜拜"]:
                console.print("👋 再见！明天见~")
                break

            # 发送消息
            console.print()
            response = await agent.chat(student_id, user_input)

            # 显示回复
            console.print(response)
            console.print()

        except KeyboardInterrupt:
            console.print("\n👋 再见！明天见~")
            break
        except EOFError:
            console.print("\n👋 再见！明天见~")
            break
        except Exception as e:
            console.print(f"出错了: {e}", style="red")
            console.print('输入"exit"退出，或者继续对话~')


async def api_mode():
    """API模式运行（Phase 2）"""
    console = Console()
    console.print("API模式尚未实现，敬请期待！🚧", style="yellow")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Kid Agent - 小学数学教学助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="运行模式: cli(命令行) 或 api(服务)",
    )

    parser.add_argument(
        "--student",
        type=str,
        default="default_student",
        help="学生ID",
    )

    args = parser.parse_args()

    if args.mode == "cli":
        asyncio.run(cli_mode(args.student))
    else:
        asyncio.run(api_mode())


if __name__ == "__main__":
    main()