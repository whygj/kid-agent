#!/usr/bin/env python3
"""习题数据生成脚本

为每个知识点生成3-5道练习题。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import uuid
from datetime import datetime

from src.config.settings import get_config
from src.knowledge.db import get_db
from src.knowledge.crud import KnowledgeCRUD
from openai import AsyncOpenAI


async def generate_exercises_for_concept(
    client: AsyncOpenAI,
    concept_id: str,
    concept_name: str,
    definition: str,
    grade: int
) -> list[dict]:
    """为单个知识点生成习题"""

    prompt = f"""你是一个小学数学老师。请为以下知识点生成3-5道练习题。

知识点：{concept_name}
定义：{definition}
年级：{grade}

要求：
1. 题目类型多样：选择题、填空题、计算题、应用题
2. 难度适中，适合该年级学生
3. 选择题需要提供4个选项（A/B/C/D），标明正确答案
4. 每题需要简要解析

请以JSON格式输出，格式如下：
{{
    "exercises": [
        {{
            "stem": "题目文本",
            "type": "choice|fill|solve|apply",
            "answer": "答案",
            "analysis": "解析",
            "difficulty": 1-5,
            "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}}
        }}
    ]
}}"""

    try:
        config = get_config()
        response = await client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "你是小学数学老师，擅长编写适合儿童的练习题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        content = response.choices[0].message.content

        # 提取JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content)
        return data.get("exercises", [])

    except Exception as e:
        print(f"  [ERROR] 生成失败: {e}")
        return []


async def generate_all_exercises(limit: int = None):
    """为所有知识点生成习题"""

    print("=" * 60)
    print("习题数据生成")
    print("=" * 60)

    config = get_config()
    client = AsyncOpenAI(
        api_key=config.zhipu_api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4"
    )

    db = get_db()
    crud = KnowledgeCRUD(db)

    # 获取所有知识点
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, definition,
               (SELECT MAX(grade) FROM books b
                JOIN sections s ON b.id = s.book_id
                WHERE s.id = (SELECT section_id FROM concepts WHERE concepts.id = concepts.id LIMIT 1)) as grade
        FROM concepts
        ORDER BY id
    """)

    concepts = cursor.fetchall()
    print(f"\n找到 {len(concepts)} 个知识点")

    if limit:
        concepts = concepts[:limit]
        print(f"限制处理前 {limit} 个知识点")

    total_exercises = 0
    failed = 0

    for idx, concept in enumerate(concepts, 1):
        concept_id, name, definition, grade = concept

        print(f"\n[{idx}/{len(concepts)}] 生成习题: {name}")

        # 检查是否已有习题
        cursor.execute(
            "SELECT COUNT(*) FROM relation_tests_concept WHERE concept_id = ?",
            (concept_id,)
        )
        existing = cursor.fetchone()[0]

        if existing > 0:
            print(f"  跳过（已有{existing}道题）")
            continue

        # 生成习题
        exercises = await generate_exercises_for_concept(
            client, concept_id, name, definition or "", grade or 3
        )

        if not exercises:
            print(f"  [FAILED] 未生成习题")
            failed += 1
            continue

        # 保存习题
        for ex in exercises:
            ex_id = str(uuid.uuid4())

            options_json = None
            if ex.get("type") == "choice" and ex.get("options"):
                options_json = json.dumps(ex["options"], ensure_ascii=False)

            cursor.execute("""
                INSERT INTO exercises (id, stem, answer, analysis, difficulty, type, options, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ex_id,
                ex.get("stem", ""),
                ex.get("answer", ""),
                ex.get("analysis", ""),
                ex.get("difficulty", 2),
                ex.get("type", "solve"),
                options_json,
                "AI生成"
            ))

            # 关联知识点
            cursor.execute("""
                INSERT INTO relation_tests_concept (exercise_id, concept_id, weight)
                VALUES (?, ?, ?)
            """, (ex_id, concept_id, 1.0))

        conn.commit()
        total_exercises += len(exercises)
        print(f"  生成 {len(exercises)} 道题")

        # 避免API限流
        if idx % 5 == 0:
            await asyncio.sleep(1)

    print("\n" + "=" * 60)
    print(f"完成！共生成 {total_exercises} 道习题")
    if failed > 0:
        print(f"失败: {failed} 个知识点")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成习题数据")
    parser.add_argument("--limit", type=int, help="限制处理的知识点数量")
    args = parser.parse_args()

    asyncio.run(generate_all_exercises(limit=args.limit))