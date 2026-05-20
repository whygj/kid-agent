"""
小学数学 3-5 年级知识点数据（人教版）
覆盖三年级上/下册、四年级上/下册、五年级上/下册全部单元，
每个年级至少 25 个知识点，含跨年级前置依赖。
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    EXPERT = 5


@dataclass
class KnowledgePoint:
    id: str
    grade: int
    name: str
    description: str
    difficulty: Difficulty
    category: str
    prerequisites: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


# ─────────────────────────────────────────────
# 三年级（共 28 个知识点）
# ─────────────────────────────────────────────

GRADE_3_POINTS: List[KnowledgePoint] = [

    # ===== 三年级上册 =====

    # 1. 时、分、秒
    KnowledgePoint(
        id="math_g3_001", grade=3,
        name="认识秒",
        description="认识时间单位秒，知道1分=60秒，能读出钟面上的秒针位置。",
        difficulty=Difficulty.EASY,
        category="量与计量",
        prerequisites=["math_g2_006"],  # 二年级认识时间（时、分）
        examples=[
            "秒针走一小格是1秒，走一大格是5秒，走一圈是60秒。",
            "1分 = 60秒",
        ],
        common_mistakes=[
            "把秒针和分针混淆。",
            "误以为1分=100秒。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_002", grade=3,
        name="时间单位的换算与计算",
        description="能进行时、分、秒之间的简单换算，计算经过的时间。",
        difficulty=Difficulty.MEDIUM,
        category="量与计量",
        prerequisites=["math_g3_001", "math_g2_006"],
        examples=[
            "2分 = 120秒",
            "从8:15到8:40经过了25分钟。",
            "1时30分 = 90分",
        ],
        common_mistakes=[
            "进率弄错（时、分、秒是60进制而非10进制）。",
            "计算经过时间时直接用大数减小数，忽略借位。",
        ],
    ),

    # 2. 万以内的加法和减法（一）
    KnowledgePoint(
        id="math_g3_003", grade=3,
        name="两位数加减两位数口算",
        description="能口算100以内的两位数加、减两位数。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g2_002", "math_g2_003"],  # 二年级100以内加减法
        examples=[
            "35 + 48 = 83",
            "72 - 36 = 36",
        ],
        common_mistakes=[
            "个位进位后忘记给十位加1。",
            "退位减法时忘记从十位退1。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_004", grade=3,
        name="几百几十加减几百几十",
        description="能计算几百几十加、减几百几十的算式，如340+280。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_003", "math_g2_005"],  # 二年级万以内认识
        examples=[
            "340 + 280 = 620",
            "650 - 370 = 280",
        ],
        common_mistakes=[
            "百位相加后忘记加十位进上来的1。",
            "十位不够减时退位处理错误。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_005", grade=3,
        name="估算",
        description="能对万以内加减法的结果进行合理估算，用≈表示估算结果。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_004"],
        examples=[
            "403 + 298 ≈ 400 + 300 = 700",
            "692 - 308 ≈ 700 - 300 = 400",
        ],
        common_mistakes=[
            "估算结果与精确计算结果差距太大（如把692估成600）。",
            "混淆≈和=的含义。",
        ],
    ),

    # 3. 测量
    KnowledgePoint(
        id="math_g3_006", grade=3,
        name="认识毫米和分米",
        description="认识长度单位毫米(mm)和分米(dm)，知道1cm=10mm，1dm=10cm，能测量物体长度。",
        difficulty=Difficulty.EASY,
        category="量与计量",
        prerequisites=["math_g2_008"],  # 二年级认识厘米和米
        examples=[
            "1厘米 = 10毫米",
            "1分米 = 10厘米",
            "一枚硬币的厚度大约是1毫米。",
        ],
        common_mistakes=[
            "毫米和厘米的进率记错。",
            "测量时没有从0刻度线对齐。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_007", grade=3,
        name="认识千米",
        description="认识长度单位千米(km)，知道1千米=1000米，能用千米描述较长距离。",
        difficulty=Difficulty.EASY,
        category="量与计量",
        prerequisites=["math_g3_006", "math_g2_008"],
        examples=[
            "1千米 = 1000米",
            "学校到家的距离大约是3千米。",
        ],
        common_mistakes=[
            "把千米和米的进率记成100。",
            "日常生活中对千米缺乏直观感受。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_008", grade=3,
        name="认识吨",
        description="认识质量单位吨(t)，知道1吨=1000千克，能用吨描述较重物体。",
        difficulty=Difficulty.EASY,
        category="量与计量",
        prerequisites=["math_g2_009"],  # 二年级认识克和千克
        examples=[
            "1吨 = 1000千克",
            "一辆卡车载重约5吨。",
        ],
        common_mistakes=[
            "吨和千克的进率记错。",
            "把质量单位和长度单位混淆。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_009", grade=3,
        name="长度单位和质量单位的综合换算",
        description="能综合运用千米、米、分米、厘米、毫米以及吨、千克、克进行换算和比较。",
        difficulty=Difficulty.HARD,
        category="量与计量",
        prerequisites=["math_g3_006", "math_g3_007", "math_g3_008"],
        examples=[
            "3千米50米 = 3050米",
            "2吨 = 2000千克",
            "5dm - 30cm = 20cm",
        ],
        common_mistakes=[
            "复合单位换算时漏算某一部分。",
            "不同单位加减时忘记先统一单位。",
        ],
    ),

    # 4. 万以内的加法和减法（二）
    KnowledgePoint(
        id="math_g3_010", grade=3,
        name="三位数加三位数（连续进位）",
        description="掌握三位数加三位数的笔算方法，包括连续进位的情况。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_004"],
        examples=[
            "475 + 368 = 843",
            "599 + 401 = 1000",
        ],
        common_mistakes=[
            "连续两次进位时漏加。",
            "百位相加满十时忘记向千位进1。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_011", grade=3,
        name="三位数减三位数（连续退位）",
        description="掌握三位数减三位数的笔算方法，包括连续退位及被减数中间有0的情况。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g3_010"],
        examples=[
            "503 - 247 = 256",
            "1000 - 528 = 472",
        ],
        common_mistakes=[
            "被减数中间有0时退位处理错误。",
            "连续退位时忘记某一位已退1。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_012", grade=3,
        name="加减法的验算",
        description="掌握加减法的验算方法：加法用交换加数或和-加数验算，减法用差+减数或被减数-差验算。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_010", "math_g3_011"],
        examples=[
            "验算456+278=734：734-456=278 ✓",
            "验算800-357=443：443+357=800 ✓",
        ],
        common_mistakes=[
            "验算时把减数和差的位置搞混。",
            "用错误的结果去验算，无法发现问题。",
        ],
    ),

    # 5. 倍的认识
    KnowledgePoint(
        id="math_g3_013", grade=3,
        name="认识倍",
        description="理解『倍』的含义，能求一个数是另一个数的几倍，或求一个数的几倍是多少。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g2_004"],  # 二年级乘法基础
        examples=[
            "8是4的2倍，因为8÷4=2。",
            "5的3倍是15，因为5×3=15。",
        ],
        common_mistakes=[
            "把『是几倍』和『的几倍』混淆。",
            "用加法代替乘法求『几倍是多少』。",
        ],
    ),

    # 6. 多位数乘一位数
    KnowledgePoint(
        id="math_g3_014", grade=3,
        name="口算乘法（整十整百乘一位数）",
        description="能口算整十、整百数乘一位数。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g2_004"],  # 二年级表内乘法
        examples=[
            "20 × 3 = 60",
            "300 × 4 = 1200",
        ],
        common_mistakes=[
            "忘记末尾的0。",
            "把乘法做成加法（如200×3=203）。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_015", grade=3,
        name="笔算多位数乘一位数（不进位）",
        description="掌握两、三位数乘一位数的竖式计算（不进位情况）。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_014"],
        examples=[
            "123 × 2 = 246",
            "312 × 3 = 936",
        ],
        common_mistakes=[
            "数位没有对齐。",
            "漏乘某一位。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_016", grade=3,
        name="笔算多位数乘一位数（进位）",
        description="掌握两、三位数乘一位数的竖式计算（含一次和连续进位）。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g3_015"],
        examples=[
            "167 × 4 = 668",
            "249 × 8 = 1992",
        ],
        common_mistakes=[
            "进位数忘记加到前一位。",
            "连续进位时只加第一次的进位。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_017", grade=3,
        name="乘法中的0",
        description="知道0和任何数相乘都得0，能处理因数中间或末尾有0的乘法。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_016"],
        examples=[
            "0 × 5 = 0",
            "108 × 5 = 540",
            "340 × 3 = 1020",
        ],
        common_mistakes=[
            "因数中间有0时跳过该位直接乘下一位。",
            "0 × 5 = 5（与0+5混淆）。",
        ],
    ),

    # 7. 长方形和正方形
    KnowledgePoint(
        id="math_g3_018", grade=3,
        name="四边形的认识",
        description="认识四边形的特征：有4条直的边和4个角，能辨认四边形。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g1_008"],  # 一年级认识图形
        examples=[
            "长方形、正方形、平行四边形都是四边形。",
            "三角形不是四边形。",
        ],
        common_mistakes=[
            "把不是封闭图形的四条线段当成四边形。",
            "忽略四边形边的位置关系。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_019", grade=3,
        name="长方形和正方形的特征",
        description="掌握长方形对边相等、4个角都是直角；正方形4条边都相等、4个角都是直角。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g3_018"],
        examples=[
            "长方形长5cm、宽3cm，周长 = (5+3)×2 = 16cm。",
            "正方形边长4cm，周长 = 4×4 = 16cm。",
        ],
        common_mistakes=[
            "混淆长方形的长和宽。",
            "认为长方形和正方形没有关系。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_020", grade=3,
        name="长方形和正方形的周长",
        description="理解周长含义，能计算长方形和正方形的周长。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g3_019"],
        examples=[
            "长方形周长 = (长+宽)×2",
            "正方形周长 = 边长×4",
            "长8cm、宽5cm的长方形周长 = (8+5)×2 = 26cm。",
        ],
        common_mistakes=[
            "忘记乘2（只算了一条长加一条宽）。",
            "周长和面积概念混淆。",
        ],
    ),

    # 8. 分数的初步认识
    KnowledgePoint(
        id="math_g3_021", grade=3,
        name="认识几分之一",
        description="初步认识分数，理解几分之一的含义，能读写简单分数，知道分数各部分名称。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=[],
        examples=[
            "把一个蛋糕平均分成4份，每份是它的1/4。",
            "分子、分母、分数线的含义。",
        ],
        common_mistakes=[
            "没有『平均分』也写成几分之一。",
            "分子和分母的位置写反。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_022", grade=3,
        name="认识几分之几",
        description="认识几分之几，会比较同分母分数的大小。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_021"],
        examples=[
            "3/8表示把一个整体平均分成8份，取其中的3份。",
            "3/8 > 1/8（同分母分数，分子大的大）。",
        ],
        common_mistakes=[
            "比较时只看分子不看分母。",
            "分母越大认为分数越大（如1/8 > 1/4）。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_023", grade=3,
        name="简单的分数加减法",
        description="能计算同分母分数的简单加减法（分母不超过10）。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_022"],
        examples=[
            "2/7 + 3/7 = 5/7",
            "5/8 - 1/8 = 4/8",
        ],
        common_mistakes=[
            "把分母也相加（如2/7+3/7=5/14）。",
            "结果没有化简（如4/8应化为1/2）。",
        ],
    ),

    # 9. 数学广角─集合
    KnowledgePoint(
        id="math_g3_024", grade=3,
        name="集合（韦恩图）",
        description="初步体会集合思想，能用韦恩图（Venn图）表示两个集合之间的关系，解决简单的重叠问题。",
        difficulty=Difficulty.HARD,
        category="数学思想",
        prerequisites=[],
        examples=[
            "参加语文兴趣小组的有8人，参加数学的有9人，两个都参加的有3人，共8+9-3=14人。",
        ],
        common_mistakes=[
            "直接把两个数相加，忘记减去重叠部分。",
            "韦恩图各部分的数字填写错误。",
        ],
    ),

    # ===== 三年级下册 =====

    # 1. 位置与方向
    KnowledgePoint(
        id="math_g3_025", grade=3,
        name="认识东、南、西、北",
        description="能辨认东、南、西、北四个方向，能看简单的路线图。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g1_007"],  # 一年级上下前后左右
        examples=[
            "早晨太阳在东方。",
            "面向北方，右边是东方。",
        ],
        common_mistakes=[
            "把左右方向和东南西北混淆。",
            "转身后方向判断出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_026", grade=3,
        name="认识东北、东南、西北、西南",
        description="认识八个方向，能用方向词描述物体的位置和行走路线。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g3_025"],
        examples=[
            "学校在小明家的东北方向。",
            "从家出发向东走，再向东南方向走就到了公园。",
        ],
        common_mistakes=[
            "把东北和西北搞混。",
            "路线描述时方向判断出错。",
        ],
    ),

    # 2. 除数是一位数的除法
    KnowledgePoint(
        id="math_g3_027", grade=3,
        name="口算除法",
        description="能口算一位数除整十、整百、整千数及两位数。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g2_007"],  # 二年级表内除法
        examples=[
            "60 ÷ 3 = 20",
            "800 ÷ 4 = 200",
            "93 ÷ 3 = 31",
        ],
        common_mistakes=[
            "600÷3=20（漏掉一个0）。",
            "口算两位数除一位数时十位余数忘记和个位合并。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_028", grade=3,
        name="笔算除法（两位数÷一位数）",
        description="掌握两位数除以一位数的笔算方法，理解每一步的含义。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_027"],
        examples=[
            "72 ÷ 6 = 12",
            "85 ÷ 5 = 17",
        ],
        common_mistakes=[
            "商的位置写错。",
            "余数大于除数。",
        ],
    ),

    # 额外补充三年级综合知识点
    KnowledgePoint(
        id="math_g3_029", grade=3,
        name="复式统计表",
        description="能读懂简单的复式统计表，能收集和整理数据并填写复式统计表，进行简单分析。",
        difficulty=Difficulty.MEDIUM,
        category="统计与概率",
        prerequisites=["math_g2_010"],  # 二年级数据收集整理
        examples=[
            "某班男生和女生分别喜欢不同运动项目的人数统计表。",
            "通过复式统计表比较两个小组的数据。",
        ],
        common_mistakes=[
            "表格中行和列的数据填写错位。",
            "忽略合计行的计算。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_030", grade=3,
        name="年、月、日",
        description="认识年、月、日，知道大月（31天）和小月（30天），知道二月的天数和平闰年。",
        difficulty=Difficulty.MEDIUM,
        category="量与计量",
        prerequisites=["math_g2_006"],
        examples=[
            "大月：1、3、5、7、8、10、12月（31天）。",
            "闰年二月有29天，全年366天。",
        ],
        common_mistakes=[
            "记错哪些月是大月/小月。",
            "判断闰年的方法不正确。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_031", grade=3,
        name="24时计时法",
        description="掌握24时计时法，能将12时计时法和24时计时法互相转换，计算经过时间。",
        difficulty=Difficulty.HARD,
        category="量与计量",
        prerequisites=["math_g3_030", "math_g3_002"],
        examples=[
            "下午3时 = 15时",
            "上午9时到下午5时经过了8小时。",
            "火车13:30出发，17:45到达，经过4小时15分。",
        ],
        common_mistakes=[
            "下午时间忘记加12。",
            "经过时间跨天时计算出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_032", grade=3,
        name="小数的初步认识",
        description="结合具体情境初步认识小数，能读写简单的小数，会比较一位小数的大小。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g2_005", "math_g3_022"],  # 万以内数的认识 + 分数初步
        examples=[
            "0.5读作零点五，表示十分之五。",
            "3.2元 = 3元2角。",
            "0.8 > 0.5",
        ],
        common_mistakes=[
            "小数点位置读错或写错。",
            "认为0.3 > 0.8（按整数比较方式）。",
        ],
    ),
    KnowledgePoint(
        id="math_g3_033", grade=3,
        name="搭配问题",
        description="能用图示连线等方法解决简单的搭配问题，初步感受排列与组合思想。",
        difficulty=Difficulty.MEDIUM,
        category="数学思想",
        prerequisites=["math_g1_003"],  # 一年级分类与整理
        examples=[
            "3件上衣和2条裤子有3×2=6种搭配方法。",
            "从甲地到乙地有3条路，从乙地到丙地有4条路，共3×4=12种走法。",
        ],
        common_mistakes=[
            "遗漏或重复某种搭配。",
            "把排列和组合混淆。",
        ],
    ),
]


# ─────────────────────────────────────────────
# 四年级（共 27 个知识点）
# ─────────────────────────────────────────────

GRADE_4_POINTS: List[KnowledgePoint] = [

    # ===== 四年级上册 =====

    # 1. 大数的认识
    KnowledgePoint(
        id="math_g4_001", grade=4,
        name="亿以内数的认识",
        description="认识计数单位万、十万、百万、千万、亿，掌握亿以内数的读法和写法。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g2_005", "math_g3_004"],  # 万以内数的认识
        examples=[
            "3456789读作：三百四十五万六千七百八十九。",
            "一亿 = 100000000",
        ],
        common_mistakes=[
            "每级中间有0时多读或少读零。",
            "写数时位数不对。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_002", grade=4,
        name="亿以上数的认识与改写",
        description='能读写亿以上的数，能将大数改写成以"万"或"亿"为单位的数。',
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_001"],
        examples=[
            "120000000 = 1.2亿",
            "3450000 = 345万",
        ],
        common_mistakes=[
            "改写时小数点点错位置。",
            "省略尾数后的近似数与精确数混淆。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_003", grade=4,
        name="大数的比较与近似数",
        description="能比较亿以内数的大小，能用四舍五入法求大数的近似数。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_001"],
        examples=[
            "3456789 > 3456788（位数相同从最高位比）。",
            "3456789 ≈ 346万（省略万位后面的尾数）。",
        ],
        common_mistakes=[
            "四舍五入时看错位数的下一位。",
            "比较时只看开头数字不看位数。",
        ],
    ),

    # 2. 公顷和平方千米
    KnowledgePoint(
        id="math_g4_004", grade=4,
        name="认识公顷和平方千米",
        description="认识面积单位公顷(hm²)和平方千米(km²)，知道1公顷=10000平方米，1平方千米=100公顷。",
        difficulty=Difficulty.MEDIUM,
        category="量与计量",
        prerequisites=["math_g3_019", "math_g3_020"],  # 长方形正方形特征和周长
        examples=[
            "1公顷 = 10000平方米",
            "1平方千米 = 100公顷 = 1000000平方米",
        ],
        common_mistakes=[
            "公顷和平方米的进率记成100。",
            "平方千米和平方米的进率算错。",
        ],
    ),

    # 3. 角的度量
    KnowledgePoint(
        id="math_g4_005", grade=4,
        name="线段、直线和射线",
        description="认识线段、直线和射线，理解它们的联系和区别。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g1_008"],
        examples=[
            "线段有两个端点，可以度量长度。",
            "射线有一个端点，向一个方向无限延伸。",
            "直线没有端点，向两个方向无限延伸。",
        ],
        common_mistakes=[
            "把射线和直线混淆。",
            "认为直线可以度量长度。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_006", grade=4,
        name="角的分类",
        description="认识锐角、直角、钝角、平角和周角，知道它们之间的关系。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_005"],
        examples=[
            "锐角 < 90°, 直角 = 90°, 90° < 钝角 < 180°",
            "平角 = 180°, 周角 = 360°",
            "1周角 = 2平角 = 4直角",
        ],
        common_mistakes=[
            "混淆钝角和平角的界限。",
            "180°和360°分别对应平角和周角记反。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_007", grade=4,
        name="角的度量与画角",
        description="会用量角器量角和画指定度数的角。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g4_006"],
        examples=[
            "用量角器量角时：中心对顶点，0刻度线对一边。",
            "画一个65°的角。",
        ],
        common_mistakes=[
            "量角器读数时用错内圈或外圈刻度。",
            "中心点没有对准角的顶点。",
        ],
    ),

    # 4. 三位数乘两位数
    KnowledgePoint(
        id="math_g4_008", grade=4,
        name="三位数乘两位数的笔算",
        description="掌握三位数乘两位数的竖式计算方法，理解每一步的含义。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g3_016", "math_g3_014"],  # 多位数乘一位数
        examples=[
            "145 × 12 = 1740",
            "234 × 56 = 13104",
        ],
        common_mistakes=[
            "用十位上的数去乘时，积的末位没有和十位对齐。",
            "两次部分积相加时进位遗漏。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_009", grade=4,
        name="积的变化规律",
        description="探索并掌握积的变化规律：一个因数不变，另一个因数乘/除以几，积也乘/除以几。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_008"],
        examples=[
            "3 × 15 = 45，则 30 × 15 = 450",
            "8 × 25 = 200，则 4 × 25 = 100",
        ],
        common_mistakes=[
            "两个因数同时变化时直接把变化量相乘。",
            "变化方向搞反（乘看成除）。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_010", grade=4,
        name="常见的数量关系",
        description='掌握"单价x数量=总价""速度x时间=路程"等常见数量关系。',
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_008"],
        examples=[
            "每本书25元，买12本，总价 = 25 × 12 = 300元。",
            "汽车每小时行80千米，行3小时，路程 = 80 × 3 = 240千米。",
        ],
        common_mistakes=[
            "把速度和路程的单位写错。",
            "数量关系式变形时出错（如求时间=路程÷速度）。",
        ],
    ),

    # 5. 平行四边形和梯形
    KnowledgePoint(
        id="math_g4_011", grade=4,
        name="平行与垂直",
        description="理解平行线和垂线的概念，能用三角尺和直尺画平行线和垂线。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_005"],
        examples=[
            "在同一平面内不相交的两条直线叫平行线。",
            "两条直线相交成直角，就说这两条直线互相垂直。",
        ],
        common_mistakes=[
            "认为不相交的两条直线一定平行（忽略不在同一平面的情况）。",
            "画垂线时三角尺摆放不正确。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_012", grade=4,
        name="平行四边形的认识",
        description="认识平行四边形的特征（对边平行且相等），了解平行四边形容易变形的性质。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g4_011", "math_g3_018"],
        examples=[
            "平行四边形对边平行且相等。",
            "长方形和正方形是特殊的平行四边形。",
        ],
        common_mistakes=[
            "认为平行四边形四个角相等。",
            "把平行四边形和梯形混淆。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_013", grade=4,
        name="梯形的认识",
        description="认识梯形的特征（只有一组对边平行），知道等腰梯形和直角梯形。",
        difficulty=Difficulty.EASY,
        category="图形与几何",
        prerequisites=["math_g4_012"],
        examples=[
            "梯形只有一组对边平行，平行的那组边分别叫上底和下底。",
            "等腰梯形两腰相等。",
        ],
        common_mistakes=[
            "把梯形的上底和下底搞反。",
            "认为梯形必须有一组边相等。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_014", grade=4,
        name="画平行四边形和梯形的高",
        description="能在平行四边形和梯形中画高，理解高的含义。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g4_012", "math_g4_013", "math_g4_011"],
        examples=[
            "平行四边形的高是从一条边到对边的垂直线段。",
            "梯形的高是两底之间的垂直线段。",
        ],
        common_mistakes=[
            "高没有垂直于底边。",
            "把底边的长度当成高。",
        ],
    ),

    # 6. 除数是两位数的除法
    KnowledgePoint(
        id="math_g4_015", grade=4,
        name="口算除法（整十数除整十、整百数）",
        description="能口算整十数除整十数、整十数除几百几十数。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g3_027"],
        examples=[
            "60 ÷ 20 = 3",
            "150 ÷ 30 = 5",
        ],
        common_mistakes=[
            "被除数和除数末尾的0消去时出错。",
            "商末尾多写0。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_016", grade=4,
        name="笔算除法（四舍五入试商）",
        description="掌握用四舍五入法把除数看作整十数来试商的方法。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_015", "math_g3_028"],
        examples=[
            "84 ÷ 21：把21看作20来试商，商4。",
            "196 ÷ 39：把39看作40来试商。",
        ],
        common_mistakes=[
            "四舍初商可能偏大需要调小；五入初商可能偏小需要调大。",
            "试商后忘记检验。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_017", grade=4,
        name="商的变化规律",
        description="探索并掌握商的变化规律：被除数/除数同时乘/除以相同的数（0除外），商不变。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_016"],
        examples=[
            "48 ÷ 12 = 4，则 480 ÷ 120 = 4",
            "36 ÷ 6 = 6，则 360 ÷ 60 = 6",
        ],
        common_mistakes=[
            "被除数和除数没有同时变化。",
            "余数的处理出错（商不变规律中余数会变化）。",
        ],
    ),

    # 7. 条形统计图
    KnowledgePoint(
        id="math_g4_018", grade=4,
        name="条形统计图",
        description="能读懂条形统计图，能根据数据绘制条形统计图，并进行简单分析。",
        difficulty=Difficulty.MEDIUM,
        category="统计与概率",
        prerequisites=["math_g3_029"],  # 复式统计表
        examples=[
            "一格可以代表多个单位（如一格代表5人）。",
            "从条形统计图中读出最大值和最小值。",
        ],
        common_mistakes=[
            "纵轴刻度不均匀。",
            "条的宽度不一致。",
        ],
    ),

    # 8. 数学广角─优化
    KnowledgePoint(
        id="math_g4_019", grade=4,
        name="优化问题（沏茶、烙饼）",
        description="能用优化思想合理安排时间，如沏茶问题、烙饼问题。",
        difficulty=Difficulty.HARD,
        category="数学思想",
        prerequisites=[],
        examples=[
            "沏茶问题：烧水的同时洗茶杯，节省时间。",
            "烙饼问题：每次最多烙2张，烙3张饼最少需要3次。",
        ],
        common_mistakes=[
            "一步一步排队思考，没有利用并行时间。",
            "烙饼问题时没有利用锅的空位。",
        ],
    ),

    # ===== 四年级下册 =====

    # 1. 四则运算
    KnowledgePoint(
        id="math_g4_020", grade=4,
        name="四则混合运算顺序",
        description="掌握没有括号和有括号的四则混合运算的顺序。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_010", "math_g3_028", "math_g3_016"],
        examples=[
            "没有括号：先乘除后加减。",
            "有小括号：先算小括号里面的。",
            "25 + 12 × 3 = 25 + 36 = 61",
        ],
        common_mistakes=[
            "从左到右依次计算，忽略先乘除后加减。",
            "括号内的运算顺序搞错。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_021", grade=4,
        name="有关0的运算",
        description="知道0在加、减、乘、除中的特性：0不能作除数。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g4_020"],
        examples=[
            "0 + a = a",
            "a - 0 = a",
            "a × 0 = 0",
            "0 ÷ a = 0（a≠0）",
            "0不能作除数。",
        ],
        common_mistakes=[
            "认为0÷0=0或0÷0=1。",
            "5 ÷ 0 = 0（错误，0不能作除数）。",
        ],
    ),

    # 2. 观察物体（二）
    KnowledgePoint(
        id="math_g4_022", grade=4,
        name="观察物体（从不同方向看）",
        description="能辨认从前面、上面、侧面观察由几个正方体搭成的物体所看到的形状。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g1_008"],
        examples=[
            "由4个小正方体搭成的物体，从前面看到3个正方形。",
            "从不同方向看同一个物体，看到的形状可能不同。",
        ],
        common_mistakes=[
            "把从前面看到的和从侧面看到的混淆。",
            "漏数被遮挡的正方体。",
        ],
    ),

    # 3. 运算定律
    KnowledgePoint(
        id="math_g4_023", grade=4,
        name="加法交换律和结合律",
        description="理解并会运用加法交换律（a+b=b+a）和加法结合律（(a+b)+c=a+(b+c)）进行简便运算。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_020"],
        examples=[
            "287 + 63 + 37 = 287 + (63 + 37) = 287 + 100 = 387",
            "135 + 78 + 65 = 135 + 65 + 78 = 200 + 78 = 278",
        ],
        common_mistakes=[
            "结合律只改变运算顺序，误以为也改变运算符号。",
            "凑整时把数算错。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_024", grade=4,
        name="乘法交换律和结合律",
        description="理解并会运用乘法交换律（a×b=b×a）和乘法结合律（(a×b)×c=a×(b×c)）进行简便运算。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_023", "math_g3_016"],
        examples=[
            "25 × 37 × 4 = 25 × 4 × 37 = 100 × 37 = 3700",
            "125 × 8 = 1000",
        ],
        common_mistakes=[
            "没有凑成整十整百的数就直接计算。",
            "25×4=100和125×8=1000记不牢。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_025", grade=4,
        name="乘法分配律",
        description="理解并会运用乘法分配律（(a+b)×c=a×c+b×c）进行简便运算。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_024"],
        examples=[
            "102 × 45 = (100 + 2) × 45 = 100×45 + 2×45 = 4500 + 90 = 4590",
            "36 × 99 = 36 × (100 - 1) = 3600 - 36 = 3564",
        ],
        common_mistakes=[
            "乘法分配律展开时漏乘某一项。",
            "混淆乘法分配律和结合律。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_026", grade=4,
        name="减法和除法的运算性质",
        description="理解并运用减法的运算性质（a-b-c=a-(b+c)）和除法的运算性质（a÷b÷c=a÷(b×c)）。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_025"],
        examples=[
            "536 - 178 - 22 = 536 - (178 + 22) = 536 - 200 = 336",
            "2700 ÷ 25 ÷ 4 = 2700 ÷ (25 × 4) = 2700 ÷ 100 = 27",
        ],
        common_mistakes=[
            "a-b-c 错误地写成 a-(b-c)。",
            "除法性质中把÷(b×c)写成÷b×c。",
        ],
    ),

    # 4. 小数的意义和性质
    KnowledgePoint(
        id="math_g4_027", grade=4,
        name="小数的意义",
        description="理解小数的意义，知道小数的计数单位是十分之一、百分之一等。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_032", "math_g3_022"],  # 小数初步认识 + 分数
        examples=[
            "0.3表示3个十分之一，即3/10。",
            "0.25表示25个百分之一，即25/100。",
        ],
        common_mistakes=[
            "混淆小数的数位（十分位、百分位等）。",
            "认为小数一定比整数小。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_028", grade=4,
        name="小数的性质和大小比较",
        description="掌握小数的性质（末尾添上或去掉0，大小不变），能比较小数的大小。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_027"],
        examples=[
            "0.30 = 0.3",
            "3.45 > 3.4 > 3.05",
        ],
        common_mistakes=[
            "认为0.3和0.30不同。",
            "比较时只看小数位数的多少（如认为0.6 < 0.58）。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_029", grade=4,
        name="小数点移动引起大小变化",
        description="掌握小数点向右移动一位、两位、三位，小数分别扩大到原数的10倍、100倍、1000倍，反之缩小。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_028"],
        examples=[
            "3.56 → 35.6（扩大到10倍）",
            "3.56 → 356（扩大到100倍）",
            "3.56 → 0.356（缩小到原来的1/10）",
        ],
        common_mistakes=[
            "移动方向和倍数关系搞反。",
            "位数不够时没有补0。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_030", grade=4,
        name="小数与单位换算",
        description="能利用小数点移动规律进行单位换算（如厘米和米、克和千克之间）。",
        difficulty=Difficulty.HARD,
        category="量与计量",
        prerequisites=["math_g4_029", "math_g3_009"],
        examples=[
            "350cm = 3.5m",
            "0.85kg = 850g",
            "1.25m = 1m25cm",
        ],
        common_mistakes=[
            "换算方向搞反。",
            "复合单位换算时出错（如1.25m ≠ 1m2.5cm）。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_031", grade=4,
        name="求一个小数的近似数",
        description='能用四舍五入法求小数的近似数，能将非整万/整亿数改写成以"万"或"亿"为单位的数。',
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_028", "math_g4_002"],
        examples=[
            "3.456保留两位小数 ≈ 3.46",
            "345678 = 34.5678万",
        ],
        common_mistakes=[
            "四舍五入时看错要保留的后一位。",
            "近似数末尾的0随意去掉（如3.40 ≠ 3.4的精确度不同）。",
        ],
    ),

    # 5. 三角形
    KnowledgePoint(
        id="math_g4_032", grade=4,
        name="三角形的特性",
        description="认识三角形的特征（三条边、三个角、三个顶点），理解三角形的稳定性，掌握三角形三边关系。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_011", "math_g1_008"],
        examples=[
            "三角形任意两边之和大于第三边。",
            "3cm、4cm、5cm可以围成三角形，因为3+4>5。",
        ],
        common_mistakes=[
            "只验证一组两边之和大于第三边就下结论。",
            "认为三角形不具有稳定性。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_033", grade=4,
        name="三角形的分类",
        description="能按角分为锐角三角形、直角三角形、钝角三角形；按边分为等腰三角形和等边三角形。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_032", "math_g4_006"],
        examples=[
            "等边三角形的三条边相等，三个角都是60°。",
            "等腰三角形的两条边相等，两个底角相等。",
        ],
        common_mistakes=[
            "认为等腰三角形不可能是直角三角形。",
            "混淆按角分类和按边分类的标准。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_034", grade=4,
        name="三角形的内角和",
        description="知道三角形的内角和是180°，能利用内角和求未知角的度数。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_033", "math_g4_006"],
        examples=[
            "一个三角形有两个角分别是50°和70°，第三个角 = 180° - 50° - 70° = 60°。",
            "直角三角形中两个锐角之和 = 90°。",
        ],
        common_mistakes=[
            "内角和记成360°。",
            "求第三个角时用减法计算出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_035", grade=4,
        name="三角形的底和高",
        description="理解三角形的底和高的含义，能画出三角形指定底边上的高。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g4_032", "math_g4_011"],
        examples=[
            "从三角形的一个顶点向对边作垂线，顶点和垂足之间的线段就是高。",
            "一个三角形有三条高。",
        ],
        common_mistakes=[
            "高没有垂直于底边。",
            "钝角三角形外侧的高画不出来或画错。",
        ],
    ),

    # 6. 小数的加法和减法
    KnowledgePoint(
        id="math_g4_036", grade=4,
        name="小数加减法",
        description="掌握小数加减法的计算方法：小数点对齐，按整数加减法计算。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_027", "math_g3_010", "math_g3_011"],
        examples=[
            "3.54 + 2.78 = 6.32",
            "8.3 - 4.56 = 3.74",
        ],
        common_mistakes=[
            "末位对齐而非小数点对齐。",
            "小数位数不同时忘记补0。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_037", grade=4,
        name="小数的加减混合运算",
        description="能进行小数加减混合运算，能运用运算定律进行简便计算。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g4_036", "math_g4_023"],
        examples=[
            "5.62 + 3.47 + 4.38 = 5.62 + 4.38 + 3.47 = 10 + 3.47 = 13.47",
            "15.2 - 3.56 - 6.44 = 15.2 - (3.56 + 6.44) = 15.2 - 10 = 5.2",
        ],
        common_mistakes=[
            "小数加减混合运算时运算顺序出错。",
            "简便运算时凑整出错。",
        ],
    ),

    # 7. 图形的运动（二）
    KnowledgePoint(
        id="math_g4_038", grade=4,
        name="轴对称图形",
        description="进一步认识轴对称图形，能画出轴对称图形的另一半，能画出对称轴。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g2_011"],  # 二年级图形运动初步
        examples=[
            "正方形有4条对称轴。",
            "画轴对称图形的另一半时，对应点到对称轴的距离相等。",
        ],
        common_mistakes=[
            "对称轴画错位置。",
            "对应点连线没有垂直于对称轴。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_039", grade=4,
        name="平移",
        description="能在方格纸上画出平移后的图形，能数出图形平移的距离。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_038"],
        examples=[
            "把三角形向右平移5格。",
            "平移不改变图形的形状和大小。",
        ],
        common_mistakes=[
            "数平移格数时数错（应数对应点之间的格数，而非两个图形之间的间隔）。",
            "平移时图形的形状发生了变化。",
        ],
    ),

    # 8. 平均数与条形统计图
    KnowledgePoint(
        id="math_g4_040", grade=4,
        name="平均数",
        description="理解平均数的含义，掌握求平均数的方法（总数÷份数=平均数）。",
        difficulty=Difficulty.MEDIUM,
        category="统计与概率",
        prerequisites=["math_g4_020", "math_g4_016"],
        examples=[
            "小明5次考试成绩分别是85、90、88、92、95，平均分 = (85+90+88+92+95)÷5 = 90。",
            "平均数反映一组数据的整体水平。",
        ],
        common_mistakes=[
            "把最大值和最小值的平均当作整组数据的平均。",
            "平均数不一定是数据中的某个数。",
        ],
    ),
    KnowledgePoint(
        id="math_g4_041", grade=4,
        name="复式条形统计图",
        description="能读懂复式条形统计图，能绘制复式条形统计图并进行数据分析。",
        difficulty=Difficulty.HARD,
        category="统计与概率",
        prerequisites=["math_g4_018", "math_g4_040"],
        examples=[
            "用不同颜色的条形分别表示男生和女生的数据。",
            "通过复式条形统计图比较两组数据。",
        ],
        common_mistakes=[
            "忘记标注图例。",
            "纵轴单位不一致。",
        ],
    ),

    # 9. 数学广角—鸡兔同笼
    KnowledgePoint(
        id="math_g4_042", grade=4,
        name="鸡兔同笼问题",
        description="能用列表法、假设法解决鸡兔同笼等类似问题。",
        difficulty=Difficulty.EXPERT,
        category="数学思想",
        prerequisites=["math_g4_020"],
        examples=[
            "鸡兔共8只，共26条腿。假设全是鸡：8×2=16条腿，差26-16=10条腿，每只兔比鸡多2条腿，所以兔=10÷2=5只，鸡=8-5=3只。",
        ],
        common_mistakes=[
            "假设法中『差』的除数搞错。",
            "列表法中数据跳跃过大，遗漏正确答案。",
        ],
    ),
]


# ─────────────────────────────────────────────
# 五年级（共 27 个知识点）
# ─────────────────────────────────────────────

GRADE_5_POINTS: List[KnowledgePoint] = [

    # ===== 五年级上册 =====

    # 1. 小数乘法
    KnowledgePoint(
        id="math_g5_001", grade=5,
        name="小数乘整数",
        description="掌握小数乘整数的计算方法，理解积的小数位数与因数小数位数的关系。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_036", "math_g3_016"],
        examples=[
            "3.5 × 4 = 14",
            "0.28 × 5 = 1.4",
        ],
        common_mistakes=[
            "积的小数点点错位置。",
            "先按整数乘法计算后忘记确定小数位数。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_002", grade=5,
        name="小数乘小数",
        description="掌握小数乘小数的计算方法：先按整数乘法计算，再点小数点。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_001"],
        examples=[
            "2.4 × 0.8 = 1.92（共2位小数）",
            "0.56 × 0.04 = 0.0224（共4位小数）",
        ],
        common_mistakes=[
            "小数位数不够时忘记在前面补0。",
            "两个因数都小于1时认为积应该大于其中一个因数。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_003", grade=5,
        name="积的近似数",
        description="能用四舍五入法求小数乘法积的近似值。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_002", "math_g4_031"],
        examples=[
            "3.14 × 2.5 = 7.85 ≈ 7.9（保留一位小数）",
        ],
        common_mistakes=[
            "四舍五入前没有先算出精确值。",
            "保留位数与要求不符。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_004", grade=5,
        name="小数乘法的简便运算",
        description="能运用乘法运算定律进行小数乘法的简便计算。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_002", "math_g4_025"],
        examples=[
            "0.25 × 3.2 × 1.25 = 0.25 × (4 × 0.8) × 1.25 = (0.25 × 4) × (0.8 × 1.25) = 1 × 1 = 1",
            "2.5 × 4.8 = 2.5 × (4 + 0.8) = 10 + 2 = 12",
        ],
        common_mistakes=[
            "拆数时小数点位置出错。",
            "乘法分配律应用到小数时漏项。",
        ],
    ),

    # 2. 位置（用数对确定位置）
    KnowledgePoint(
        id="math_g5_005", grade=5,
        name="用数对确定位置",
        description="能用数对（列，行）表示位置，能在方格纸上用数对确定位置。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g3_025", "math_g1_007"],
        examples=[
            "小明在第3列第2行，用数对(3, 2)表示。",
            "数对(4, 5)表示第4列第5行。",
        ],
        common_mistakes=[
            "把列和行的顺序搞反（先列后行）。",
            "(3,2)和(2,3)表示不同的位置。",
        ],
    ),

    # 3. 小数除法
    KnowledgePoint(
        id="math_g5_006", grade=5,
        name="小数除以整数",
        description="掌握小数除以整数的计算方法：商的小数点和被除数的小数点对齐。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_036", "math_g4_016"],
        examples=[
            "22.4 ÷ 4 = 5.6",
            "7.83 ÷ 9 = 0.87",
        ],
        common_mistakes=[
            "商的小数点位置点错。",
            "整数部分不够除时忘记商0。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_007", grade=5,
        name="一个数除以小数",
        description="掌握除数是小数的除法：先把除数转化成整数，被除数同时扩大相同倍数再除。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_006", "math_g4_029"],
        examples=[
            "7.65 ÷ 0.85 = 765 ÷ 85 = 9",
            "12.6 ÷ 0.28 = 1260 ÷ 28 = 45",
        ],
        common_mistakes=[
            "被除数和除数小数位数不同时，被除数补0不到位。",
            "移动小数点时只移动了除数的忘记移动被除数的。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_008", grade=5,
        name="商的近似数和循环小数",
        description="能求商的近似数，认识循环小数（有限小数和无限小数）。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_007"],
        examples=[
            "10 ÷ 3 = 3.3̄（循环小数）",
            "15 ÷ 7 ≈ 2.14（保留两位小数）",
        ],
        common_mistakes=[
            "循环小数循环节标错位置。",
            "求近似数时多除了一位或少除了一位。",
        ],
    ),

    # 4. 可能性
    KnowledgePoint(
        id="math_g5_009", grade=5,
        name="可能性",
        description='初步体验事件发生的可能性，能用"一定""可能""不可能"描述事件，感受随机性。',
        difficulty=Difficulty.MEDIUM,
        category="统计与概率",
        prerequisites=[],
        examples=[
            "太阳从东方升起——一定。",
            "明天可能下雨——可能。",
            "人能活到200岁——不可能。",
        ],
        common_mistakes=[
            "把『不太可能』等同于『不可能』。",
            "对随机事件的可能性大小判断有误。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_010", grade=5,
        name="可能性的大小",
        description="能比较事件发生的可能性的大小，能设计简单公平的游戏规则。",
        difficulty=Difficulty.HARD,
        category="统计与概率",
        prerequisites=["math_g5_009"],
        examples=[
            "箱子里有3红球2白球，摸到红球的可能性比白球大。",
            "设计公平规则：双方赢的可能性相等。",
        ],
        common_mistakes=[
            "认为可能性大就一定会发生。",
            "不理解游戏规则的『公平』含义。",
        ],
    ),

    # 5. 简易方程
    KnowledgePoint(
        id="math_g5_011", grade=5,
        name="用字母表示数",
        description="能用字母表示数、运算定律和计算公式，理解字母表示数的优越性。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g4_020", "math_g4_023"],
        examples=[
            "正方形面积 S = a²（a表示边长）",
            "加法交换律：a + b = b + a",
            "速度×时间=路程：vt = s",
        ],
        common_mistakes=[
            "a²和2a混淆（a² = a×a，2a = a+a）。",
            "省略乘号时数字写在字母后面（如a3，应为3a）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_012", grade=5,
        name="方程的意义",
        description="理解方程的含义：含有未知数的等式叫方程。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g5_011"],
        examples=[
            "x + 5 = 12 是方程。",
            "3 + 5 = 8 不是方程（没有未知数）。",
            "x + 5 不是方程（不是等式）。",
        ],
        common_mistakes=[
            "把等式和方程混淆。",
            "认为含有字母的式子就是方程。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_013", grade=5,
        name="等式的性质",
        description="理解等式的性质（一）：等式两边加上或减去同一个数，左右两边仍然相等。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_012"],
        examples=[
            "如果 x + 3 = 9，那么 x + 3 - 3 = 9 - 3，即 x = 6。",
        ],
        common_mistakes=[
            "等式两边操作不一致。",
            "移项时忘记变号。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_014", grade=5,
        name="解方程（一步和两步）",
        description="能用等式的性质解一步和两步方程。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_013"],
        examples=[
            "x + 3.2 = 8 → x = 4.8",
            "2x - 4 = 10 → 2x = 14 → x = 7",
        ],
        common_mistakes=[
            "2x = 14 → x = 7 这一步忘记除以2。",
            "检验时把解代入方程计算出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_015", grade=5,
        name="列方程解应用题",
        description="能用方程解决简单的实际问题，找出等量关系并列出方程。",
        difficulty=Difficulty.VERY_HARD,
        category="数与运算",
        prerequisites=["math_g5_014"],
        examples=[
            "小明比小红大3岁，两人年龄之和是27岁。设小红x岁，x + (x+3) = 27 → x = 12。",
        ],
        common_mistakes=[
            "找错等量关系。",
            "列方程时把已知量和未知量混用。",
        ],
    ),

    # 6. 多边形的面积
    KnowledgePoint(
        id="math_g5_016", grade=5,
        name="平行四边形的面积",
        description="掌握平行四边形面积公式：S = ah（底×高），理解公式的推导过程。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_014", "math_g3_020"],
        examples=[
            "平行四边形底8cm、高5cm，面积 = 8×5 = 40cm²。",
        ],
        common_mistakes=[
            "用斜边代替高来计算面积。",
            "底和高不对应（底是某条边但高不是该边上的高）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_017", grade=5,
        name="三角形的面积",
        description="掌握三角形面积公式：S = ah÷2（底×高÷2），理解公式推导。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g5_016", "math_g4_035"],
        examples=[
            "三角形底6cm、高4cm，面积 = 6×4÷2 = 12cm²。",
        ],
        common_mistakes=[
            "忘记除以2。",
            "底和高不对应。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_018", grade=5,
        name="梯形的面积",
        description="掌握梯形面积公式：S = (a+b)h÷2（上底+下底）×高÷2。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g5_017", "math_g4_013"],
        examples=[
            "梯形上底3cm、下底7cm、高4cm，面积 = (3+7)×4÷2 = 20cm²。",
        ],
        common_mistakes=[
            "忘记除以2。",
            "上底和下底相加时算错。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_019", grade=5,
        name="组合图形的面积",
        description="能把组合图形分解成基本图形（长方形、三角形、梯形等），计算面积。",
        difficulty=Difficulty.VERY_HARD,
        category="图形与几何",
        prerequisites=["math_g5_016", "math_g5_017", "math_g5_018"],
        examples=[
            "一个L形图形可以分成两个长方形来求面积。",
            "不规则图形可以用割补法转化为基本图形。",
        ],
        common_mistakes=[
            "分解后重复计算或遗漏某部分面积。",
            "分解方法不当导致计算过于复杂。",
        ],
    ),

    # 7. 数学广角─植树问题
    KnowledgePoint(
        id="math_g5_020", grade=5,
        name="植树问题",
        description="掌握三种植树问题的模型：两端都栽、只栽一端、两端不栽，理解棵数与段数的关系。",
        difficulty=Difficulty.HARD,
        category="数学思想",
        prerequisites=["math_g4_020"],
        examples=[
            "100米路，每隔10米栽一棵树。两端都栽：100÷10+1 = 11棵。",
            "只栽一端：100÷10 = 10棵。",
            "两端不栽：100÷10-1 = 9棵。",
        ],
        common_mistakes=[
            "三种模型混淆（多1、不变、少1）。",
            "封闭路线上的植树问题（棵数=段数）忘记单独考虑。",
        ],
    ),

    # ===== 五年级下册 =====

    # 1. 观察物体（三）
    KnowledgePoint(
        id="math_g5_021", grade=5,
        name="观察物体（三）",
        description="能根据从不同方向看到的图形，推断搭成这个物体所需正方体的数量和摆放方式。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g4_022"],
        examples=[
            "从前面看3个正方形，从上面看4个正方形，从右面看2个正方形，推断至少需要几个正方体。",
        ],
        common_mistakes=[
            "只考虑一个方向看到的形状，忽略其他方向。",
            "被遮挡的正方体漏算。",
        ],
    ),

    # 2. 因数与倍数
    KnowledgePoint(
        id="math_g5_022", grade=5,
        name="因数和倍数",
        description="理解因数和倍数的含义，能求一个数的因数和倍数。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g2_004", "math_g2_007"],  # 表内乘除法
        examples=[
            "2 × 3 = 6，所以2和3是6的因数，6是2的倍数也是3的倍数。",
            "12的因数有：1、2、3、4、6、12。",
        ],
        common_mistakes=[
            "忘记1和本身也是因数。",
            "认为因数和倍数的个数是无限的（因数有限，倍数无限）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_023", grade=5,
        name="2、5、3的倍数特征",
        description="掌握2、5、3的倍数特征，理解奇数和偶数的含义。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g5_022"],
        examples=[
            "2的倍数特征：个位是0、2、4、6、8。",
            "5的倍数特征：个位是0或5。",
            "3的倍数特征：各位数字之和是3的倍数。",
        ],
        common_mistakes=[
            "认为3的倍数也看个位。",
            "奇数、偶数与质数、合数混淆。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_024", grade=5,
        name="质数和合数",
        description="理解质数和合数的含义，能判断一个数是质数还是合数，知道1既不是质数也不是合数。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_022"],
        examples=[
            "质数只有1和本身两个因数，如2、3、5、7、11。",
            "合数有3个或更多因数，如4、6、8、9、10。",
            "2是最小的质数，也是唯一的偶质数。",
        ],
        common_mistakes=[
            "认为1是质数。",
            "认为所有奇数都是质数。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_025", grade=5,
        name="最大公因数和最小公倍数",
        description="理解公因数、最大公因数、公倍数、最小公倍数的含义，能用列举法或短除法求解。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_022", "math_g5_024"],
        examples=[
            "12和18的公因数有1、2、3、6，最大公因数是6。",
            "4和6的最小公倍数是12。",
        ],
        common_mistakes=[
            "混淆公因数和公倍数的概念。",
            "短除法中除数选择不当。",
        ],
    ),

    # 3. 长方体和正方体
    KnowledgePoint(
        id="math_g5_026", grade=5,
        name="长方体和正方体的认识",
        description="认识长方体和正方体的特征：面、棱、顶点的数量和性质。",
        difficulty=Difficulty.MEDIUM,
        category="图形与几何",
        prerequisites=["math_g4_032", "math_g3_019"],
        examples=[
            "长方体有6个面、12条棱、8个顶点。",
            "正方体是特殊的长方体（长=宽=高）。",
        ],
        common_mistakes=[
            "认为长方体相邻的面一定不同。",
            "长、宽、高的概念理解不清。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_027", grade=5,
        name="长方体和正方体的表面积",
        description="掌握长方体和正方体表面积的计算方法，能解决实际问题。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g5_026"],
        examples=[
            "长方体表面积 = (长×宽 + 长×高 + 宽×高) × 2",
            "正方体表面积 = 棱长 × 棱长 × 6",
        ],
        common_mistakes=[
            "忘记乘2（只算了三个面的面积）。",
            "实际问题中没有根据具体情况确定需要计算几个面（如无盖鱼缸只算5个面）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_028", grade=5,
        name="体积和体积单位",
        description="理解体积的含义，认识体积单位（cm³、dm³、m³），知道1dm³=1000cm³。",
        difficulty=Difficulty.MEDIUM,
        category="量与计量",
        prerequisites=["math_g5_026"],
        examples=[
            "1立方厘米是一个棱长1cm的正方体的体积。",
            "1立方分米 = 1000立方厘米",
        ],
        common_mistakes=[
            "体积单位和面积单位混淆。",
            "相邻体积单位间的进率是1000（不是100）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_029", grade=5,
        name="长方体和正方体的体积",
        description="掌握长方体体积=长×宽×高，正方体体积=棱长×棱长×棱长，能用V=Sh计算。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g5_028", "math_g5_026"],
        examples=[
            "长方体长5cm、宽4cm、高3cm，体积 = 5×4×3 = 60cm³。",
            "正方体棱长6cm，体积 = 6³ = 216cm³。",
        ],
        common_mistakes=[
            "体积和表面积公式混淆。",
            "计算时忘记某个维度的数据。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_030", grade=5,
        name="体积单位间的进率与换算",
        description="掌握体积单位间的进率（1m³=1000dm³，1dm³=1000cm³）和容积单位（L、mL）。",
        difficulty=Difficulty.HARD,
        category="量与计量",
        prerequisites=["math_g5_028"],
        examples=[
            "1立方米 = 1000立方分米",
            "1升 = 1立方分米 = 1000毫升",
        ],
        common_mistakes=[
            "体积和容积单位之间换算出错。",
            "把1L = 1dm³ 记成 1L = 1cm³。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_031", grade=5,
        name="不规则物体的体积",
        description="能用排水法等方法测量不规则物体的体积。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g5_029"],
        examples=[
            "量杯中放入石块前水位200mL，放入后水位350mL，石块体积 = 350 - 200 = 150mL = 150cm³。",
        ],
        common_mistakes=[
            "忘记单位换算（mL到cm³）。",
            "水面没有完全浸没物体。",
        ],
    ),

    # 4. 分数的意义和性质
    KnowledgePoint(
        id="math_g5_032", grade=5,
        name="分数的意义",
        description='进一步理解分数的意义：把单位"1"平均分成若干份，表示其中一份或几份的数。',
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g3_021", "math_g3_022"],
        examples=[
            "把单位『1』平均分成5份，取其中3份，就是3/5。",
            "分数单位：3/5的分数单位是1/5。",
        ],
        common_mistakes=[
            "单位『1』和数字1混淆。",
            "没有平均分也用分数表示。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_033", grade=5,
        name="真分数和假分数",
        description="认识真分数（分子<分母）和假分数（分子≥分母），能将假分数化为带分数。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_032"],
        examples=[
            "3/4是真分数（小于1）。",
            "7/4是假分数（大于1），化为带分数：1又3/4。",
        ],
        common_mistakes=[
            "认为假分数没有意义。",
            "带分数和假分数互化时出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_034", grade=5,
        name="分数的基本性质",
        description="理解分数的基本性质：分子和分母同时乘或除以相同的数（0除外），分数大小不变。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_032"],
        examples=[
            "2/3 = 4/6 = 6/9 = 8/12",
            "12/18 = 6/9 = 2/3",
        ],
        common_mistakes=[
            "分子和分母没有同时变化。",
            "分子分母同时加减（而非乘除）。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_035", grade=5,
        name="约分",
        description="理解最简分数的含义，能将分数约分为最简分数。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_034", "math_g5_025"],
        examples=[
            "12/18 = (12÷6)/(18÷6) = 2/3",
            "约分时通常除以分子分母的最大公因数。",
        ],
        common_mistakes=[
            "没有约到最简（如把12/18约成6/9就停了）。",
            "约分时分子分母除以不同的数。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_036", grade=5,
        name="通分",
        description="理解通分的含义，能把异分母分数通分为同分母分数，比较异分母分数的大小。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_034", "math_g5_025"],
        examples=[
            "比较3/4和5/6：通分为9/12和10/12，所以3/4 < 5/6。",
        ],
        common_mistakes=[
            "通分后分子没有相应变化。",
            "公分母不是最小公倍数导致计算复杂。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_037", grade=5,
        name="分数和小数的互化",
        description="能将分数化成小数（用分子÷分母），能将小数化成分数。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_034", "math_g4_027", "math_g5_007"],
        examples=[
            "3/4 = 3÷4 = 0.75",
            "0.35 = 35/100 = 7/20",
        ],
        common_mistakes=[
            "分数化小数时除法计算出错。",
            "小数化分数后没有约分。",
        ],
    ),

    # 5. 图形的运动（三）
    KnowledgePoint(
        id="math_g5_038", grade=5,
        name="旋转",
        description="进一步认识旋转（绕点、方向、角度），能在方格纸上画出旋转后的图形。",
        difficulty=Difficulty.HARD,
        category="图形与几何",
        prerequisites=["math_g4_039", "math_g4_006"],
        examples=[
            "把三角形绕O点顺时针旋转90°。",
            "旋转三要素：旋转中心、旋转方向、旋转角度。",
        ],
        common_mistakes=[
            "旋转中心找错。",
            "顺时针和逆时针方向搞反。",
        ],
    ),

    # 6. 分数的加法和减法
    KnowledgePoint(
        id="math_g5_039", grade=5,
        name="同分母分数加减法",
        description="掌握同分母分数加减法：分母不变，分子相加减。",
        difficulty=Difficulty.EASY,
        category="数与运算",
        prerequisites=["math_g5_032"],
        examples=[
            "3/7 + 2/7 = 5/7",
            "5/8 - 1/8 = 4/8 = 1/2",
        ],
        common_mistakes=[
            "分母也相加（3/7+2/7=5/14，错误）。",
            "结果没有化简。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_040", grade=5,
        name="异分母分数加减法",
        description="掌握异分母分数加减法：先通分，再按同分母加减法计算。",
        difficulty=Difficulty.HARD,
        category="数与运算",
        prerequisites=["math_g5_039", "math_g5_036"],
        examples=[
            "1/3 + 1/4 = 4/12 + 3/12 = 7/12",
            "5/6 - 3/8 = 20/24 - 9/24 = 11/24",
        ],
        common_mistakes=[
            "没有通分直接加减分子和分母。",
            "通分后分子计算出错。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_041", grade=5,
        name="分数加减混合运算",
        description="能进行分数加减混合运算，能运用运算定律进行简便计算。",
        difficulty=Difficulty.VERY_HARD,
        category="数与运算",
        prerequisites=["math_g5_040", "math_g4_023"],
        examples=[
            "1/2 + 1/3 + 1/6 = 3/6 + 2/6 + 1/6 = 6/6 = 1",
            "5/6 - 1/4 - 1/3 = 5/6 - (3/12 + 4/12) = 10/12 - 7/12 = 3/12 = 1/4",
        ],
        common_mistakes=[
            "混合运算中通分不彻底。",
            "运算顺序出错。",
        ],
    ),

    # 7. 折线统计图
    KnowledgePoint(
        id="math_g5_042", grade=5,
        name="折线统计图",
        description="认识折线统计图，能读懂单式和复式折线统计图，能绘制折线统计图。",
        difficulty=Difficulty.MEDIUM,
        category="统计与概率",
        prerequisites=["math_g4_018"],
        examples=[
            "折线统计图能清楚地反映数据的变化趋势。",
            "复式折线统计图可以比较两组数据的变化趋势。",
        ],
        common_mistakes=[
            "纵轴刻度不均匀导致折线变形。",
            "忘记标注图例。",
        ],
    ),

    # 8. 数学广角—找次品
    KnowledgePoint(
        id="math_g5_043", grade=5,
        name="找次品问题",
        description='能用天平称量的策略找次品，理解"三分法"是最优策略。',
        difficulty=Difficulty.EXPERT,
        category="数学思想",
        prerequisites=["math_g5_025"],
        examples=[
            "9个物品中有一个次品较轻，用天平最少称2次就能找出。分成(3,3,3)，第一次称两组3个。",
            "n个物品中找1个次品，称量次数 = ⌈log₃n⌉。",
        ],
        common_mistakes=[
            "分成两组而非三组，导致称量次数增多。",
            "认为每次称量只能比较2个物品。",
        ],
    ),

    # 额外补充五年级综合知识点
    KnowledgePoint(
        id="math_g5_044", grade=5,
        name="用公因数和公倍数解决实际问题",
        description="能用最大公因数和最小公倍数解决铺地砖、分东西等实际问题。",
        difficulty=Difficulty.VERY_HARD,
        category="数与运算",
        prerequisites=["math_g5_025"],
        examples=[
            "用长4cm、宽3cm的长方形瓷砖铺正方形地面，至少需要几块？最小公倍数12，12÷4×12÷3 = 12块。",
            "把12个苹果和16个橘子平均分给小朋友，最多分给几人？最大公因数4。",
        ],
        common_mistakes=[
            "不知道该用最大公因数还是最小公倍数。",
            "计算总数时忘记除以单个瓷砖的面积。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_045", grade=5,
        name="分数与除法的关系",
        description="理解分数与除法的关系：a÷b = a/b（b≠0），能利用这个关系解决问题。",
        difficulty=Difficulty.MEDIUM,
        category="数与运算",
        prerequisites=["math_g5_032"],
        examples=[
            "把3米长的绳子平均分成5段，每段长3÷5 = 3/5米。",
            "1÷4 = 1/4",
        ],
        common_mistakes=[
            "把『每份是多少』和『是整体的几分之几』混淆。",
            "分子和分母的位置写反。",
        ],
    ),
    KnowledgePoint(
        id="math_g5_046", grade=5,
        name="打电话问题（优化）",
        description="用指数增长的思想解决打电话通知等优化问题。",
        difficulty=Difficulty.HARD,
        category="数学思想",
        prerequisites=["math_g4_019"],
        examples=[
            "每分钟每人通知1人，n分钟最多通知2ⁿ-1人。",
            "5分钟最多通知31人。",
        ],
        common_mistakes=[
            "用加法思维（1+1+1...）而非指数思维（1,2,4,8...）。",
            "忘记减去最开始的那个人（2ⁿ-1中的-1）。",
        ],
    ),
]


# ─────────────────────────────────────────────
# 合并与查询函数
# ─────────────────────────────────────────────

ALL_POINTS: List[KnowledgePoint] = GRADE_3_POINTS + GRADE_4_POINTS + GRADE_5_POINTS

# 构建 ID → KnowledgePoint 索引
_POINT_INDEX = {p.id: p for p in ALL_POINTS}


def get_point_by_id(point_id: str) -> Optional[KnowledgePoint]:
    """根据知识点 ID 查找知识点。"""
    return _POINT_INDEX.get(point_id)


def get_points_by_grade(grade: int) -> List[KnowledgePoint]:
    """获取指定年级的所有知识点。"""
    return [p for p in ALL_POINTS if p.grade == grade]


def get_points_by_difficulty(difficulty: Difficulty) -> List[KnowledgePoint]:
    """获取指定难度的所有知识点。"""
    return [p for p in ALL_POINTS if p.difficulty == difficulty]
