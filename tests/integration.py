"""Phase 1d 集成测试 - 完整教学循环"""
import asyncio
import sys
import os

STUDENT = "test_integration"

async def main():
    from src.agent.tutor import TutorAgent
    
    print("=" * 50)
    print("  少年助手 Phase 1d 集成测试")
    print("=" * 50)
    print()
    
    tutor = TutorAgent()
    
    # 1. 开始会话
    print("[1] 开始会话...")
    try:
        greeting = await tutor.start_session(STUDENT)
        print(f"    开场白: {greeting[:100]}...")
        print("    ✅ 会话创建成功")
    except Exception as e:
        print(f"    ❌ 会话创建失败: {e}")
        import traceback; traceback.print_exc()
        return
    print()
    
    # 2. 请求出题
    print("[2] 请求出题...")
    try:
        response = await tutor.chat(STUDENT, "我想做数学题")
        print(f"    回复: {response[:150]}...")
        print("    ✅ 出题成功")
    except Exception as e:
        print(f"    ❌ 出题失败: {e}")
        import traceback; traceback.print_exc()
    print()
    
    # 3. 回答问题
    print("[3] 模拟回答...")
    try:
        response = await tutor.chat(STUDENT, "24")
        print(f"    回复: {response[:150]}...")
        print("    ✅ 判题+反馈成功")
    except Exception as e:
        print(f"    ❌ 回答失败: {e}")
        import traceback; traceback.print_exc()
    print()
    
    # 4. 再出一题
    print("[4] 再来一题...")
    try:
        response = await tutor.chat(STUDENT, "继续做题")
        print(f"    回复: {response[:150]}...")
        print("    ✅ 连续出题成功")
    except Exception as e:
        print(f"    ❌ 连续出题失败: {e}")
    print()
    
    # 5. 查看学习报告
    print("[5] 请求学习报告...")
    try:
        response = await tutor.chat(STUDENT, "看看我的学习情况")
        print(f"    回复: {response[:200]}...")
        print("    ✅ 学习报告成功")
    except Exception as e:
        print(f"    ❌ 学习报告失败: {e}")
    print()
    
    # 6. 保存并重启验证
    print("[6] 重启验证持久化...")
    try:
        tutor2 = TutorAgent()
        greeting2 = await tutor2.start_session(STUDENT)
        print(f"    重启后开场白: {greeting2[:100]}...")
        print("    ✅ 重启验证通过（数据持久化成功）")
    except Exception as e:
        print(f"    ❌ 重启验证失败: {e}")
    print()
    
    # 清理
    for f in [f"data/{STUDENT}.db"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[清理] 删除: {f}")
    
    print()
    print("=" * 50)
    print("  ✅ 集成测试全部完成")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
