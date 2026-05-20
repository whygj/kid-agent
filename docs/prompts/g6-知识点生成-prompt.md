你需要为中国小学数学Kid Agent项目创建六年级的完整知识点数据文件。

### 人教版六年级课程目录

#### 六年级上册
1. 分数乘法（分数×整数、分数×分数、倒数的认识）
2. 位置与方向(二)（用方向和距离确定位置）
3. 分数除法（分数÷整数、整数÷分数、分数÷分数）
4. 比（比的意义、比的基本性质、化简比、按比分配）
5. 圆（圆的认识、圆的周长、圆的面积）
6. 百分数(一)（百分数的意义、百分数与分数小数的互化、百分数的应用）
7. 扇形统计图
8. 数学广角─数与形

#### 六年级下册
1. 负数（负数的认识、数轴）
2. 百分数(二)（折扣、成数、税率、利率）
3. 圆柱与圆锥（圆柱的表面积和体积、圆锥的体积）
4. 比例（比例的意义和基本性质、正比例和反比例、比例尺、图形的放大和缩小）
5. 数学广角—鸽巢问题
6. 整理和复习（数与代数、图形与几何、统计与概率、综合与实践）

## 格式要求

创建文件：`/home/ubuntu/projects/kid-agent-local/src/knowledge/math_g6.py`

严格遵循以下格式：

```python
"""6年级数学知识点数据"""

from dataclasses import dataclass
from enum import IntEnum


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    EXPERT = 5


@dataclass
class KnowledgePoint:
    id: str
    name: str
    grade: int  # 6
    subject: str = "数学"
    difficulty: Difficulty = Difficulty.MEDIUM
    prerequisites: list[str] = None
    description: str = ""
    examples: list[str] = None
    common_mistakes: list[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.examples is None:
            self.examples = []
        if self.common_mistakes is None:
            self.common_mistakes = []


GRADE_6_POINTS = [
    # 至少25个知识点
]

ALL_POINTS = GRADE_6_POINTS

def get_point_by_id(point_id): ...
def get_points_by_grade(grade): ...
def get_points_by_difficulty(difficulty): ...
```

- 至少25个知识点
- ID格式：math_g6_001 ~ math_g6_025+
- grade = 6
- prerequisites 引用5年级（math_g5_xxx）和6年级内部的知识点
- 每个 KnowledgePoint 必须有 examples 和 common_mistakes
- description 要详细

直接写文件。
