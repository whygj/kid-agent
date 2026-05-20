"""
人教版八年级、九年级数学知识点数据
Chinese Mathematics Curriculum - Grade 8 & Grade 9 Knowledge Points
(PEP / 人教版)
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
    name: str
    grade: int
    subject: str = "数学"
    difficulty: Difficulty = Difficulty.MEDIUM
    prerequisites: List[str] = field(default_factory=list)
    description: str = ""
    examples: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────
# 八年级上册 (Grade 8, Volume 1)
# ──────────────────────────────────────────────

# 第十一章 三角形

GRADE_8_POINTS: List[KnowledgePoint] = [

    KnowledgePoint(
        id="math_g8_001",
        name="三角形的边",
        grade=8,
        difficulty=Difficulty.EASY,
        prerequisites=["math_g7_001", "math_g7_003"],
        description="理解三角形的概念，掌握三角形三边关系：任意两边之和大于第三边，任意两边之差小于第三边。能根据边长判断三条线段能否组成三角形。",
        examples=[
            "判断边长 3、4、8 能否组成三角形（不能，因为 3+4=7 < 8）",
            "已知三角形两边长为 5 和 9，求第三边 a 的取值范围（4 < a < 14）",
            "等腰三角形两边长为 4 和 9，求周长（22）",
        ],
        common_mistakes=[
            "忘记验证所有三组两边之和，只验证一组就下结论",
            "等腰三角形中未讨论哪条边是腰，导致漏解或多解",
            "混淆'两边之和大于第三边'与'两边之差小于第三边'的等价表述",
        ],
    ),

    KnowledgePoint(
        id="math_g8_002",
        name="三角形的高、中线与角平分线",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_001"],
        description="理解三角形的高、中线、角平分线的概念，能正确画出各种三角形（锐角、直角、钝角）的三条高、三条中线和三条角平分线。三角形的三条中线交于重心。",
        examples=[
            "画锐角三角形 ABC 的三条高，说明高的位置在三角形内部",
            "画钝角三角形的三条高，说明有两条高在三角形外部",
            "三角形一边上的中线将原三角形分成面积相等的两个三角形",
        ],
        common_mistakes=[
            "钝角三角形的高画在三角形内部而非延长线上",
            "混淆高和中线的定义：高是到对边所在直线的垂线段，中线是到对边中点的线段",
            "认为三角形的高一定在三角形内部",
        ],
    ),

    KnowledgePoint(
        id="math_g8_003",
        name="三角形的内角和",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_003", "math_g8_001"],
        description="掌握三角形内角和定理：三角形三个内角的和等于 180°。能用平行线的性质证明三角形内角和定理。能解决与三角形内角有关的计算问题。",
        examples=[
            "在三角形 ABC 中，∠A=50°，∠B=70°，求 ∠C（60°）",
            "证明：直角三角形的两个锐角互余",
            "在三角形中，最大角等于最小角的 2 倍，最大角比第三个角大 20°，求三个角",
        ],
        common_mistakes=[
            "求角时忘记三角形内角和为 180°，把条件列成不等式或遗漏条件",
            "外角等于不相邻两内角之和，容易误认为等于相邻内角之和",
            "多个三角形组合时，公共角的等量关系遗漏",
        ],
    ),

    KnowledgePoint(
        id="math_g8_004",
        name="三角形的外角",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_003"],
        description="理解三角形外角的概念。掌握三角形外角的性质：三角形的一个外角等于与它不相邻的两个内角的和；三角形的一个外角大于任何一个与它不相邻的内角。",
        examples=[
            "三角形 ABC 中，∠A=40°，∠B=60°，求 ∠ACB 的外角（80°）",
            "利用外角定理证明：三角形的外角和等于 360°",
            "在三角形中，一个外角为 120°，其中一个不相邻内角为 45°，求另一个不相邻内角（75°）",
        ],
        common_mistakes=[
            "混淆'外角等于不相邻两内角之和'与'外角等于相邻内角'的错误关系",
            "认为外角一定大于所有内角（实际只大于不相邻的内角）",
            "在画外角时只画了一个方向的外角，遗漏另一个方向",
        ],
    ),

    KnowledgePoint(
        id="math_g8_005",
        name="多边形及其内角和",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_003"],
        description="理解多边形的概念，掌握多边形内角和公式：(n-2)×180°。掌握多边形外角和等于 360°（与边数无关）。能根据内角和反求多边形边数。",
        examples=[
            "求八边形的内角和（(8-2)×180°=1080°）",
            "已知多边形内角和为 1260°，求边数（9）",
            "求正六边形每个内角的度数（120°）",
        ],
        common_mistakes=[
            "内角和公式记错为 n×180° 或 (n-1)×180°",
            "正 n 边形每个内角 = (n-2)×180°/n，计算时忘记除以 n",
            "外角和恒等于 360°，误以为外角和也与边数有关",
        ],
    ),

    # 第十二章 全等三角形

    KnowledgePoint(
        id="math_g8_006",
        name="全等三角形的概念与性质",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_001", "math_g8_003"],
        description="理解全等三角形的概念，掌握全等三角形的性质：全等三角形的对应边相等，对应角相等。能正确表示两个全等三角形并找出对应元素。",
        examples=[
            "△ABC≅△DEF，AB=5，BC=7，AC=8，求 DE、EF、FD 的长",
            "已知 △ABC≅△BAD，找出对应边和对应角",
            "利用全等三角形的对应关系求未知角或边",
        ],
        common_mistakes=[
            "书写全等式时对应顶点的顺序不对，导致找错对应边和对应角",
            "混淆对应边与公共边的关系",
            "全等符号 ≅ 和相似符号 ∽ 混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g8_007",
        name="全等三角形的判定（SSS/SAS/ASA/AAS/HL）",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_006"],
        description="掌握全等三角形的五种判定方法：SSS（三边）、SAS（两边及其夹角）、ASA（两角及其夹边）、AAS（两角及其中一角的对边）、HL（直角三角形的斜边和一直角边）。能根据已知条件选择合适的判定方法证明三角形全等。",
        examples=[
            "已知 AB=DE，∠A=∠D，AC=DF，用 SAS 判定 △ABC≅△DEF",
            "已知 ∠B=∠E，∠C=∠F，BC=EF，用 ASA 判定 △ABC≅△DEF",
            "Rt△ABC 和 Rt△DEF 中，AB=DE=5，AC=DF=3，用 HL 判定全等",
        ],
        common_mistakes=[
            "用 SSA（两边及其中一边的对角）判定全等——这是错误的，SSA 不能判定全等",
            "SAS 中夹角条件不满足（不是两已知边的夹角）就误判为全等",
            "HL 定理只适用于直角三角形，在一般三角形中不能使用",
            "证明时未声明公共边或公共角就默认使用",
        ],
    ),

    KnowledgePoint(
        id="math_g8_008",
        name="角的平分线的性质",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_007"],
        description="掌握角平分线的性质定理：角平分线上的点到角两边的距离相等。掌握角平分线的判定定理：到角两边距离相等的点在角的平分线上。能利用全等三角形证明角平分线的性质。",
        examples=[
            "OC 是 ∠AOB 的平分线，P 是 OC 上一点，PE⊥OA 于 E，PF⊥OB 于 F，求证 PE=PF",
            "在 ∠AOB 内部一点 P，到 OA 的距离为 3，到 OB 的距离为 3，求证 P 在角平分线上",
            "利用角平分线性质求三角形内角平分线分对边之比",
        ],
        common_mistakes=[
            "使用角平分线性质时忘记验证'点到两边的距离'即垂直条件",
            "混淆'角平分线上的点'与'到两边距离相等的点'的因果方向",
            "角平分线性质中'距离'指垂线段长度，误用斜线段代替",
        ],
    ),

    # 第十三章 轴对称

    KnowledgePoint(
        id="math_g8_009",
        name="轴对称与轴对称图形",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_003"],
        description="理解轴对称和轴对称图形的概念，能识别轴对称图形并找出对称轴。掌握轴对称的性质：对应点连线被对称轴垂直平分，对应线段相等，对应角相等。",
        examples=[
            "判断正三角形、正方形、圆分别有几条对称轴",
            "画出点 A 关于直线 l 的对称点 A'",
            "在坐标系中画 △ABC 关于 y 轴的对称图形",
        ],
        common_mistakes=[
            "混淆轴对称（两个图形的关系）与轴对称图形（一个图形的性质）",
            "找对称轴时遗漏（如正三角形有 3 条，不是 1 条）",
            "坐标系中关于 y 轴对称时只改变 x 的符号，误将 y 也改变",
        ],
    ),

    KnowledgePoint(
        id="math_g8_010",
        name="线段的垂直平分线",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_009"],
        description="理解线段垂直平分线的概念。掌握线段垂直平分线的性质：线段垂直平分线上的点到线段两端点的距离相等。掌握其判定：到线段两端点距离相等的点在线段的垂直平分线上。",
        examples=[
            "已知 AB 的垂直平分线上的点 P 到 A 的距离为 5，求 P 到 B 的距离（5）",
            "在三角形 ABC 中，AB 的垂直平分线交 AC 于 D，已知 AD=3，BC=7，求 △BDC 的周长与 AC 的关系",
            "用尺规作图作线段的垂直平分线",
        ],
        common_mistakes=[
            "混淆垂直平分线性质与角平分线性质的使用场景",
            "在三角形中利用垂直平分线转移线段时遗漏等量关系",
            "作垂直平分线时圆规半径不够大导致交点找不到",
        ],
    ),

    KnowledgePoint(
        id="math_g8_011",
        name="等腰三角形",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_009", "math_g8_007"],
        description="掌握等腰三角形的性质：等边对等角（两个底角相等）；等腰三角形的顶角平分线、底边上的中线、底边上的高互相重合（三线合一）。掌握等腰三角形的判定：等角对等边。理解等边三角形（三线合一的特例）。",
        examples=[
            "等腰三角形的一个角为 80°，求其余两个角（80°、20° 或 50°、50°）",
            "已知等腰三角形一腰上的中线将周长分为 15 和 12 两部分，求各边长",
            "证明：等腰三角形两底角的平分线相等",
        ],
        common_mistakes=[
            "已知一个角时未分情况讨论（该角是顶角还是底角），导致漏解",
            "三线合一的前提是必须是等腰三角形，底边上的线才能三线合一",
            "等腰三角形的腰和中线、高、角平分线混在一起，计算时弄不清已知量",
        ],
    ),

    # 第十四章 整式的乘法与因式分解

    KnowledgePoint(
        id="math_g8_012",
        name="幂的运算",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_010"],
        description="掌握幂的运算法则：同底数幂相乘（aᵐ·aⁿ=aᵐ⁺ⁿ）、幂的乘方（(aᵐ)ⁿ=aᵐⁿ）、积的乘方（(ab)ⁿ=aⁿbⁿ）、同底数幂相除（aᵐ÷aⁿ=aᵐ⁻ⁿ，a≠0）。理解零指数幂和负整数指数幂的意义。",
        examples=[
            "计算 x³·x⁵（x⁸）",
            "计算 (a²b³)²（a⁴b⁶）",
            "计算 2⁰ + (−1)⁻²（1+1=2）",
        ],
        common_mistakes=[
            "混淆 aᵐ·aⁿ=aᵐ⁺ⁿ（指数相加）与 (aᵐ)ⁿ=aᵐⁿ（指数相乘）",
            "同底数幂相除时 aᵐ÷aⁿ 的指数计算错误为 aᵐÿⁿ",
            "负整数指数幂 a⁻ⁿ=1/aⁿ 的计算出错，忘记取倒数",
            "零指数幂 a⁰=1 的前提是 a≠0",
        ],
    ),

    KnowledgePoint(
        id="math_g8_013",
        name="整式的乘法",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_012"],
        description="掌握单项式乘单项式、单项式乘多项式、多项式乘多项式的运算法则。能正确进行整式的乘法运算。",
        examples=[
            "计算 (2x²y)(−3xy³)（−6x³y⁴）",
            "计算 2x(3x²−4x+1)（6x³−8x²+2x）",
            "计算 (x+2)(x−3)（x²−x−6）",
        ],
        common_mistakes=[
            "多项式乘多项式时漏项，尤其交叉相乘时遗漏某些项",
            "合并同类项时系数计算错误或忘记合并",
            "符号处理不当：负号分配时漏掉某些项",
        ],
    ),

    KnowledgePoint(
        id="math_g8_014",
        name="乘法公式（平方差与完全平方）",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_013"],
        description="掌握平方差公式 (a+b)(a−b)=a²−b² 和完全平方公式 (a±b)²=a²±2ab+b²。能灵活运用乘法公式简化计算。",
        examples=[
            "计算 (2x+3)(2x−3)（4x²−9）",
            "计算 (x+5)²（x²+10x+25）",
            "用乘法公式简便计算 101²−99²（400）",
        ],
        common_mistakes=[
            "完全平方公式忘记中间项 2ab，写成 (a+b)²=a²+b²",
            "平方差公式中两个因式的符号判断错误",
            "(a−b)²=a²−2ab+b² 中间项符号弄错",
            "将 (a+b)² 与 a²+b² 混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g8_015",
        name="因式分解",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_013", "math_g8_014"],
        description="理解因式分解与整式乘法的关系（互逆运算）。掌握因式分解的基本方法：提公因式法、公式法（平方差公式、完全平方公式）。能综合运用多种方法进行因式分解。",
        examples=[
            "因式分解 6x²y−3xy（3xy(2x−1)）",
            "因式分解 x²−9（(x+3)(x−3)）",
            "因式分解 x²+6x+9（(x+3)²）",
            "因式分解 2x²−8（2(x+2)(x−2)）",
        ],
        common_mistakes=[
            "因式分解不彻底，如 x⁴−16 只分解到 (x²+4)(x²−4) 而未继续分解 x²−4",
            "忘记先提公因式就直接用公式法",
            "混淆因式分解与整式乘法，分解后又展开回去",
            "提公因式后括号内未化简",
        ],
    ),

    # 第十五章 分式

    KnowledgePoint(
        id="math_g8_016",
        name="分式的概念与基本性质",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_010", "math_g8_012"],
        description="理解分式的概念：形如 A/B（B 中含有字母）的式子。掌握分式有意义的条件（分母不为 0）和分式值为 0 的条件（分子为 0 且分母不为 0）。掌握分式的基本性质：分式的分子分母同乘（或除以）同一个不为 0 的整式，分式的值不变。",
        examples=[
            "当 x 取何值时，分式 (x−2)/(x+3) 有意义（x≠−3）",
            "当 x 取何值时，分式 (x²−4)/(x−2) 的值为 0（x=−2）",
            "利用分式的基本性质约分 (6x²y)/(9xy²)（2x/(3y)）",
        ],
        common_mistakes=[
            "求分式值为 0 时只考虑分子为 0，忘记验证分母不为 0",
            "约分时对分子分母是多项式的情况忘记先因式分解再约分",
            "分式的分母不能为 0 这一隐含条件在解题中被忽略",
        ],
    ),

    KnowledgePoint(
        id="math_g8_017",
        name="分式的运算",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_016", "math_g8_015"],
        description="掌握分式的加减乘除运算法则。能进行分式的加减（通分后加减）、乘除（约分后乘除）。掌握混合运算的顺序。",
        examples=[
            "计算 1/(x+1) + 1/(x−1)（2x/(x²−1)）",
            "计算 (x²−4)/(x+2) × 1/(x−2)（1）",
            "计算 (a/b − c/d)（(ad−bc)/(bd)）",
        ],
        common_mistakes=[
            "异分母分式加减时忘记通分直接加减分子分母",
            "分式乘除时混淆：除以一个分式等于乘以它的倒数",
            "分式运算结果未化到最简",
            "混合运算时运算顺序错误",
        ],
    ),

    KnowledgePoint(
        id="math_g8_018",
        name="分式方程",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_017", "math_g7_012"],
        description="理解分式方程的概念。掌握分式方程的解法：去分母化为整式方程，解整式方程，验根（必须验证）。能列分式方程解应用题。",
        examples=[
            "解方程 2/(x−1) = 3/(x+1)（x=5）",
            "解方程 1/(x−2) + 3 = (1−x)/(2−x)（解出 x 后需验根）",
            "甲乙两人加工同样多的零件，甲每小时比乙多加工 10 个，甲用 6 小时，乙用 8 小时，求各自的效率",
        ],
        common_mistakes=[
            "解分式方程后忘记验根（增根问题），导致取到使分母为 0 的解",
            "去分母时漏乘某些项（尤其是常数项）",
            "列分式方程解应用题时设未知量不当或等量关系找错",
        ],
    ),

    # ──────────────────────────────────────────────
    # 八年级下册 (Grade 8, Volume 2)
    # ──────────────────────────────────────────────

    # 第十六章 二次根式

    KnowledgePoint(
        id="math_g8_019",
        name="二次根式的概念与性质",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_004"],
        description="理解二次根式的概念：形如 √a（a≥0）的式子。掌握二次根式的性质：√a≥0（a≥0）；(√a)²=a（a≥0）；√(a²)=|a|。理解最简二次根式的概念。",
        examples=[
            "求 √(x−3) 中 x 的取值范围（x≥3）",
            "计算 (√5)²（5）",
            "化简 √(−3)²（3）",
        ],
        common_mistakes=[
            "混淆 √(a²)=|a| 与 √(a²)=a（当 a 可能为负时忘记加绝对值）",
            "二次根式有意义的条件是被开方数非负，忘记这一限制",
            "化简 √(a²) 时不考虑 a 的正负性",
        ],
    ),

    KnowledgePoint(
        id="math_g8_020",
        name="二次根式的乘除与加减",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_019"],
        description="掌握二次根式的乘法 √a·√b=√(ab)（a≥0,b≥0）和除法 √a/√b=√(a/b)（a≥0,b>0）。掌握二次根式的加减：先化简为最简二次根式，再合并同类二次根式。掌握分母有理化。",
        examples=[
            "计算 √6×√3（3√2）",
            "计算 √8+√18−√32（3√2−4√2+3√2=2√2）",
            "分母有理化 1/(√3+√2)（√3−√2）",
        ],
        common_mistakes=[
            "二次根式加减时未化到最简就尝试合并",
            "不是同类二次根式强行合并（如 √2+√3≠√5）",
            "分母有理化时分子漏乘有理化因式",
            "√a+√b=√(a+b) 是错误运算",
        ],
    ),

    # 第十七章 勾股定理

    KnowledgePoint(
        id="math_g8_021",
        name="勾股定理",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_001", "math_g8_020"],
        description="掌握勾股定理：直角三角形两直角边的平方和等于斜边的平方，即 a²+b²=c²。能用勾股定理在已知直角三角形两边的情况下求第三边。能应用勾股定理解决实际问题。",
        examples=[
            "直角三角形两直角边为 3 和 4，求斜边（5）",
            "直角三角形斜边为 13，一直角边为 5，求另一直角边（12）",
            "一个梯子长 10 米靠在墙上，梯子底端距墙 6 米，梯子顶端距地面多高（8 米）",
        ],
        common_mistakes=[
            "勾股定理中 a²+b²=c² 的 c 必须是斜边（最长边），将直角边当作斜边代入",
            "列方程时忘记开方，如算出 c²=25 后答案写 25 而非 5",
            "实际问题中未判断是否为直角三角形就直接用勾股定理",
        ],
    ),

    KnowledgePoint(
        id="math_g8_022",
        name="勾股定理的逆定理",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_021"],
        description="掌握勾股定理的逆定理：如果三角形的三边 a、b、c 满足 a²+b²=c²，那么这个三角形是直角三角形。能利用逆定理判断三角形是否为直角三角形。了解常见的勾股数组。",
        examples=[
            "判断边长为 5、12、13 的三角形是否为直角三角形（5²+12²=169=13²，是）",
            "判断边长为 4、5、6 的三角形是否为直角三角形（16+25=41≠36，不是）",
            "已知三角形三边为 n²−1、2n、n²+1，证明它是直角三角形",
        ],
        common_mistakes=[
            "验证时未将最长边的平方放在等式右边（c² 的位置）",
            "计算平方时出错导致错误判断",
            "混淆勾股定理（已知直角求边）和逆定理（已知边判断直角）",
        ],
    ),

    # 第十八章 平行四边形

    KnowledgePoint(
        id="math_g8_023",
        name="平行四边形的性质与判定",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g7_003", "math_g8_007"],
        description="掌握平行四边形的性质：对边平行且相等、对角相等、邻角互补、对角线互相平分。掌握平行四边形的判定方法：两组对边分别平行；两组对边分别相等；一组对边平行且相等；对角线互相平分；两组对角分别相等。",
        examples=[
            "平行四边形 ABCD 中，∠A=70°，求其余三个角（110°、70°、110°）",
            "四边形 ABCD 中，AB∥CD 且 AB=CD，求证 ABCD 为平行四边形",
            "平行四边形两对角线长为 10 和 14，一边长为 6，求另一边长（10）",
        ],
        common_mistakes=[
            "混淆性质和判定的使用场景：性质用于已知是平行四边形时推导结论，判定用于证明是平行四边形",
            "一组对边平行且一组对边相等不能判定平行四边形（可能是等腰梯形）",
            "利用对角线性质时忘记'互相平分'不是'相等'",
        ],
    ),

    KnowledgePoint(
        id="math_g8_024",
        name="矩形、菱形、正方形",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_023"],
        description="理解特殊平行四边形的定义和性质：矩形（有一个角是直角的平行四边形，对角线相等）、菱形（有一组邻边相等的平行四边形，对角线互相垂直）、正方形（既是矩形又是菱形）。掌握它们之间的包含关系和各自的判定方法。",
        examples=[
            "矩形 ABCD 的对角线 AC=10，AB=6，求 BC（8）",
            "菱形 ABCD 的对角线 AC=8，BD=6，求菱形面积（24）和边长（5）",
            "正方形对角线长为 8，求面积（32）",
        ],
        common_mistakes=[
            "混淆矩形和菱形的性质：矩形是'对角线相等'，菱形是'对角线互相垂直'",
            "菱形面积公式 = 对角线之积/2，误用底乘高以外的错误公式",
            "正方形是特殊的矩形和菱形，判断条件时过多或过少",
        ],
    ),

    # 第十九章 一次函数

    KnowledgePoint(
        id="math_g8_025",
        name="函数的概念",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_010"],
        description="理解函数的概念：在一个变化过程中，如果有两个变量 x 和 y，对于 x 的每一个确定的值，y 都有唯一确定的值与之对应。理解自变量、因变量的概念。能确定函数自变量的取值范围。",
        examples=[
            "y=2x+1 中，当 x=3 时，y=7",
            "求函数 y=√(x−2) 中自变量 x 的取值范围（x≥2）",
            "一辆汽车以 60 km/h 的速度行驶，路程 s 与时间 t 的函数关系为 s=60t",
        ],
        common_mistakes=[
            "函数关系中自变量的取值范围忘记考虑实际意义",
            "混淆函数解析式中的自变量和因变量",
            "函数图像上点的坐标与函数值之间的对应关系理解不清",
        ],
    ),

    KnowledgePoint(
        id="math_g8_026",
        name="一次函数的图象与性质",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_025"],
        description="理解正比例函数 y=kx 和一次函数 y=kx+b 的概念。掌握一次函数图象是一条直线。理解 k 和 b 对图象的影响：k>0 时 y 随 x 增大而增大，k<0 时 y 随 x 增大而减小；b>0 图象与 y 轴交于正半轴，b<0 交于负半轴。",
        examples=[
            "画函数 y=2x−1 的图象，说明 k=2>0，y 随 x 增大而增大",
            "一次函数 y=−3x+4 的图象经过哪些象限（一、二、四象限）",
            "求直线 y=2x+3 与 x 轴、y 轴的交点坐标",
        ],
        common_mistakes=[
            "由 k 的正负判断增减性时搞反方向",
            "画图象时只取一个点就画线，至少需要两个点",
            "混淆直线与坐标轴交点的求法：令 y=0 求 x 轴交点，令 x=0 求 y 轴交点",
        ],
    ),

    KnowledgePoint(
        id="math_g8_027",
        name="一次函数与方程、不等式",
        grade=8,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_026", "math_g7_012"],
        description="理解一次函数与一元一次方程的关系：y=kx+b 的图象与 x 轴交点的横坐标即 kx+b=0 的解。理解一次函数与一元一次不等式的关系：y=kx+b 的图象在 x 轴上方（或下方）对应的 x 的范围即不等式的解集。能利用一次函数解决实际问题。",
        examples=[
            "利用 y=2x−6 的图象解方程 2x−6=0（x=3）",
            "利用图象解不等式 2x−6>0（x>3）",
            "用一次函数建模选择方案问题：比较两种收费方案",
        ],
        common_mistakes=[
            "不理解函数图象与方程解的对应关系",
            "从图象上读不等式解集时搞错不等号方向",
            "实际应用问题中自变量取值范围忽略实际约束（如非负整数等）",
        ],
    ),

    # 第二十章 数据的分析

    KnowledgePoint(
        id="math_g8_028",
        name="平均数、中位数与众数",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_014"],
        description="掌握算术平均数、加权平均数、中位数、众数的概念和计算方法。理解它们各自的特点和适用场景。能选择合适的统计量描述数据的集中趋势。",
        examples=[
            "数据 3、5、5、7、8 的平均数（5.6）、中位数（5）、众数（5）",
            "某学生语数外成绩分别为 90、85、92，各科权重为 3、3、4，求加权平均分（89.1）",
            "5 个人工资为 3000、3000、3500、4000、15000，分析用平均数还是中位数描述更合理",
        ],
        common_mistakes=[
            "求中位数时忘记先将数据排序",
            "加权平均数计算时忘记乘以权重或忘记除以权重总和",
            "数据个数为偶数时中位数取中间两数的平均值，直接取一个数",
            "对含有异常值的数据使用平均数描述不够合理，应考虑中位数",
        ],
    ),

    KnowledgePoint(
        id="math_g8_029",
        name="方差与数据的波动",
        grade=8,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_028"],
        description="理解方差的概念：各数据与平均数之差的平方的平均值。掌握方差的计算公式。理解方差的意义：方差越大，数据的波动越大，越不稳定。能用方差比较两组数据的稳定性。",
        examples=[
            "数据 2、4、6、8、10 的方差（8）",
            "甲乙两组数据的平均数相同，方差分别为 3 和 7，哪组数据更稳定（甲组）",
            "五次测验成绩分别为 78、82、80、85、75，求方差（12）",
        ],
        common_mistakes=[
            "方差计算时忘记除以数据个数 n，或错误除以 n−1",
            "认为方差越小越好，忽略实际情境中有时需要一定的波动",
            "比较两组数据稳定性时忘记先确认平均数是否相同或接近",
        ],
    ),
]

# ──────────────────────────────────────────────
# 九年级上册 (Grade 9, Volume 1)
# ──────────────────────────────────────────────

# 第二十一章 一元二次方程

GRADE_9_POINTS: List[KnowledgePoint] = [

    KnowledgePoint(
        id="math_g9_001",
        name="一元二次方程的概念",
        grade=9,
        difficulty=Difficulty.EASY,
        prerequisites=["math_g7_012", "math_g8_012"],
        description="理解一元二次方程的概念：只含有一个未知数，且未知数的最高次数为 2 的整式方程。掌握一元二次方程的一般形式 ax²+bx+c=0（a≠0）。能识别二次项、一次项、常数项及对应系数。",
        examples=[
            "判断 x²+2x−3=0 是一元二次方程并指出 a=1、b=2、c=−3",
            "方程 (x−1)(x+2)=3 化为一般形式（x²+x−5=0）",
            "关于 x 的方程 (m−1)x²+2x−3=0，当 m≠1 时为一元二次方程",
        ],
        common_mistakes=[
            "忘记验证 a≠0 的条件，尤其在含参数的一元二次方程中",
            "化一般形式时展开计算出错导致系数错误",
            "混淆一元二次方程和一元一次方程的区别",
        ],
    ),

    KnowledgePoint(
        id="math_g9_002",
        name="配方法解一元二次方程",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_001", "math_g8_014"],
        description="掌握配方法解一元二次方程的步骤：将方程化为 x²+px+q=0 的形式，移常数项，两边同加一次项系数一半的平方，化为 (x+m)²=n 的形式，利用直接开平方法求解。",
        examples=[
            "用配方法解 x²+6x−7=0（(x+3)²=16，x=−7 或 x=1）",
            "用配方法解 2x²−8x+2=0（先化简为 x²−4x+1=0，再配方）",
            "将 x²−4x+1 配方为 (x−2)²−3",
        ],
        common_mistakes=[
            "配方时一次项系数除以 2 后忘记平方",
            "二次项系数不为 1 时忘记先两边除以二次项系数",
            "配方后等号右边为负数时仍开平方，忘记判断无实数根的情况",
        ],
    ),

    KnowledgePoint(
        id="math_g9_003",
        name="公式法解一元二次方程",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_002"],
        description="掌握一元二次方程的求根公式：x=(−b±√(b²−4ac))/(2a)。理解判别式 Δ=b²−4ac 的意义：Δ>0 有两个不等实根，Δ=0 有两个相等实根，Δ<0 无实数根。",
        examples=[
            "用公式法解 x²−5x+6=0（Δ=1>0，x=2 或 x=3）",
            "用公式法解 x²−4x+4=0（Δ=0，x=2，重根）",
            "判断方程 x²+x+1=0 的根的情况（Δ=−3<0，无实数根）",
        ],
        common_mistakes=[
            "代入求根公式时系数 a、b、c 的符号搞错（特别是负号）",
            "判别式 Δ 的计算错误导致对根的情况判断失误",
            "公式中分母是 2a，误写为 2 或 a",
            "Δ<0 时说'无解'，应说'无实数根'（还有复数根）",
        ],
    ),

    KnowledgePoint(
        id="math_g9_004",
        name="因式分解法解一元二次方程",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_001", "math_g8_015"],
        description="掌握因式分解法（十字相乘法）解一元二次方程：将方程一边化为 0，另一边因式分解为两个一次因式的乘积，利用 ab=0 则 a=0 或 b=0 求解。",
        examples=[
            "解方程 x²−7x+10=0（(x−2)(x−5)=0，x=2 或 x=5）",
            "解方程 x²−3x=0（x(x−3)=0，x=0 或 x=3）",
            "解方程 3x²−6x=0（3x(x−2)=0，x=0 或 x=2）",
        ],
        common_mistakes=[
            "方程两边直接约去含 x 的因式，导致丢根（如 x²=3x 直接除以 x 丢掉 x=0 的根）",
            "十字相乘时因式分解不正确",
            "右边不是 0 时直接因式分解（必须先移项使右边为 0）",
        ],
    ),

    KnowledgePoint(
        id="math_g9_005",
        name="一元二次方程的根与系数的关系（韦达定理）",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_003"],
        description="掌握韦达定理：设一元二次方程 ax²+bx+c=0 的两根为 x₁、x₂，则 x₁+x₂=−b/a，x₁·x₂=c/a。能利用韦达定理不解方程求关于两根的代数式的值。",
        examples=[
            "方程 x²−5x+6=0 的两根之和为 5，两根之积为 6",
            "已知方程 x²−3x+1=0 的两根为 x₁、x₂，不求根，求 x₁²+x₂²（(x₁+x₂)²−2x₁x₂=7）",
            "已知方程两根为 2 和 −3，求该一元二次方程（x²+x−6=0）",
        ],
        common_mistakes=[
            "韦达定理中 x₁+x₂=−b/a 忘记负号，误写为 b/a",
            "利用韦达定理求值时不会将目标式变形为 x₁+x₂ 和 x₁·x₂ 的组合",
            "忘记韦达定理的前提是方程有实数根（Δ≥0）",
        ],
    ),

    KnowledgePoint(
        id="math_g9_006",
        name="一元二次方程的应用",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_002", "math_g9_003", "math_g9_004"],
        description="能列一元二次方程解决实际问题，包括：面积问题、增长率问题、利润问题等。能对方程的根进行合理性检验（舍去不符合实际意义的根）。",
        examples=[
            "一个矩形的长比宽多 3 cm，面积为 40 cm²，求长和宽",
            "某商品原价 100 元，连续两次降价后为 81 元，求每次降价的百分率（10%）",
            "某厂一月份产量 500 吨，三月份产量 720 吨，求平均每月增长率（20%）",
        ],
        common_mistakes=[
            "列方程时等量关系找错",
            "增长率问题中公式混淆：增长后量=原量×(1+增长率)ⁿ",
            "解出方程后未检验根的实际合理性，保留了不合题意的解（如负的长度、超过 100% 的增长率）",
        ],
    ),

    # 第二十二章 二次函数

    KnowledgePoint(
        id="math_g9_007",
        name="二次函数的概念与图象",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_025", "math_g8_026"],
        description="理解二次函数的概念：y=ax²+bx+c（a≠0）。掌握二次函数图象是抛物线。理解 a、b、c 对图象的影响。掌握顶点坐标公式 (−b/(2a), (4ac−b²)/(4a))。理解开口方向（a>0 向上，a<0 向下）。",
        examples=[
            "求 y=x²−4x+3 的顶点坐标（2, −1）",
            "判断 y=−2x²+3x−1 的开口方向（向下，因为 a=−2<0）",
            "求 y=x²−2x−3 与 x 轴交点（(−1,0) 和 (3,0)）",
        ],
        common_mistakes=[
            "顶点坐标公式记忆错误，尤其是纵坐标公式 (4ac−b²)/(4a) 的分子分母",
            "混淆 a 的正负与开口方向",
            "求与 x 轴交点时令 x=0 而非令 y=0",
        ],
    ),

    KnowledgePoint(
        id="math_g9_008",
        name="二次函数的性质",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_007"],
        description="掌握二次函数 y=ax²+bx+c 的性质：对称轴 x=−b/(2a)；当 a>0 时，顶点处取最小值；当 a<0 时，顶点处取最大值。掌握增减性：在对称轴两侧单调性相反。能用描点法画二次函数图象。",
        examples=[
            "y=x²−6x+5 的对称轴为 x=3，在 x=3 处取最小值 −4",
            "当 x<3 时 y 随 x 增大而减小，当 x>3 时 y 随 x 增大而增大",
            "求 y=−x²+4x−3 在 0≤x≤5 上的最大值和最小值",
        ],
        common_mistakes=[
            "对称轴方程 x=−b/(2a) 记忆错误或忘记负号",
            "求最值时忘记考虑自变量的取值范围是否包含顶点",
            "增减性的判断与对称轴的关系搞反",
        ],
    ),

    KnowledgePoint(
        id="math_g9_009",
        name="二次函数的三种形式",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_007"],
        description="掌握二次函数的三种表达形式：一般式 y=ax²+bx+c、顶点式 y=a(x−h)²+k（顶点为 (h,k)）、交点式 y=a(x−x₁)(x−x₂)（x₁、x₂ 为与 x 轴交点的横坐标）。能根据不同条件选择合适的形式求解。",
        examples=[
            "将 y=x²−4x+3 化为顶点式 y=(x−2)²−1",
            "已知顶点为 (1,−4) 且过点 (0,−3)，求二次函数（y=(x−1)²−4=x²−2x−3）",
            "已知与 x 轴交于 (1,0) 和 (3,0)，过点 (0,3)，求函数（y=(x−1)(x−3)=x²−4x+3 验证后调整 a）",
        ],
        common_mistakes=[
            "一般式转顶点式时配方出错",
            "顶点式 y=a(x−h)²+k 中 h 的符号：如顶点 (3,2) 对应 y=a(x−3)²+2 而非 y=a(x+3)²+2",
            "交点式中忘记系数 a 的存在，直接写成 y=(x−x₁)(x−x₂)",
        ],
    ),

    KnowledgePoint(
        id="math_g9_010",
        name="二次函数与一元二次方程的关系",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_007", "math_g9_003"],
        description="理解二次函数 y=ax²+bx+c 的图象与 x 轴的交点与一元二次方程 ax²+bx+c=0 的根的关系：Δ>0 时有两个交点，Δ=0 时有一个交点（相切），Δ<0 时无交点。能用图象法近似求一元二次方程的根。",
        examples=[
            "判断 y=x²−2x+3 与 x 轴是否有交点（Δ=−8<0，无交点）",
            "已知二次函数与 x 轴交于 (−1,0) 和 (3,0)，写出一元二次方程的根",
            "利用图象法求 x²−x−1=0 的近似根",
        ],
        common_mistakes=[
            "混淆'函数图象与 x 轴的交点'和'方程的根'之间的对应关系",
            "Δ=0 时说有一个根（实际有两个相等的实数根，图象与 x 轴相切）",
            "用图象法求近似根时读数不够精确",
        ],
    ),

    KnowledgePoint(
        id="math_g9_011",
        name="二次函数的实际应用",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_007", "math_g9_008"],
        description="能建立二次函数模型解决实际问题：最大利润问题、最大面积问题、抛物线型问题（桥梁、隧道、投掷运动等）。能根据实际意义确定自变量的取值范围。",
        examples=[
            "用 20 米长的篱笆围矩形，最大面积为 25 平方米（边长为 5）",
            "商品定价问题：售价每提高 1 元，销量减少 10 件，求最大利润",
            "抛物线型桥拱问题：建立坐标系求桥拱的函数表达式并计算净空高度",
        ],
        common_mistakes=[
            "建立坐标系时原点和坐标轴选择不当导致函数表达式复杂",
            "求最大值时忽略自变量的实际取值范围",
            "利润问题中未正确表示总收入和总成本",
        ],
    ),

    # 第二十三章 旋转

    KnowledgePoint(
        id="math_g9_012",
        name="图形的旋转",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_009"],
        description="理解旋转的概念：将图形绕一个定点转动一定角度。掌握旋转的三要素：旋转中心、旋转角、旋转方向。理解旋转的性质：对应点到旋转中心的距离相等，对应点与旋转中心连线的夹角等于旋转角，旋转前后图形全等。",
        examples=[
            "将点 A(2,3) 绕原点逆时针旋转 90° 后的坐标（−3,2）",
            "将等边三角形绕其中心旋转 120° 后与原图形重合",
            "画 △ABC 绕点 O 旋转 60° 后的图形",
        ],
        common_mistakes=[
            "旋转角的方向判断错误（顺时针与逆时针搞混）",
            "旋转后的对应点坐标计算错误",
            "画旋转图形时对应点到旋转中心的距离不相等",
        ],
    ),

    KnowledgePoint(
        id="math_g9_013",
        name="中心对称与中心对称图形",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_012"],
        description="理解中心对称的概念：将一个图形绕某点旋转 180° 后与另一个图形重合。理解中心对称图形：一个图形绕某点旋转 180° 后与自身重合。掌握中心对称的性质：对称点连线被对称中心平分。",
        examples=[
            "判断平行四边形、矩形、菱形是否为中心对称图形",
            "求点 (3,−2) 关于原点的对称点（−3,2）",
            "画 △ABC 关于点 O 的中心对称图形",
        ],
        common_mistakes=[
            "混淆中心对称（两个图形）与中心对称图形（一个图形）",
            "求关于某点的对称点时坐标计算错误（应为 (2x₀−x, 2y₀−y)）",
            "中心对称与轴对称的混淆",
        ],
    ),

    # 第二十四章 圆

    KnowledgePoint(
        id="math_g9_014",
        name="圆的基本性质",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_003"],
        description="理解圆的定义。掌握圆的相关概念：弦、直径、弧、半圆、等弧、圆心角、圆周角。掌握圆的基本性质：圆是轴对称图形也是中心对称图形。",
        examples=[
            "圆心角的度数等于它所对弧的度数",
            "在同圆或等圆中，相等的圆心角所对的弧相等、弦相等",
            "判断：直径是最长的弦（正确）",
        ],
        common_mistakes=[
            "混淆弦和弧：弦是线段，弧是曲线",
            "等弧必须在同圆或等圆中才能比较，不同圆中的弧不能比较",
            "圆心角与圆周角的概念混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g9_015",
        name="垂径定理",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_014"],
        description="掌握垂径定理：垂直于弦的直径平分这条弦，并且平分弦所对的两条弧。掌握垂径定理的推论：平分弦（非直径）的直径垂直于弦，并且平分弦所对的两条弧。",
        examples=[
            "圆 O 的半径为 5，弦 AB=8，求圆心到弦 AB 的距离（3）",
            "已知弦 AB 被 OC 垂直平分于点 D，OD=3，AB=8，求圆的半径（5）",
            "利用垂径定理求弦长、弓高或半径",
        ],
        common_mistakes=[
            "垂径定理推论中忘记条件'弦不是直径'——平分直径的直线不一定垂直于该直径",
            "利用垂径定理构造直角三角形时，弦的一半、圆心距、半径的关系列错",
            "拱桥问题中坐标系的建立和垂径定理的结合运用出错",
        ],
    ),

    KnowledgePoint(
        id="math_g9_016",
        name="圆心角与圆周角",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_014"],
        description="掌握圆心角与圆周角的关系：在同圆或等圆中，同弧或等弧上的圆周角等于该弧所对圆心角的一半。掌握半圆（或直径）所对的圆周角是直角。90° 的圆周角所对的弦是直径。",
        examples=[
            "圆心角 ∠AOB=80°，则圆周角 ∠ACB=40°（C 在优弧上）",
            "AB 是直径，C 是圆上一点，则 ∠ACB=90°",
            "已知圆周角为 35°，求它所对弧的度数（70°）",
        ],
        common_mistakes=[
            "圆周角定理中'等于圆心角的一半'的前提是同弧上的圆周角和圆心角",
            "圆周角在优弧和劣弧上的度数之和为 180°，容易只考虑一种情况",
            "画圆周角时角的顶点不在圆上",
        ],
    ),

    KnowledgePoint(
        id="math_g9_017",
        name="点与圆、直线与圆的位置关系",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_014"],
        description="掌握点与圆的位置关系：d<r 在圆内，d=r 在圆上，d>r 在圆外（d 为点到圆心的距离，r 为半径）。掌握直线与圆的位置关系：d>r 相离，d=r 相切，d<r 相交（d 为圆心到直线的距离）。掌握切线的性质和判定：切线垂直于过切点的半径。",
        examples=[
            "圆心 O(0,0)，半径 r=5，判断点 (3,4) 与圆的位置关系（在圆上，因为 √(9+16)=5=r）",
            "证明直线是圆的切线：连半径证垂直或作垂线证等于半径",
            "已知圆的切线，求切线长",
        ],
        common_mistakes=[
            "判断直线与圆的位置关系时未正确计算圆心到直线的距离 d",
            "切线的判定与性质混淆：判定是'已知垂直证半径'，性质是'已知切线证垂直'",
            "切线长定理：从圆外一点到圆的两条切线长相等，使用时忘记证全等",
        ],
    ),

    KnowledgePoint(
        id="math_g9_018",
        name="正多边形和圆",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g8_005", "math_g9_014"],
        description="理解正多边形与圆的关系：正多边形有一个外接圆和一个内切圆。掌握正多边形的中心角、边心距等概念和计算。能利用正多边形的性质进行相关计算。",
        examples=[
            "正六边形的中心角为 60°，边长等于外接圆半径",
            "求正三角形的边心距与外接圆半径之比（1:2）",
            "计算正方形外接圆半径与内切圆半径之比（√2:1）",
        ],
        common_mistakes=[
            "混淆外接圆半径（中心到顶点）与内切圆半径（边心距，中心到边）",
            "正 n 边形的中心角 = 360°/n，记错公式",
            "计算正多边形面积时忘记用分割法（n 个等腰三角形面积之和）",
        ],
    ),

    KnowledgePoint(
        id="math_g9_019",
        name="弧长和扇形面积",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_014"],
        description="掌握弧长公式 l=nπr/180。掌握扇形面积公式 S=nπr²/360 或 S=lr/2。掌握圆锥的侧面积和全面积的计算。",
        examples=[
            "半径为 6，圆心角为 120° 的弧长（4π）",
            "半径为 3，圆心角为 60° 的扇形面积（3π/2）",
            "圆锥底面半径为 3，母线长为 5，求侧面积（15π）",
        ],
        common_mistakes=[
            "弧长公式中 n 不带度数符号但代表角度值，与弧度混淆",
            "扇形面积公式选择不当：已知弧长用 S=lr/2，已知圆心角用 S=nπr²/360",
            "圆锥侧面积 = πrl（r 为底面半径，l 为母线长），将底面半径与母线搞混",
        ],
    ),

    # 第二十五章 概率初步

    KnowledgePoint(
        id="math_g9_020",
        name="随机事件与概率",
        grade=9,
        difficulty=Difficulty.EASY,
        prerequisites=[],
        description="理解必然事件、不可能事件和随机事件的概念。理解概率的意义：概率是对随机事件发生可能性大小的度量。必然事件的概率为 1，不可能事件的概率为 0，随机事件的概率在 0 和 1 之间。",
        examples=[
            "判断'明天会下雨'是随机事件",
            "判断'太阳从东方升起'是必然事件（概率为 1）",
            "掷一枚骰子，出现 7 点是不可能事件（概率为 0）",
        ],
        common_mistakes=[
            "混淆随机事件和不可能事件",
            "认为概率小的事件不会发生，概率大的事件一定会发生",
            "对概率的等可能性理解不足",
        ],
    ),

    KnowledgePoint(
        id="math_g9_021",
        name="用列举法求概率",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_020"],
        description="掌握用列举法（列表法、树状图法）求等可能事件的概率：P(A)=事件A包含的结果数/所有等可能结果数。能在两步或三步实验中正确列举所有等可能结果。",
        examples=[
            "掷两枚硬币，求一正一反的概率（2/4=1/2）",
            "袋中有 3 红 2 白共 5 个球，随机取两个，求一红一白的概率",
            "用树状图求连续三次掷硬币均为正面的概率（1/8）",
        ],
        common_mistakes=[
            "列举时遗漏某些结果或重复计算",
            "不等可能的情况直接用公式（必须等可能才行）",
            "有序与无序问题：摸球问题中'先红后白'和'先白后红'是不同结果还是相同结果搞混",
        ],
    ),

    KnowledgePoint(
        id="math_g9_022",
        name="用频率估计概率",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_020"],
        description="理解当试验次数足够大时，事件发生的频率趋于稳定，可以用频率来估计概率。了解蒙特卡洛方法的基本思想。",
        examples=[
            "抛硬币 1000 次，正面朝上 503 次，用频率估计正面朝上的概率约为 0.503",
            "通过大量重复试验，某事件发生的频率稳定在 0.32 附近，估计该事件的概率约为 0.32",
            "解释为什么一次试验的频率不等于概率",
        ],
        common_mistakes=[
            "混淆频率和概率：频率是试验得到的统计值，概率是理论值",
            "认为'频率趋近于概率'意味着频率一定等于概率",
            "试验次数太少时用频率估计概率不可靠",
        ],
    ),

    # ──────────────────────────────────────────────
    # 九年级下册 (Grade 9, Volume 2)
    # ──────────────────────────────────────────────

    # 第二十七章 相似

    KnowledgePoint(
        id="math_g9_023",
        name="比例线段与相似多边形",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g7_010", "math_g8_007"],
        description="理解比例线段的概念：四条线段 a、b、c、d 中，如果 a:b=c:d，则这四条线段成比例。掌握比例的基本性质：a/b=c/d → ad=bc。理解相似多边形的概念：对应角相等，对应边成比例。掌握相似比的概念。",
        examples=[
            "已知 a:b=3:5，b:c=5:7，求 a:b:c（3:5:7）",
            "两相似矩形的长分别为 6 和 9，宽分别为 4 和 6，相似比为 2:3",
            "求线段的比例中项：已知 a=2，c=8，求 b 使 a:b=b:c（b=4）",
        ],
        common_mistakes=[
            "比例的基本性质 ad=bc 应用时搞错交叉相乘",
            "连比问题中中间量的统一处理出错",
            "相似比是有序的，注意对应关系",
        ],
    ),

    KnowledgePoint(
        id="math_g9_024",
        name="相似三角形的判定",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_023", "math_g8_007"],
        description="掌握相似三角形的判定方法：AA（两角分别相等）、SAS（两边成比例且夹角相等）、SSS（三边成比例）。掌握相似三角形预备定理：平行于三角形一边的直线截其他两边，所构成的三角形与原三角形相似。",
        examples=[
            "在 △ABC 和 △DEF 中，∠A=∠D=50°，∠B=∠E=60°，用 AA 判定相似",
            "已知 AB/DE=AC/DF=2/3，∠A=∠D，用 SAS 判定相似",
            "在 △ABC 中，DE∥BC 交 AB、AC 于 D、E，证明 △ADE∽△ABC",
        ],
        common_mistakes=[
            "相似比中对应边的比值方向不一致（如 a/b 对应 c/d 而非 d/c）",
            "SAS 判定中成比例的两边必须是夹角的两边",
            "书写相似时对应顶点顺序不对",
        ],
    ),

    KnowledgePoint(
        id="math_g9_025",
        name="相似三角形的性质",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_024"],
        description="掌握相似三角形的性质：对应角相等、对应边成比例；对应高的比、对应中线的比、对应角平分线的比都等于相似比；周长比等于相似比；面积比等于相似比的平方。",
        examples=[
            "两相似三角形的相似比为 3:5，面积比为 9:25",
            "相似三角形对应高的比为 2:3，则周长比为 2:3，面积比为 4:9",
            "利用相似三角形的性质求未知线段或面积",
        ],
        common_mistakes=[
            "面积比等于相似比的平方，误以为面积比等于相似比",
            "对应高的比等于相似比，忘记是'对应'高而非任意高",
            "周长比等于相似比而非相似比的平方",
        ],
    ),

    KnowledgePoint(
        id="math_g9_026",
        name="位似变换",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_024"],
        description="理解位似图形的概念：两个多边形不仅相似，而且对应顶点的连线交于一点（位似中心），对应边互相平行。掌握画位似图形的方法。能利用位似变换将图形放大或缩小。",
        examples=[
            "以原点为位似中心，将 △ABC 放大为原来的 2 倍",
            "已知位似比为 1:3，画位似图形",
            "在坐标系中，以 (1,1) 为位似中心画位似图形",
        ],
        common_mistakes=[
            "位似比的正负与图形方向的关系：正位似比同侧，负位似比异侧",
            "位似中心不在原点时坐标变换公式套用错误",
            "位似变换后忘记验证对应边是否平行",
        ],
    ),

    # 第二十八章 锐角三角函数

    KnowledgePoint(
        id="math_g9_027",
        name="锐角三角函数",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g8_021", "math_g9_024"],
        description="理解锐角三角函数的定义：在直角三角形中，sinA=对边/斜边、cosA=邻边/斜边、tanA=对边/邻边。掌握 30°、45°、60° 的三角函数值。理解互余两角之间的三角函数关系。",
        examples=[
            "在 Rt△ABC 中，∠C=90°，BC=3，AC=4，AB=5，则 sinA=3/5，cosA=4/5，tanA=3/4",
            "sin30°=1/2，cos60°=1/2，tan45°=1",
            "已知 sinA=3/5，求 cosA（4/5）和 tanA（3/4）",
        ],
        common_mistakes=[
            "混淆对边、邻边、斜边的位置关系（相对于所讨论的角而言）",
            "特殊角的三角函数值记忆错误",
            "sin²A+cos²A=1 的关系不会灵活运用",
            "tanA=sinA/cosA 忘记",
        ],
    ),

    KnowledgePoint(
        id="math_g9_028",
        name="解直角三角形",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_027", "math_g8_021"],
        description="理解解直角三角形的含义：由已知元素（至少含一边）求其余未知元素。掌握解直角三角形的基本类型和解法。能运用解直角三角形解决实际问题（仰角、俯角、坡度、方向角等）。",
        examples=[
            "在 Rt△ABC 中，∠C=90°，∠A=30°，BC=5，求 AB（10）和 AC（5√3）",
            "仰角问题：从地面 A 点看楼顶 B 的仰角为 30°，距楼 50 米，求楼高（50√3/3 米）",
            "坡度问题：坡比为 1:√3，则坡角为 30°",
        ],
        common_mistakes=[
            "解直角三角形时已知条件不足（必须至少知道一条边）",
            "实际问题中方向角（北偏东 30°等）的理解错误",
            "仰角和俯角搞混：仰角向上看，俯角向下看",
            "计算过程中三角函数值代入错误",
        ],
    ),

    # 第二十九章 投影与视图

    KnowledgePoint(
        id="math_g9_029",
        name="投影",
        grade=9,
        difficulty=Difficulty.EASY,
        prerequisites=["math_g8_009"],
        description="理解平行投影和中心投影的概念。平行投影的光线是平行的（如太阳光），中心投影的光线从一点发出（如灯光）。能画出简单图形在平行光和中心光下的投影。",
        examples=[
            "在太阳光下，同一时刻不同物体的物高与影长成正比",
            "路灯下的影子的长度与物体到路灯的距离有关",
            "判断正投影与斜投影的区别",
        ],
        common_mistakes=[
            "混淆平行投影和中心投影的性质",
            "平行投影中不同时刻影长不同，误以为始终成正比",
            "中心投影中影长的变化规律理解错误",
        ],
    ),

    KnowledgePoint(
        id="math_g9_030",
        name="三视图",
        grade=9,
        difficulty=Difficulty.MEDIUM,
        prerequisites=["math_g9_029"],
        description="理解三视图的概念：主视图（从前向后看）、俯视图（从上向下看）、左视图（从左向右看）。掌握三视图的画法规则：长对正、高平齐、宽相等。能根据三视图想象并描述物体的形状。能根据三视图计算几何体的表面积和体积。",
        examples=[
            "画圆柱体的三视图：主视图和左视图为矩形，俯视图为圆",
            "画正方体的三视图：三个视图都是正方形",
            "根据三视图判断几何体：主视图和左视图为三角形，俯视图为圆→圆锥",
        ],
        common_mistakes=[
            "三视图中虚线和实线的使用：看不见的轮廓线用虚线",
            "俯视图的方位判断错误",
            "由三视图还原立体图形时遗漏细节或判断错误",
            "'长对正、高平齐、宽相等'对应关系搞错",
        ],
    ),

    # ──────────────────────────────────────────────
    # 补充综合知识点
    # ──────────────────────────────────────────────

    KnowledgePoint(
        id="math_g9_031",
        name="相似三角形的应用",
        grade=9,
        difficulty=Difficulty.VERY_HARD,
        prerequisites=["math_g9_024", "math_g9_025"],
        description="能利用相似三角形解决实际问题：测量无法直接到达的距离或高度。掌握利用影子测高、利用镜面反射测距等方法。能建立相似模型解决综合问题。",
        examples=[
            "利用阳光影子测树高：同一时刻竹竿高 2 米影长 1.5 米，树影长 6 米，树高 8 米",
            "利用相似三角形测量河宽",
            "综合利用相似与全等解决几何综合题",
        ],
        common_mistakes=[
            "实际测量问题中相似比的正反比关系搞错",
            "多个三角形嵌套时相似关系找错",
            "计算中单位换算遗漏",
        ],
    ),

    KnowledgePoint(
        id="math_g9_032",
        name="圆的综合问题",
        grade=9,
        difficulty=Difficulty.EXPERT,
        prerequisites=["math_g9_015", "math_g9_016", "math_g9_017"],
        description="综合运用圆的知识（垂径定理、圆周角定理、切线长定理等）解决几何综合题。能处理圆与三角形的综合、圆与相似的综合。掌握常见辅助线的作法。",
        examples=[
            "圆中弦 AB、CD 交于点 P，利用圆周角定理和相似三角形求线段长",
            "切线与割线的综合：已知切线长和割线长求半径",
            "圆内接四边形对角互补的性质应用",
        ],
        common_mistakes=[
            "综合题中辅助线作法选择不当（常见辅助线：连半径、作弦心距、作切线等）",
            "圆周角定理和圆心角定理的选择使用不当",
            "多个定理综合运用时逻辑链条断裂",
        ],
    ),

    KnowledgePoint(
        id="math_g9_033",
        name="二次函数与几何综合",
        grade=9,
        difficulty=Difficulty.EXPERT,
        prerequisites=["math_g9_007", "math_g9_008", "math_g9_009"],
        description="综合运用二次函数与几何知识解决压轴题：二次函数图象上的几何图形问题、动点问题、存在性问题等。能将几何条件转化为代数方程。",
        examples=[
            "抛物线 y=x²+bx+c 与 x 轴交于 A、B 两点，求使 △ABC 面积最大的点 C",
            "抛物线上的动点 P 使 △PAB 为等腰三角形，求 P 的坐标",
            "二次函数图象与直线围成区域的面积计算",
        ],
        common_mistakes=[
            "存在性问题中未分情况讨论（如等腰三角形需讨论哪条边为底）",
            "将几何条件转化为方程时遗漏情况",
            "动点问题中自变量取值范围的确定不完整",
            "计算量大时中间步骤出错导致后续全错",
        ],
    ),

    KnowledgePoint(
        id="math_g9_034",
        name="概率的综合应用",
        grade=9,
        difficulty=Difficulty.HARD,
        prerequisites=["math_g9_020", "math_g9_021"],
        description="综合运用概率知识解决实际问题：游戏公平性判断、复杂事件的概率计算、概率与统计的结合。能用概率的知识分析和解决实际问题。",
        examples=[
            "设计一个公平的游戏规则",
            "两个转盘的概率问题：用列表法或树状图法求概率",
            "配紫色问题：红+蓝=紫，求配成紫色的概率",
        ],
        common_mistakes=[
            "游戏公平性的判断标准不清晰（双方获胜概率相等即为公平）",
            "多步实验中树状图法画不完整",
            "不放回与放回实验的概率计算混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g9_035",
        name="代数几何综合题",
        grade=9,
        difficulty=Difficulty.EXPERT,
        prerequisites=["math_g9_009", "math_g9_024", "math_g9_028"],
        description="中考压轴题型：将函数、方程、几何（相似、三角函数、圆等）综合在一起。掌握数形结合、分类讨论、方程思想等数学思想方法的综合运用。",
        examples=[
            "抛物线与直线的交点问题，结合三角形面积或相似",
            "坐标系中的几何问题：求满足特定条件的点坐标",
            "动点沿函数图象运动时相关几何量的变化规律",
        ],
        common_mistakes=[
            "综合题中条件转化遗漏（几何条件→代数方程时丢条件）",
            "分类讨论不完整：等腰三角形三种情况、直角三角形三种情况等",
            "计算过程中因步骤太多而出错",
            "未验证所求的解是否满足所有条件",
        ],
    ),
]

# ──────────────────────────────────────────────
# 合并与查询函数
# ──────────────────────────────────────────────

ALL_POINTS: List[KnowledgePoint] = GRADE_8_POINTS + GRADE_9_POINTS

_INDEX_BY_ID: dict = {p.id: p for p in ALL_POINTS}


def get_point_by_id(point_id: str) -> Optional[KnowledgePoint]:
    """根据知识点 ID 获取知识点，不存在则返回 None。"""
    return _INDEX_BY_ID.get(point_id)


def get_points_by_grade(grade: int) -> List[KnowledgePoint]:
    """获取指定年级的所有知识点。"""
    return [p for p in ALL_POINTS if p.grade == grade]


def get_points_by_difficulty(difficulty: Difficulty) -> List[KnowledgePoint]:
    """获取指定难度的所有知识点。"""
    return [p for p in ALL_POINTS if p.difficulty == difficulty]
