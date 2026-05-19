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


# 三年级知识点（10个）
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
    KnowledgePoint(
        id="math_g3_007",
        name="时间计算",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        description="认识时、分、秒，会进行简单的时间计算",
        examples=["1小时=60分钟", "从3点到3点半经过30分钟"],
        common_mistakes=["时和分换算错误", "计算经过时间出错"],
    ),
    KnowledgePoint(
        id="math_g3_008",
        name="重量单位",
        grade=3,
        difficulty=Difficulty.MEDIUM,
        description="认识克、千克、吨，会进行单位换算",
        examples=["1千克=1000克", "1吨=1000千克"],
        common_mistakes=["单位大小顺序记错", "换算时少算或多算零"],
    ),
    KnowledgePoint(
        id="math_g3_009",
        name="数据分析",
        grade=3,
        difficulty=Difficulty.EASY,
        description="会收集和整理数据，认识简单的统计表",
        examples=["统计班级同学最喜欢的运动", "制作简单的表格"],
        common_mistakes=["数据统计错误", "不会看表格"],
    ),
    KnowledgePoint(
        id="math_g3_010",
        name="逻辑推理",
        grade=3,
        difficulty=Difficulty.HARD,
        description="掌握简单的逻辑推理方法，解决数学趣题",
        examples=["找规律填数", "简单的排列组合"],
        common_mistakes=["观察不够仔细", "推理逻辑错误"],
    ),
]

# 四年级知识点（10个）
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
    KnowledgePoint(
        id="math_g4_007",
        name="简便计算",
        grade=4,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g4_003"],
        description="运用运算律进行简便计算",
        examples=["25×4=100", "125×8=1000"],
        common_mistakes=["公式记错", "符号处理不当"],
    ),
    KnowledgePoint(
        id="math_g4_008",
        name="平行与垂直",
        grade=4,
        difficulty=Difficulty.EASY,
        description="认识平行线和垂直线，会判断两条直线的位置关系",
        examples=["同一平面内不相交的两条直线平行", "两条直线相交成直角则互相垂直"],
        common_mistakes=["平行和垂直的概念混淆", "判断标准记错"],
    ),
    KnowledgePoint(
        id="math_g4_009",
        name="行程问题",
        grade=4,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g3_001"],
        description="解决简单的行程问题（路程=速度×时间）",
        examples=["速度60千米/小时，行驶2小时，路程是多少？"],
        common_mistakes=["单位不统一", "公式记错"],
    ),
    KnowledgePoint(
        id="math_g4_010",
        name="图形变换",
        grade=4,
        difficulty=Difficulty.MEDIUM,
        description="认识图形的平移、旋转和轴对称",
        examples=["图形向右平移3格", "图形旋转90度"],
        common_mistakes=["平移和旋转混淆", "旋转方向错误"],
    ),
]

# 五年级知识点（10个）
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
        name="分数乘除法",
        grade=5,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g5_002"],
        description="掌握分数的乘法和除法运算",
        examples=["1/2×2/3=1/3", "3/4÷1/2=3/2"],
        common_mistakes=["乘法分子分母直接乘", "除法要乘倒数"],
    ),
    KnowledgePoint(
        id="math_g5_004",
        name="简易方程",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        description="认识方程，会解简单的一元一次方程",
        examples=["x+5=12", "2x=10"],
        common_mistakes=["等号两边运算不一致", "未知数处理错误"],
    ),
    KnowledgePoint(
        id="math_g5_005",
        name="多边形面积",
        grade=5,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g3_006"],
        description="计算三角形、平行四边形、梯形的面积",
        examples=["三角形面积=底×高÷2", "平行四边形面积=底×高"],
        common_mistakes=["忘记除以2", "底和高对应错误"],
    ),
    KnowledgePoint(
        id="math_g5_006",
        name="长方体和正方体",
        grade=5,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g5_005"],
        description="认识长方体和正方体的特征，计算表面积和体积",
        examples=["表面积=(长×宽+长×高+宽×高)×2", "体积=长×宽×高"],
        common_mistakes=["表面积和体积混淆", "单位换算"],
    ),
    KnowledgePoint(
        id="math_g5_007",
        name="因数和倍数",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        description="理解因数和倍数的概念，找出一个数的因数和倍数",
        examples=["2和4是8的因数", "8是2和4的倍数"],
        common_mistakes=["混淆因数和倍数", "1和本身"],
    ),
    KnowledgePoint(
        id="math_g5_008",
        name="折线统计图",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g4_006"],
        description="会看会画折线统计图，分析数据变化趋势",
        examples=["温度变化统计"],
        common_mistakes=["点位置错误", "连线错误"],
    ),
    KnowledgePoint(
        id="math_g5_009",
        name="可能性",
        grade=5,
        difficulty=Difficulty.MEDIUM,
        description="理解可能性的大小，会计算简单事件的概率",
        examples=["抛硬币正面朝上的可能性是1/2"],
        common_mistakes=["可能性和必然事件混淆", "概率计算错误"],
    ),
    KnowledgePoint(
        id="math_g5_010",
        name="优化策略",
        grade=5,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g5_004"],
        description="运用数学知识解决生活中的优化问题",
        examples=["怎样安排时间最省", "怎样用料最节约"],
        common_mistakes=["没有考虑所有情况", "选择方案不合理"],
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