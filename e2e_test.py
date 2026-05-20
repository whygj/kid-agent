#!/usr/bin/env python3
"""kid-agent E2E测试 — 核心教学闭环验证

测试链路：
1. 知识库查询（304知识点）
2. LLM调用（智谱GLM）
3. 教学出题
4. 批改反馈
"""
import asyncio
import sys
import os
import sqlite3
from pathlib import Path

# 确保项目根目录
PROJECT = Path(__file__).parent
sys.path.insert(0, str(PROJECT / "src"))
os.chdir(PROJECT)

# 加载.env
from dotenv import load_dotenv
load_dotenv(PROJECT / ".env")

KB_PATH = PROJECT / "src" / "kid_agent" / "data" / "kid_knowledge" / "knowledge.db"


def test_knowledge_db():
    """测试1: 知识库能不能读"""
    print("\n" + "="*60)
    print("[测试1] 知识库查询")
    print("="*60)
    
    if not KB_PATH.exists():
        print(f"  ✗ 知识库不存在: {KB_PATH}")
        return False
    
    conn = sqlite3.connect(str(KB_PATH))
    conn.row_factory = sqlite3.Row
    
    # 总知识点数
    count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
    print(f"  总知识点: {count}个")
    
    # 3年级知识点
    rows = conn.execute(
        "SELECT c.name, c.importance FROM concepts c "
        "JOIN sections s ON c.section_id = s.id "
        "JOIN books b ON s.book_id = b.id "
        "WHERE b.grade = 3 ORDER BY c.name LIMIT 10"
    ).fetchall()
    print(f"  3年级知识点(前10):")
    for r in rows:
        print(f"    - {r['name']} ({r['importance']})")
    
    # 常见错误
    mistakes = conn.execute("SELECT COUNT(*) FROM common_mistakes").fetchone()[0]
    print(f"  常见错误: {mistakes}条")
    
    # 前置依赖
    prereqs = conn.execute("SELECT COUNT(*) FROM relation_prerequisite").fetchone()[0]
    print(f"  前置依赖: {prereqs}条")
    
    # 查一个具体知识点
    row = conn.execute(
        "SELECT c.*, b.grade FROM concepts c "
        "JOIN sections s ON c.section_id = s.id "
        "JOIN books b ON s.book_id = b.id "
        "WHERE c.name LIKE '%加法%' LIMIT 1"
    ).fetchone()
    if row:
        print(f"  测试查询: {row['name']} ({row['grade']}年级)")
        cm = conn.execute(
            "SELECT mistake, reason FROM common_mistakes WHERE concept_id = ?",
            (row['id'],)
        ).fetchall()
        print(f"    常见错误: {len(cm)}个")
        for m in cm[:3]:
            print(f"      - {m['mistake']} → {m['reason']}")
    
    conn.close()
    print("  ✓ 知识库查询正常")
    return True


async def test_llm_call():
    """测试2: LLM能不能调通"""
    print("\n" + "="*60)
    print("[测试2] LLM调用 (智谱GLM)")
    print("="*60)
    
    try:
        from kid_agent.services.llm import complete
        
        print("  调用GLM-5.1...")
        response = await complete(
            "请用一句话回答：1+1等于几？",
            system_prompt="你是一个数学老师，回答要简洁准确。",
        )
        print(f"  GLM回复: {response}")
        print("  ✓ LLM调用正常")
        return True
    except Exception as e:
        print(f"  ✗ LLM调用失败: {type(e).__name__}: {e}")
        return False


async def test_knowledge_tool():
    """测试3: KidKnowledgeTool完整调用"""
    print("\n" + "="*60)
    print("[测试3] KidKnowledgeTool工具调用")
    print("="*60)
    
    try:
        from kid_agent.tools.kid_knowledge_tool import KidKnowledgeTool
        
        tool = KidKnowledgeTool()
        
        # 按年级查询
        r = await tool.execute(action="by_grade", grade=3)
        print(f"  3年级: {r.content[:80]}...")
        assert r.success
        
        # 搜加法
        r = await tool.execute(action="query", name="加法")
        print(f"  加法查询: {r.content[:80]}...")
        assert r.success
        
        # 前置依赖
        r = await tool.execute(action="prereq_chain", name="加法")
        print(f"  依赖链: {r.content[:80]}...")
        
        # 常见错误
        r = await tool.execute(action="mistakes", name="加法")
        print(f"  常见错误: {r.content[:80]}...")
        
        print("  ✓ KidKnowledgeTool正常")
        return True
    except Exception as e:
        print(f"  ✗ KidKnowledgeTool失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_quiz_generation():
    """测试4: 用LLM生成数学题"""
    print("\n" + "="*60)
    print("[测试4] LLM出题 + 批改")
    print("="*60)
    
    try:
        from kid_agent.services.llm import complete
        
        # 出一道3年级加法题
        print("  生成3年级加法题...")
        quiz_prompt = """你是一个小学数学老师。请出一道3年级的两位数加法题。
要求：
1. 题目要有趣味性
2. 返回格式必须是JSON：{"question": "题目文本", "answer": "正确答案", "type": "choice", "options": ["A选项", "B选项", "C选项", "D选项"]}

只返回JSON，不要其他内容。"""

        quiz_resp = await complete(quiz_prompt, system_prompt="你是数学出题专家。")
        print(f"  LLM出题结果: {quiz_resp[:200]}")
        
        # 批改
        print("\n  模拟批改...")
        grade_prompt = f"""你是数学批改老师。
题目: {quiz_resp}
学生答案: 一个错误答案

请判断对错并给出讲解。返回JSON：{{"is_correct": false, "explanation": "讲解内容"}}
只返回JSON。"""
        
        grade_resp = await complete(grade_prompt, system_prompt="你是批改专家。")
        print(f"  批改结果: {grade_resp[:200]}")
        
        print("  ✓ LLM出题+批改正常")
        return True
    except Exception as e:
        print(f"  ✗ 出题/批改失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n" + "#"*60)
    print("  kid-agent E2E测试 — 核心教学闭环验证")
    print("#"*60)
    
    results = {}
    
    # 测试1: 知识库（同步）
    results["知识库"] = test_knowledge_db()
    
    # 测试2: LLM
    results["LLM调用"] = await test_llm_call()
    
    # 测试3: Knowledge Tool
    results["KnowledgeTool"] = await test_knowledge_tool()
    
    # 测试4: 出题+批改
    results["出题批改"] = await test_llm_quiz_generation()
    
    # 汇总
    print("\n" + "#"*60)
    print("  E2E测试汇总")
    print("#"*60)
    for name, ok in results.items():
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n  🎉 全部通过！kid-agent核心闭环正常！")
    else:
        print("\n  ⚠️ 部分失败，需要排查")
    
    return passed == total


if __name__ == "__main__":
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)
