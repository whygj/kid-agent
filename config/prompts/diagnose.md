# 诊断Prompt模板

## 学生信息

- **学生ID**：{student_id}
- **年级**：{grade}
- **总答题数**：{total_count}
- **整体正确率**：{accuracy:.1%}

## 薄弱知识点

{weak_points_info}

## 分析要求

1. **找出主要薄弱点**：学生最需要补的知识点
2. **分析原因**：为什么会错在这些地方
3. **给出建议**：具体的学习建议和复习顺序
4. **语气**：鼓励性的，不要打击孩子

## 返回格式

请用JSON格式返回：

```json
{
    "summary": "整体分析总结（1-2句话）",
    "recommendations": [
        {
            "priority": 1,
            "point_id": "知识点ID",
            "point_name": "知识点名称",
            "reason": "薄弱原因分析",
            "suggested_action": "具体学习建议"
        }
    ]
}
```

**注意**：
- priority按优先级排序，1最优先
- suggested_action要具体可执行
- 语气要鼓励性