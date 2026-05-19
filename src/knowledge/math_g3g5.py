"""3-5年级数学知识点数据"""

from dataclasses import dataclass
from enum import IntEnum


class Difficulty(IntEnum):
    """难度等级"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    EXPERT = 5


@dataclass
class KnowledgePoint:
    """知识点数据结构"""
    id: str
    name: str
    grade: int  # 3, 4, 5
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


# 三年级知识点
GRADE_3_POINTS = [
    KnowledgePoint(
        id="math_g3_001",
        name="乘法口诀",
        grade=3,
        difficulty=Difficulty.EASY,
        description="掌握1-9的乘法口诀，能快速计算乘法",
        examples=["7×8=56", "9×6=54", "8×5=40"],
        common_mistakes=["混淆口诀（如三九二十八）", "忘记进位"],
    ),
    KnowledgePoint(
        id="math_g3_002",
        name="一位数乘两位数",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g3_001"],
        description="掌握一位数乘两位数的竖式计算方法",
        examples=["23×4=92", "45×3=135"],
        common_mistakes=["忘记进位", "对齐错误"],
    ),
    KnowledgePoint(
        id="math_g3_003",
        name="除法基础",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g3_001"],
        description="理解除法的意义，掌握简单除法计算",
        examples=["12÷4=3", "18÷2=9"],
        common_mistakes=["商的位置写错", "余数大于除数"],
    ),
    KnowledgePoint(
        id="math_g3_004",
        name="分数初步认识",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        description="认识简单的分数（分子、分母、分数线）",
        examples=["1/2, 1/3, 1/4"],
        common_mistakes=["分子分母混淆", "分母越小分数越大"],
    ),
    KnowledgePoint(
        id="math_g3_005",
        name="长方形和正方形的周长",
        grade=3,
        difficulty=Difficulty.EASY,
        description="计算长方形和正方形的周长",
        examples=["长方形周长=(长+宽)×2", "正方形周长=边长×4"],
        common_mistakes=["忘记乘2", "单位混淆"],
    ),
    KnowledgePoint(
        id="math_g3_006",
        name="面积初步认识",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        description="认识面积单位，计算长方形和正方形的面积",
        examples=["面积=长×宽"],
        common_mistakes=["周长和面积混淆", "单位换算错误"],
    ),
]

# 四年级知识点
GRADE_4_POINTS = [
    KnowledgePoint(
        id="math_g4_001",
        name="多位数乘法",
        grade=4,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g3_002"],
        description="掌握两位数乘两位数的计算方法",
        examples=["23×45=1035", "67×32=2144"],
        common_mistakes=["进位错误", "中间0的处理"],
    ),
    KnowledgePoint(
        id="math_g4_002",
        name="多位数除法",
        grade=4,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g3_003"],
        description="掌握三位数除以一位数的竖式计算",
        examples=["456÷4=114", "876÷3=292"],
        common_mistakes=["商的位置错误", "不够除时补0"],
    ),
    KnowledgePoint(
        id="math_g4_003",
        name="运算律",
        grade=4,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g3_001"],
        description="掌握加法交换律、结合律、乘法分配律",
        examples=["a+b=b+a", "a×(b+c)=a×b+a×c"],
        common_mistakes=["混淆乘法分配律", "符号错误"],
    ),
    KnowledgePoint(
        id="math_g4_004",
        name="小数的初步认识",
        grade=4,
        difficulty=Difficulty.MEDIUM,
        description="认识小数，掌握小数的读写方法",
        examples=["3.14, 0.5, 12.5"],
        common_mistakes=["小数点位置", "读法错误"],
    ),
    KnowledgePoint(
        id="math_g4_005",
        name="角的度量",
        grade=4,
        difficulty=Difficulty.MEDIUM,
        description="认识角，使用量角器测量角度",
        examples=["锐角、直角、钝角"],
        common_mistakes=["量角器使用错误", "内外圈刻度混淆"],
    ),
    KnowledgePoint(
        id="math_g4_006",
        name="条形统计图",
        grade=4,
        difficulty=Difficulty.EASY,
        description="会看会画简单的条形统计图",
        examples=["各班级人数统计"],
        common_mistakes=["刻度不均匀", "单位标注遗漏"],
    ),
]

# 五年级知识点
GRADE_5_POINTS = [
    KnowledgePoint(
        id="math_g5_001",
        name="小数四则运算",
        grade=5,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g4_004"],
        description="掌握小数的加减乘除运算",
        examples=["3.5+2.8=6.3", "1.2×0.5=0.6"],
        common_mistakes=["小数点对齐错误", "乘积的小数位数"],
    ),
    KnowledgePoint(
        id="math_g5_002",
        name="分数加减法",
        grade=5,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g3_004"],
        description="掌握同分母和异分母分数的加减法",
        examples=["1/3+1/3=2/3", "1/2+1/4=3/4"],
        common_mistakes=["通分错误", "忘记约分"],
    ),
    KnowledgePoint(
        id="math_g5_003",
        name="简易方程",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        description="认识方程，会解简单的一元一次方程",
        examples=["x+5=12", "2x=10"],
        common_mistakes=["等号两边运算不一致", "未知数处理错误"],
    ),
    KnowledgePoint(
        id="math_g5_004",
        name="长方体和正方体",
        grade=5,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g3_006"],
        description="认识长方体和正方体的特征，计算表面积和体积",
        examples=["表面积公式, 体积公式"],
        common_mistakes=["表面积和体积混淆", "单位换算"],
    ),
    KnowledgePoint(
        id="math_g5_005",
        name="折线统计图",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g4_006"],
        description="会看会画折线统计图，分析数据变化趋势",
        examples=["温度变化统计"],
        common_mistakes=["点位置错误", "连线错误"],
    ),
    KnowledgePoint(
        id="math_g5_006",
        name="因数和倍数",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        description="理解因数和倍数的概念，找出一个数的因数和倍数",
        examples=["2和4是8的因数", "8是2和4的倍数"],
        common_mistakes=["混淆因数和倍数", "1和本身"],
    ),
]

# 所有知识点
ALL_POINTS = GRADE_3_POINTS + GRADE_4_POINTS + GRADE_5_POINTS


def get_point_by_id(point_id: str) -> KnowledgePoint | None:
    """根据ID获取知识点"""
    for point in ALL_POINTS:
        if point.id == point_id:
            return point
    return None


def get_points_by_grade(grade: int) -> list[KnowledgePoint]:
    """获取指定年级的所有知识点"""
    return [p for p in ALL_POINTS if p.grade == grade]


def get_points_by_difficulty(difficulty: Difficulty) -> list[KnowledgePoint]:
    """获取指定难度的知识点"""
    return [p for p in ALL_POINTS if p.difficulty == difficulty]