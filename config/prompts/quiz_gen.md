# 出题Prompt模板

## 知识点信息

- **知识点名称**：{name}
- **年级**：{grade}
- **难度**：{difficulty}（1-5级，1最简单，5最难）
- **知识点描述**：{description}

## 出题要求

1. **题型多样**：可以是填空题、选择题、计算题、应用题
2. **生活化**：题目要贴近生活，有趣味性
3. **难度匹配**：严格按照指定难度出题
4. **避免重复**：不要和学生最近做过的题目重复

## 返回格式

请用JSON格式返回：

```json
{
    "question_type": "free | choice | calculation | application",
    "question": "题目内容（选择题要包含选项）",
    "options": ["选项A", "选项B", "选项C", "选项D"],
    "answer": "标准答案",
    "explanation": "答案解释（给老师看的）"
}
```

**注意**：
- question_type如果是choice，必须提供options
- answer要准确简洁
- explanation要说明解题思路