# 已生成的知识点数据文件说明
# 更新: 2026-05-20

## 文件列表（src/knowledge/）

这些是Claude Code根据人教版目录生成的数学知识点数据文件，作为种子数据。

| 文件 | 年级 | 知识点数 | 大小 |
|------|------|---------|------|
| math_g1g2.py | 一年级+二年级 | ~40+ | 45KB |
| math_g3g5_v2.py | 三年级+四年级+五年级 | ~75+ | 80KB |
| math_g6.py | 六年级 | 31 | 38KB |
| math_g7.py | 七年级 | 44 | 56KB |
| math_g8g9.py | 八年级+九年级 | ~50+ | 68KB |

## 重要说明

这些文件是旧格式（Python KnowledgePoint dataclass），按照新的知识库框架设计
（KNOWLEDGE-BASE-DESIGN.md），需要迁移到SQLite数据库。

迁移方法：
1. 建好SQLite表（按schema.sql）
2. 写一个迁移脚本，遍历这些文件中的ALL_POINTS
3. 每个KnowledgePoint转为concepts表的一行记录
4. prerequisites列表转为relation_prerequisite表的边

## 注意

这些只覆盖了数学一个学科，1-9年级。还缺：
- 高中（10-12年级）数学
- 语文（1-12年级）
- 英语（3-12年级）
- 物理（8-12年级）
- 化学（9-12年级）
- 生物（7-12年级）
- 历史、地理、政治等

## 最快获得大量知识点的方式

K12-KGraph数据集（北大开源）已有人教版6500+概念：
```python
from datasets import load_dataset
ds = load_dataset("lhpku20010120/K12-KGraph")
```
可以直接导入SQLite，比手工生成快100倍。
