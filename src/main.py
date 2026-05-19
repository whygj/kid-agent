"""Kid Agent - 命令行入口"""

import asyncio
import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.agent.tutor import get_tutor_agent
from src.agent.roster import get_student_roster
from src.memory.store import get_store


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


async def list_students():
    """列出所有学生"""
    console = Console()
    console.print("正在加载学生数据...", style="dim")

    store = await get_store()
    roster = get_student_roster()
    roster._store = store
    roster._graph = None

    # 获取所有学生（暂时返回空列表，需要扩展store.py）
    students = []

    if not students:
        console.print("还没有学生注册呢！先开始学习吧~", style="yellow")
        return

    console.print("📚 学生列表", style="bold blue")
    console.print()

    for i, student in enumerate(students, 1):
        summary_text = roster.format_summary_text(student)
        console.print(Panel(summary_text, title=f"学生 {i}", border_style="blue"))
        console.print()


async def show_report(student_id: str):
    """显示学生学习报告"""
    console = Console()
    console.print("正在生成学习报告...", style="dim")

    store = await get_store()
    roster = get_student_roster()
    roster._store = store

    from src.knowledge.graph import get_graph
    roster._graph = get_graph()

    report = await roster.get_student_report(student_id)

    if not report:
        console.print("没有找到该学生的学习记录", style="red")
        return

    console.print("📊 学习报告", style="bold blue")
    console.print()

    report_text = roster.format_report_text(report)
    console.print(report_text)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Kid Agent - 小学数学教学助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 默认CLI模式
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

    # 列出所有学生
    list_parser = subparsers.add_parser(
        "list-students",
        help="列出所有学生"
    )

    # 查看学习报告
    report_parser = subparsers.add_parser(
        "report",
        help="查看学生学习报告"
    )
    report_parser.add_argument(
        "student_id",
        type=str,
        help="学生ID",
    )

    args = parser.parse_args()

    if args.command == "list-students":
        asyncio.run(list_students())
    elif args.command == "report":
        asyncio.run(show_report(args.student_id))
    elif args.mode == "cli":
        asyncio.run(cli_mode(args.student))
    else:
        asyncio.run(api_mode())


if __name__ == "__main__":
    main()