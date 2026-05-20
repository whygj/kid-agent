"""
人教版小学数学 一年级、二年级 知识点数据
Kid Agent 项目 — 数学知识点图谱

涵盖一年级上/下册、二年级上/下册全部单元，每个知识点包含：
  - 唯一 ID（math_g1_001 ~ math_g1_022, math_g2_001 ~ math_g2_022）
  - 年级与单元归属
  - 难度等级
  - 前置知识链（prerequisites）
  - 典型例题（examples）
  - 常见错误（common_mistakes）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────
# 枚举 & 数据结构
# ──────────────────────────────────────────────

class Difficulty(Enum):
    """知识点难度等级"""
    BEGINNER = "beginner"        # 入门 — 初次接触的基础概念
    EASY = "easy"                # 简单 — 在已有基础上稍作延伸
    MEDIUM = "medium"            # 中等 — 需要综合运用两个以上知识点
    HARD = "hard"                # 较难 — 涉及多步推理或易混淆概念


@dataclass
class KnowledgePoint:
    """单个知识点"""
    id: str                                  # 唯一标识，如 math_g1_001
    name: str                                # 知识点名称
    grade: int                               # 年级（1 或 2）
    semester: str                            # "上册" 或 "下册"
    unit: str                                # 所属单元名称
    difficulty: Difficulty                   # 难度等级
    description: str                         # 详细描述
    prerequisites: list[str] = field(default_factory=list)   # 前置知识点 ID 列表
    examples: list[str] = field(default_factory=list)         # 典型例题
    common_mistakes: list[str] = field(default_factory=list)  # 常见错误


# ══════════════════════════════════════════════
# 一年级知识点（22 个）
# ══════════════════════════════════════════════

GRADE_1_POINTS: list[KnowledgePoint] = [

    # ── 一年级上册 ──────────────────────────────

    KnowledgePoint(
        id="math_g1_001",
        name="数一数",
        grade=1,
        semester="上册",
        unit="准备课",
        difficulty=Difficulty.BEGINNER,
        description="学习用点数的方法数出10以内物体的个数，初步建立数感。能按一定顺序逐一点数，做到不遗漏、不重复，最后说出总数。",
        prerequisites=[],
        examples=[
            "数一数图中有几只小鸟：1、2、3、4、5，一共有5只小鸟。",
            "桌上有3个苹果、2个梨，苹果多还是梨多？",
        ],
        common_mistakes=[
            "数数时漏数或重复数同一个物体",
            "数完后不能正确说出总数",
            "手口不一致——手指移动快于或慢于口头数数",
        ],
    ),

    KnowledgePoint(
        id="math_g1_002",
        name="比多少",
        grade=1,
        semester="上册",
        unit="准备课",
        difficulty=Difficulty.BEGINNER,
        description="通过一一对应的方法比较两组物体的多少，理解'同样多''多''少'的含义。能使用'谁比谁多''谁比谁少'进行完整表述。",
        prerequisites=["math_g1_001"],
        examples=[
            "○○○ 和 △△△ — 圆和三角形同样多。",
            "●●●● 和 ▲▲ — 圆比三角形多2个，三角形比圆少2个。",
        ],
        common_mistakes=[
            "只看物体排列的长度就判断多少，不使用一一对应",
            "混淆'多'和'少'的方向——说成'苹果比梨少'（实际苹果多）",
        ],
    ),

    KnowledgePoint(
        id="math_g1_003",
        name="位置（上下前后左右）",
        grade=1,
        semester="上册",
        unit="位置",
        difficulty=Difficulty.BEGINNER,
        description="能辨认上下、前后、左右这六个基本方位，会用这些方位词描述物体的相对位置关系。理解位置的相对性——参照物不同，描述也不同。",
        prerequisites=[],
        examples=[
            "小明在小红的左边，小红在小明的右边。",
            "书本在桌子的上面，椅子在桌子的下面。",
        ],
        common_mistakes=[
            "混淆左右方向，特别是面对不同朝向时",
            "忽略'谁在谁的哪边'中参照物的变化",
        ],
    ),

    KnowledgePoint(
        id="math_g1_004",
        name="1~5的认识",
        grade=1,
        semester="上册",
        unit="1~5的认识和加减法",
        difficulty=Difficulty.BEGINNER,
        description="认识数字1~5，理解每个数字所表示的数量意义。会读、会写1~5各数，掌握1~5的数序（从小到大和从大到小），能用1~5表示物体的个数。",
        prerequisites=["math_g1_001"],
        examples=[
            "3个苹果用数字'3'表示。",
            "按从小到大排列：1、2、3、4、5。",
        ],
        common_mistakes=[
            "数字书写方向错误或笔画顺序不对",
            "数字'3'和'5'书写时容易混淆",
            "数序混乱——不能正确判断4在3和5之间",
        ],
    ),

    KnowledgePoint(
        id="math_g1_005",
        name="1~5的加减法",
        grade=1,
        semester="上册",
        unit="1~5的认识和加减法",
        difficulty=Difficulty.EASY,
        description="初步理解加法和减法的含义：加法表示'合起来'，减法表示'去掉'。能计算5以内的加法和减法，认识加号'+'、减号'-'和等号'='。能根据图画或实际情境列出加法或减法算式。",
        prerequisites=["math_g1_004"],
        examples=[
            "2 + 3 = 5（树上有2只鸟，又飞来3只，一共有5只）",
            "5 - 2 = 3（有5个气球，破了2个，还剩3个）",
            "看图写算式：盘子里有4个草莓，吃掉1个，还剩几个？4 - 1 = 3",
        ],
        common_mistakes=[
            "混淆加法和减法的含义，看到'飞走'用加法",
            "把'='写成其他符号",
            "计算结果超出5的范围",
        ],
    ),

    KnowledgePoint(
        id="math_g1_006",
        name="0的认识和加减法",
        grade=1,
        semester="上册",
        unit="1~5的认识和加减法",
        difficulty=Difficulty.EASY,
        description="理解0的含义：表示没有、表示起点。会读会写0，能进行与0有关的加减法运算（任何数加0等于它本身，任何数减0等于它本身，相同的数相减等于0）。",
        prerequisites=["math_g1_005"],
        examples=[
            "盘子里没有苹果，用0表示。",
            "3 + 0 = 3，5 - 0 = 5，4 - 4 = 0",
            "尺子上的0表示起点。",
        ],
        common_mistakes=[
            "认为0就是'没有用'，忽略0在计数中的意义",
            "计算 3 - 0 = 0（误以为减0等于0）",
            "数字0的书写不规范——写成椭圆形或太小",
        ],
    ),

    KnowledgePoint(
        id="math_g1_007",
        name="认识图形(一)（立体图形）",
        grade=1,
        semester="上册",
        unit="认识图形(一)",
        difficulty=Difficulty.BEGINNER,
        description="直观认识长方体、正方体、圆柱和球四种立体图形，能辨认和区分这些图形。了解它们的基本特征：长方体和正方体有平平的面；圆柱有两个圆形的平面和弯曲的侧面；球没有平面，可以任意滚动。",
        prerequisites=[],
        examples=[
            "魔方的形状是正方体，鞋盒的形状是长方体。",
            "易拉罐的形状是圆柱，篮球的形状是球。",
            "把各种物品按形状分类。",
        ],
        common_mistakes=[
            "混淆长方体和正方体——忽略正方体每个面都一样大的特征",
            "认为圆柱只能'竖着放'，不能辨认横放的圆柱",
            "把所有能滚动的都叫球",
        ],
    ),

    KnowledgePoint(
        id="math_g1_008",
        name="6~10的认识",
        grade=1,
        semester="上册",
        unit="6~10的认识和加减法",
        difficulty=Difficulty.EASY,
        description="认识数字6~10，理解各数的基数含义和序数含义。掌握6~10的数序，会比较10以内数的大小。能用>、<和=表示两个数的大小关系。掌握6~10各数的组成（如7可以分成2和5、3和4等）。",
        prerequisites=["math_g1_004"],
        examples=[
            "8 > 5，3 < 7，6 = 6",
            "10可以分成1和9、2和8、3和7、4和6、5和5。",
            "从大到小排列：10、9、8、7、6、5、4、3、2、1。",
        ],
        common_mistakes=[
            "混淆'>'和'<'的方向——'大于号开口朝大数'",
            "数的组成不熟练——如不知道8可以分成3和5",
            "序数与基数混淆——'第5个'和'5个'分不清",
        ],
    ),

    KnowledgePoint(
        id="math_g1_009",
        name="6~10的加减法",
        grade=1,
        semester="上册",
        unit="6~10的认识和加减法",
        difficulty=Difficulty.EASY,
        description="能计算10以内的加法和减法，包括连加、连减和加减混合运算。理解交换加数位置和不变的规律。能利用数的组成快速口算。",
        prerequisites=["math_g1_005", "math_g1_008"],
        examples=[
            "4 + 5 = 9，9 - 3 = 6",
            "连加：2 + 3 + 4 = 9",
            "加减混合：8 - 3 + 2 = 7",
        ],
        common_mistakes=[
            "连加连减时忘记中间结果——算完第一步后记错",
            "加减混合题中看错运算符号",
            "交换加数后认为结果也变了——3+5和5+3结果相同",
        ],
    ),

    KnowledgePoint(
        id="math_g1_010",
        name="11~20各数的认识",
        grade=1,
        semester="上册",
        unit="11~20各数的认识",
        difficulty=Difficulty.EASY,
        description="认识11~20各数，理解'10个一是1个十'的概念。掌握11~20各数的组成（如13由1个十和3个一组成）。能正确读、写11~20各数，理解各数位上数字的含义。",
        prerequisites=["math_g1_008"],
        examples=[
            "15里面有1个十和5个一。",
            "1个十和8个一组成18。",
            "从11数到20：11、12、13、14、15、16、17、18、19、20。",
        ],
        common_mistakes=[
            "写十几的数时颠倒十位和个位——如把12写成21",
            "不理解'十位'的含义——认为15的1代表1个一",
            "11~20的数序不熟——数到19后不知道下一个是20",
        ],
    ),

    KnowledgePoint(
        id="math_g1_011",
        name="认识钟表",
        grade=1,
        semester="上册",
        unit="认识钟表",
        difficulty=Difficulty.EASY,
        description="认识钟面上的时针和分针，会看整时和半时。理解时针短而粗、分针长而细。整时时分针指向12，时针指向几就是几时；半时时分针指向6。",
        prerequisites=[],
        examples=[
            "分针指向12，时针指向3，就是3时（3:00）。",
            "分针指向6，时针在7和8之间，就是7时半（7:30）。",
        ],
        common_mistakes=[
            "混淆时针和分针",
            "半时时认为时针应该正好指向某个数字",
            "把7时半说成8时半——忽略时针还没到8",
        ],
    ),

    KnowledgePoint(
        id="math_g1_012",
        name="20以内的进位加法",
        grade=1,
        semester="上册",
        unit="20以内的进位加法",
        difficulty=Difficulty.MEDIUM,
        description="掌握20以内进位加法的计算方法，重点学会'凑十法'。能熟练计算9加几、8加几、7加几、6加几、5加几等进位加法。理解进位的原理——个位满十要向十位进一。",
        prerequisites=["math_g1_009", "math_g1_010"],
        examples=[
            "9 + 4 = 13（凑十法：看大数9，想9+1=10，把4分成1和3，10+3=13）",
            "8 + 5 = 13（把5分成2和3，8+2=10，10+3=13）",
            "7 + 6 = 13（把6分成3和3，7+3=10，10+3=13）",
        ],
        common_mistakes=[
            "凑十时不熟练——不知道把小数分成几和几",
            "忘记进位——9+4=12（忘记10+3=13）",
            "计算结果个位出错——拆数后加错剩余部分",
        ],
    ),

    # ── 一年级下册 ──────────────────────────────

    KnowledgePoint(
        id="math_g1_013",
        name="认识图形(二)（平面图形）",
        grade=1,
        semester="下册",
        unit="认识图形(二)",
        difficulty=Difficulty.EASY,
        description="直观认识长方形、正方形、三角形和圆四种平面图形。能辨认和区分这些图形，了解它们的基本特征。体会平面图形与立体图形的关系——面在体上。能用平面图形拼出简单的组合图形。",
        prerequisites=["math_g1_007"],
        examples=[
            "长方形有4条边，对边相等；正方形有4条边，每条边都相等。",
            "三角形有3条边、3个角。",
            "用长方体的面可以画出长方形。",
        ],
        common_mistakes=[
            "混淆长方形和正方形——忽略正方形四边都相等的特征",
            "认为斜放的三角形就不是三角形",
            "混淆平面图形和立体图形",
        ],
    ),

    KnowledgePoint(
        id="math_g1_014",
        name="20以内的退位减法",
        grade=1,
        semester="下册",
        unit="20以内的退位减法",
        difficulty=Difficulty.MEDIUM,
        description="掌握20以内退位减法的计算方法，重点学会'破十法'和'想加算减法'。能熟练计算十几减9、十几减8、十几减7等退位减法。理解退位原理——个位不够减，从十位借一当十。",
        prerequisites=["math_g1_012"],
        examples=[
            "15 - 9 = 6（破十法：把15分成10和5，10-9=1，1+5=6）",
            "13 - 7 = 6（想加算减：因为7+6=13，所以13-7=6）",
            "16 - 8 = 8（破十法：10-8=2，2+6=8）",
        ],
        common_mistakes=[
            "破十后忘记加回个位上的数——10-9=1后忘记加5",
            "用想加算减法时加法口算不熟练导致出错",
            "混淆进位加法和退位减法的计算策略",
        ],
    ),

    KnowledgePoint(
        id="math_g1_015",
        name="分类与整理",
        grade=1,
        semester="下册",
        unit="分类与整理",
        difficulty=Difficulty.BEGINNER,
        description="学会按一定标准对物体进行分类，能自选分类标准进行分类。会用简单的方法（如画正字、画图、表格）收集和整理数据，能看懂简单的统计图表。",
        prerequisites=["math_g1_001"],
        examples=[
            "把一组图形按形状分类：圆形3个、三角形4个、正方形2个。",
            "按颜色给一组气球分类：红色5个、蓝色3个、黄色4个。",
        ],
        common_mistakes=[
            "分类标准不统一——同一组中混用不同标准",
            "遗漏某类物体——分类后有物体未被归入任何一类",
        ],
    ),

    KnowledgePoint(
        id="math_g1_016",
        name="100以内数的认识",
        grade=1,
        semester="下册",
        unit="100以内数的认识",
        difficulty=Difficulty.EASY,
        description="认识100以内的数，理解'10个十是100'。掌握100以内数的组成（如35由3个十和5个一组成）。能正确读、写100以内的数，理解十位和个位上数字的含义。会比较100以内数的大小。",
        prerequisites=["math_g1_010"],
        examples=[
            "47里面有4个十和7个一。",
            "3个十和9个一组成39。",
            "比较大小：52 < 61，因为十位上5比6小。",
        ],
        common_mistakes=[
            "写数时颠倒十位和个位——如把36写成63",
            "比较数的大小时只看个位不看十位",
            "整十数的读写错误——把'四十'写成'4十'或'14'",
        ],
    ),

    KnowledgePoint(
        id="math_g1_017",
        name="认识人民币",
        grade=1,
        semester="下册",
        unit="认识人民币",
        difficulty=Difficulty.MEDIUM,
        description="认识各种面值的人民币（1元、5元、10元、20元、50元、100元纸币；1角、5角、1元硬币）。理解1元=10角，1角=10分的进率关系。能进行简单的人民币换算和加减计算。",
        prerequisites=["math_g1_016"],
        examples=[
            "1元 = 10角，1角 = 10分，所以1元 = 100分。",
            "2元5角 + 3角 = 2元8角",
            "1张5元可以换5张1元。",
        ],
        common_mistakes=[
            "混淆元和角的换算——认为1元=100角",
            "计算时忘记统一单位——把'2元+3角'算成5",
            "找零计算错误——付5元买东西3元2角，应找回1元8角",
        ],
    ),

    KnowledgePoint(
        id="math_g1_018",
        name="整十数加减整十数",
        grade=1,
        semester="下册",
        unit="100以内的加法和减法(一)",
        difficulty=Difficulty.EASY,
        description="掌握整十数加减整十数的口算方法。理解几个十加减几个十就是几个十的道理。如30+40就是3个十加4个十等于7个十，即70。",
        prerequisites=["math_g1_016"],
        examples=[
            "30 + 40 = 70（3个十 + 4个十 = 7个十）",
            "80 - 30 = 50（8个十 - 3个十 = 5个十）",
            "20 + 30 + 40 = 90",
        ],
        common_mistakes=[
            "30 + 40 = 7（只算数字部分，忘记结果是70）",
            "把整十数加减和一位数加减混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g1_019",
        name="两位数加减一位数和整十数（不进位不退位）",
        grade=1,
        semester="下册",
        unit="100以内的加法和减法(一)",
        difficulty=Difficulty.EASY,
        description="掌握不进位、不退位的两位数加减一位数和两位数加减整十数的口算方法。理解相同数位上的数相加减的道理。如35+2是个位上5+2=7，十位不变，结果是37。",
        prerequisites=["math_g1_018"],
        examples=[
            "35 + 4 = 39（个位5+4=9，十位3不变）",
            "56 - 3 = 53（个位6-3=3，十位5不变）",
            "42 + 30 = 72（十位4+3=7，个位2不变）",
        ],
        common_mistakes=[
            "不同数位的数直接相加——35+2=55（把2加到了十位）",
            "加减整十数时影响了个位——42+30=75（错误地改变了两个数位）",
        ],
    ),

    KnowledgePoint(
        id="math_g1_020",
        name="两位数加减一位数（进位加和退位减）",
        grade=1,
        semester="下册",
        unit="100以内的加法和减法(一)",
        difficulty=Difficulty.MEDIUM,
        description="掌握两位数加一位数（进位）和两位数减一位数（退位）的口算方法。进位加法：个位相加满十要向十位进一；退位减法：个位不够减要从十位借一当十再减。",
        prerequisites=["math_g1_019"],
        examples=[
            "28 + 5 = 33（个位8+5=13，满十进一，十位2+1=3）",
            "34 - 8 = 26（个位4-8不够减，从十位借1，14-8=6，十位3-1=2）",
            "47 + 6 = 53",
        ],
        common_mistakes=[
            "进位后忘记十位加1——28+5=23（忘记进位）",
            "退位后忘记十位减1——34-8=36（忘记退位）",
            "把进位加法和退位减法的策略混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g1_021",
        name="找规律",
        grade=1,
        semester="下册",
        unit="找规律",
        difficulty=Difficulty.MEDIUM,
        description="能发现给定图形或数字排列中的简单规律，并能按规律继续排列。规律类型包括：重复排列规律（如○△□○△□…）、递增递减规律（如2、4、6、8…）等。",
        prerequisites=["math_g1_004", "math_g1_008"],
        examples=[
            "○△△○△△○△△____ — 接下来是○△△（规律为1圆2三角重复）",
            "1、3、5、7、____ — 接下来是9（每次加2）",
            "2、4、8、16、____ — 不属于此阶段超纲，这里侧重简单递增",
        ],
        common_mistakes=[
            "不能准确识别重复单元——如把○△△○△△看作○△重复",
            "只看相邻两个的关系，忽略整体规律",
        ],
    ),

    KnowledgePoint(
        id="math_g1_022",
        name="解决问题（一步计算）",
        grade=1,
        semester="下册",
        unit="综合应用",
        difficulty=Difficulty.MEDIUM,
        description="能用10以内或20以内的加减法解决简单的实际问题。能读懂题意，找到有用的数学信息，提出数学问题，并选择加法或减法来解决。",
        prerequisites=["math_g1_005", "math_g1_014"],
        examples=[
            "小明有8颗糖，小红给了他5颗，现在有多少颗？8 + 5 = 13",
            "停车场有15辆车，开走了7辆，还剩几辆？15 - 7 = 8",
        ],
        common_mistakes=[
            "不理解题意，看到数字就随意加减",
            "不知道什么时候用加法、什么时候用减法",
            "遗漏题目中的信息或添加了题目没有的信息",
        ],
    ),
]


# ══════════════════════════════════════════════
# 二年级知识点（22 个）
# ══════════════════════════════════════════════

GRADE_2_POINTS: list[KnowledgePoint] = [

    # ── 二年级上册 ──────────────────────────────

    KnowledgePoint(
        id="math_g2_001",
        name="认识厘米和米",
        grade=2,
        semester="上册",
        unit="长度单位",
        difficulty=Difficulty.BEGINNER,
        description="认识长度单位厘米(cm)和米(m)，建立1厘米和1米的长度观念。知道1米=100厘米。会用刻度尺量物体的长度（限整厘米），能估测一些物体的长度。",
        prerequisites=["math_g1_016"],
        examples=[
            "食指的宽度大约1厘米。",
            "一庹（张开双臂）的长度大约1米。",
            "铅笔大约长15厘米。",
            "1米 = 100厘米，所以2米 = 200厘米。",
        ],
        common_mistakes=[
            "混淆厘米和米的使用场景——用厘米量教室长度",
            "测量时刻度尺的0刻度没有对齐物体一端",
            "认为厘米比米大——实际1米=100厘米，米更大",
        ],
    ),

    KnowledgePoint(
        id="math_g2_002",
        name="线段的初步认识",
        grade=2,
        semester="上册",
        unit="长度单位",
        difficulty=Difficulty.BEGINNER,
        description="认识线段的特征：直的、有两个端点、可以量出长度。能辨认线段，会画指定长度（整厘米）的线段。知道线段是直线上两点之间的部分。",
        prerequisites=["math_g2_001"],
        examples=[
            "画一条5厘米长的线段：先点一个端点，从0刻度开始，画到5厘米处，再点一个端点。",
            "判断哪些图形是线段——弯曲的不是线段。",
        ],
        common_mistakes=[
            "画的线段没有标出两个端点",
            "测量线段长度时没有从0刻度开始",
            "把射线或直线与线段混淆",
        ],
    ),

    KnowledgePoint(
        id="math_g2_003",
        name="100以内的不进位加法（竖式）",
        grade=2,
        semester="上册",
        unit="100以内的加法和减法(二)",
        difficulty=Difficulty.EASY,
        description="掌握两位数加两位数（不进位）的笔算方法。学会用竖式计算，理解相同数位对齐、从个位加起的规则。如23+45=68。",
        prerequisites=["math_g1_019"],
        examples=[
            "23 + 45 = 68（个位3+5=8，十位2+4=6）",
            "竖式：  23\n       +45\n       ———\n        68",
        ],
        common_mistakes=[
            "竖式中相同数位没有对齐——把个位和十位写歪",
            "从十位开始加而不是从个位开始",
        ],
    ),

    KnowledgePoint(
        id="math_g2_004",
        name="100以内的进位加法（竖式）",
        grade=2,
        semester="上册",
        unit="100以内的加法和减法(二)",
        difficulty=Difficulty.MEDIUM,
        description="掌握两位数加两位数（进位）的笔算方法。重点理解'个位满十，向十位进一'的规则。能正确处理连续进位的情况。会用加法验算减法。",
        prerequisites=["math_g2_003", "math_g1_020"],
        examples=[
            "38 + 47 = 85（个位8+7=15，写5进1，十位3+4+1=8）",
            "竖式：  38\n       +47\n       ———\n        85",
        ],
        common_mistakes=[
            "忘记加进位的1——38+47=75（个位进1后十位忘记加）",
            "进位标错位置或忘记标进位",
            "个位写错——8+7=16（把15记成16）",
        ],
    ),

    KnowledgePoint(
        id="math_g2_005",
        name="100以内的不退位减法（竖式）",
        grade=2,
        semester="上册",
        unit="100以内的加法和减法(二)",
        difficulty=Difficulty.EASY,
        description="掌握两位数减两位数（不退位）的笔算方法。用竖式计算时，相同数位对齐，从个位减起。如67-34=33。",
        prerequisites=["math_g2_003"],
        examples=[
            "67 - 34 = 33（个位7-4=3，十位6-3=3）",
            "89 - 25 = 64",
        ],
        common_mistakes=[
            "竖式中数位没有对齐",
            "减数和被减数写反位置",
        ],
    ),

    KnowledgePoint(
        id="math_g2_006",
        name="100以内的退位减法（竖式）",
        grade=2,
        semester="上册",
        unit="100以内的加法和减法(二)",
        difficulty=Difficulty.MEDIUM,
        description="掌握两位数减两位数（退位）的笔算方法。重点理解'个位不够减，从十位退一当十'的规则。能处理被减数个位为0的特殊情况。会用减法验算加法。",
        prerequisites=["math_g2_005"],
        examples=[
            "52 - 37 = 15（个位2-7不够减，从十位退1，12-7=5，十位5-1-3=1）",
            "70 - 28 = 42（个位0-8不够减，退位后10-8=2，十位7-1-2=4）",
        ],
        common_mistakes=[
            "退位后十位忘记减1——52-37=25（十位没减去退的1）",
            "被减数个位是0时不知如何处理——70-28不会做",
            "退位标记不清导致计算混乱",
        ],
    ),

    KnowledgePoint(
        id="math_g2_007",
        name="连加、连减和加减混合",
        grade=2,
        semester="上册",
        unit="100以内的加法和减法(二)",
        difficulty=Difficulty.MEDIUM,
        description="掌握100以内的连加、连减和加减混合运算。能用竖式分步计算，也可以用简便写法（两个竖式合写）。能解决需要两步计算的实际问题。",
        prerequisites=["math_g2_004", "math_g2_006"],
        examples=[
            "28 + 35 + 19 = 82（先算28+35=63，再算63+19=82）",
            "85 - 37 - 28 = 20（先算85-37=48，再算48-28=20）",
            "72 - 36 + 25 = 61（先算72-36=36，再算36+25=61）",
        ],
        common_mistakes=[
            "第一步算错导致后面全错",
            "加减混合时把运算符号看错——把减号看成加号",
            "列竖式时第二步的数字抄错",
        ],
    ),

    KnowledgePoint(
        id="math_g2_008",
        name="角的初步认识",
        grade=2,
        semester="上册",
        unit="角的初步认识",
        difficulty=Difficulty.BEGINNER,
        description="初步认识角，知道角有一个顶点和两条边。能辨认角，知道角的大小与两边张开的大小有关，与边的长短无关。认识直角，会用三角尺判断直角。",
        prerequisites=["math_g1_013"],
        examples=[
            "角有1个顶点和2条边。",
            "用三角尺的直角去比一比——如果完全重合就是直角。",
            "钟面上3时整，时针和分针组成直角。",
        ],
        common_mistakes=[
            "认为边越长角越大（实际角的大小与边的长短无关）",
            "把角的顶点和边的概念混淆",
            "不会用三角尺正确判断直角",
        ],
    ),

    KnowledgePoint(
        id="math_g2_009",
        name="2~6的乘法口诀",
        grade=2,
        semester="上册",
        unit="表内乘法(一)",
        difficulty=Difficulty.MEDIUM,
        description="理解乘法的意义——求几个相同加数的和用乘法计算比较简便。熟记2~6的乘法口诀，能用口诀进行相关的乘法计算。认识乘号'×'，能将加法算式改写为乘法算式。",
        prerequisites=["math_g1_009"],
        examples=[
            "3个4相加：4+4+4=12，写成乘法：3×4=12或4×3=12",
            "口诀：三四十二",
            "5×6=30（口诀：五六三十）",
        ],
        common_mistakes=[
            "不理解乘法的意义——把3×4算成3+4=7",
            "口诀背诵不熟导致计算出错",
            "混淆乘法和加法的含义——看到'3和4'就写3×4",
        ],
    ),

    KnowledgePoint(
        id="math_g2_010",
        name="观察物体(一)",
        grade=2,
        semester="上册",
        unit="观察物体(一)",
        difficulty=Difficulty.BEGINNER,
        description="能辨认从前面、后面、侧面观察到的简单物体的形状。初步体会从不同位置观察物体看到的形状可能是不同的。能根据看到的形状判断观察者的位置。",
        prerequisites=["math_g1_007"],
        examples=[
            "从前面看一个杯子，能看到杯子的正面；从侧面看，形状不同。",
            "三个人分别从前、后、侧面看同一辆车，画出的形状各不相同。",
        ],
        common_mistakes=[
            "认为从不同方向看到的形状一定相同",
            "不能把二维视图与三维物体联系起来",
        ],
    ),

    KnowledgePoint(
        id="math_g2_011",
        name="7~9的乘法口诀",
        grade=2,
        semester="上册",
        unit="表内乘法(二)",
        difficulty=Difficulty.MEDIUM,
        description="熟记7、8、9的乘法口诀，能用口诀进行相关的乘法计算。能运用乘法解决简单的实际问题（求几个几是多少）。理解乘法口诀中每句口诀可以计算两道乘法算式。",
        prerequisites=["math_g2_009"],
        examples=[
            "7×8=56（口诀：七八五十六）",
            "6×9=54（口诀：六九五十四）",
            "8×9=72（口诀：八九七十二）",
        ],
        common_mistakes=[
            "7、8、9的口诀不熟练——特别是7×8=56容易记错",
            "不能灵活运用一句口诀算两道题——'七八五十六'既算7×8也算8×7",
            "解决问题时不知道用乘法——看到'每排7个，有8排'不知道用乘法",
        ],
    ),

    KnowledgePoint(
        id="math_g2_012",
        name="认识时间（几时几分）",
        grade=2,
        semester="上册",
        unit="认识时间",
        difficulty=Difficulty.MEDIUM,
        description="在一年级认识整时和半时的基础上，进一步认识钟面上的时间，能读写几时几分和几时半。知道1时=60分。能根据钟面上的时针和分针位置说出准确时间。",
        prerequisites=["math_g1_011"],
        examples=[
            "时针过了8，分针指向3（15分），就是8时15分（8:15）。",
            "1时 = 60分，所以分针走一圈，时针走一大格。",
            "时针在5和6之间，分针指向9（45分），就是5时45分（5:45）。",
        ],
        common_mistakes=[
            "分针指向数字几就直接读几时——分针指向3应读15分而不是3分",
            "忽略时针的位置——时针过了8就是8时多而不是9时",
            "混淆'几时过几分'和'几时差几分'的说法",
        ],
    ),

    # ── 二年级下册 ──────────────────────────────

    KnowledgePoint(
        id="math_g2_013",
        name="数据收集整理",
        grade=2,
        semester="下册",
        unit="数据收集整理",
        difficulty=Difficulty.BEGINNER,
        description="学会用投票、举手等方式收集数据。能画'正'字记录数据（每个'正'字代表5个）。能读懂简单的统计表和象形统计图，能根据统计结果回答简单问题。",
        prerequisites=["math_g1_015"],
        examples=[
            "统计全班最喜欢的运动：画'正'字记录，足球'正正正'15人，篮球'正正'10人。",
            "根据统计表回答问题：喜欢足球的比喜欢篮球的多几人？15-10=5人。",
        ],
        common_mistakes=[
            "画'正'字时笔画顺序不对或少画笔画",
            "统计数据时遗漏或重复计数",
            "不能根据统计图表正确回答'最多''最少'等问题",
        ],
    ),

    KnowledgePoint(
        id="math_g2_014",
        name="表内除法(一)（用2~6的乘法口诀求商）",
        grade=2,
        semester="下册",
        unit="表内除法(一)",
        difficulty=Difficulty.MEDIUM,
        description="理解除法的意义：平均分和包含除。认识除号'÷'，能将平均分的过程用除法算式表示。掌握用2~6的乘法口诀求商的方法——想：除数×(?)=被除数。",
        prerequisites=["math_g2_009"],
        examples=[
            "12÷3=4（想：三(四)十二，所以商是4）",
            "把15个苹果平均分给5个小朋友，每人分几个？15÷5=3（想：五(三)十五）",
            "20里面有几个4？20÷4=5（想：四(五)二十）",
        ],
        common_mistakes=[
            "不理解除法的意义——把12÷3算成12-3=9",
            "求商时找不到对应的口诀",
            "混淆'平均分'和'包含除'的两种含义",
        ],
    ),

    KnowledgePoint(
        id="math_g2_015",
        name="图形的运动(一)（平移、旋转、轴对称）",
        grade=2,
        semester="下册",
        unit="图形的运动(一)",
        difficulty=Difficulty.EASY,
        description="结合实例初步认识平移、旋转和轴对称现象。能辨认生活中的平移（如推拉门）和旋转（如风车）现象。能判断一个图形是不是轴对称图形，能找出简单的对称轴。",
        prerequisites=["math_g1_013"],
        examples=[
            "推拉窗的运动是平移；风车的运动是旋转。",
            "蝴蝶、飞机、红领巾都是轴对称图形。",
            "把一张纸对折后剪出的图形展开后是轴对称图形。",
        ],
        common_mistakes=[
            "混淆平移和旋转——认为所有运动都是平移",
            "平行四边形误判为轴对称图形",
            "画对称轴时不是直线或位置不对",
        ],
    ),

    KnowledgePoint(
        id="math_g2_016",
        name="表内除法(二)（用7~9的乘法口诀求商）",
        grade=2,
        semester="下册",
        unit="表内除法(二)",
        difficulty=Difficulty.MEDIUM,
        description="掌握用7、8、9的乘法口诀求商的方法。能综合运用乘法口诀进行乘除法计算。能解决与平均分和包含除相关的实际问题。",
        prerequisites=["math_g2_011", "math_g2_014"],
        examples=[
            "56÷8=7（想：七(八)五十六，所以商是7）",
            "63÷9=7（想：(七)九六十三，所以商是7）",
            "45个苹果，每袋装9个，需要几个袋子？45÷9=5",
        ],
        common_mistakes=[
            "7、8、9相关口诀不熟练导致求商困难",
            "把除法算式中的被除数和除数搞反",
            "解决问题时不能正确判断用乘法还是除法",
        ],
    ),

    KnowledgePoint(
        id="math_g2_017",
        name="混合运算",
        grade=2,
        semester="下册",
        unit="混合运算",
        difficulty=Difficulty.HARD,
        description="掌握没有括号的混合运算顺序：先乘除后加减；只有加减或只有乘除时从左往右算。掌握有小括号的混合运算顺序：先算小括号里面的。能正确进行两步混合运算。",
        prerequisites=["math_g2_014", "math_g2_016"],
        examples=[
            "5 + 3 × 4 = 5 + 12 = 17（先乘后加）",
            "20 - 12 ÷ 4 = 20 - 3 = 17（先除后减）",
            "(15 - 7) × 3 = 8 × 3 = 24（先算括号内）",
            "30 ÷ 5 + 2 = 6 + 2 = 8（先除后加）",
        ],
        common_mistakes=[
            "不分运算顺序，从左到右依次算——5+3×4=32（错误，先算了5+3）",
            "忘记先算小括号里面的",
            "乘除和加减的优先级搞混",
        ],
    ),

    KnowledgePoint(
        id="math_g2_018",
        name="有余数的除法",
        grade=2,
        semester="下册",
        unit="有余数的除法",
        difficulty=Difficulty.HARD,
        description="理解有余数除法的意义：当物品不能正好分完时，剩余的部分叫余数。掌握有余数除法的计算方法，理解'余数一定要比除数小'的规则。能用有余数除法解决实际问题。",
        prerequisites=["math_g2_016"],
        examples=[
            "17÷5=3……2（17里面有3个5，还余2）",
            "22÷4=5……2（余数2比除数4小）",
            "有23个苹果，每袋装4个，可以装几袋？还剩几个？23÷4=5……3，装5袋剩3个。",
        ],
        common_mistakes=[
            "余数大于或等于除数——如17÷5=2……7（余数7比除数5大，不对）",
            "不会判断商是多少——利用乘法口诀找最大的那个",
            "余数忘记写或在应用题中余数的含义理解错误",
        ],
    ),

    KnowledgePoint(
        id="math_g2_019",
        name="万以内数的认识",
        grade=2,
        semester="下册",
        unit="万以内数的认识",
        difficulty=Difficulty.MEDIUM,
        description="认识计数单位'百''千''万'，知道相邻两个计数单位之间的十进关系。掌握万以内数的组成、读法和写法。会比较万以内数的大小。理解数位的含义：个位、十位、百位、千位、万位。",
        prerequisites=["math_g1_016"],
        examples=[
            "3456由3个千、4个百、5个十和6个一组成。",
            "读数：3007读作三千零七（中间有两个0只读一个零）。",
            "比较大小：2530 > 2499（千位相同，比百位5>4）。",
        ],
        common_mistakes=[
            "中间或末尾有0的数读写错误——3007写成30007或读成三千零零七",
            "比较数的大小时逐位比较的方法不熟练",
            "数的组成表达不完整——漏说某个数位",
        ],
    ),

    KnowledgePoint(
        id="math_g2_020",
        name="克和千克",
        grade=2,
        semester="下册",
        unit="克和千克",
        difficulty=Difficulty.EASY,
        description="认识质量单位克(g)和千克(kg)，知道1千克=1000克。建立1克和1千克的质量观念：1枚2分硬币约重1克，2袋盐约重1千克。能选择合适的质量单位，能进行简单的质量计算。",
        prerequisites=["math_g2_019"],
        examples=[
            "一个苹果大约重200克。",
            "一袋大米重5千克，合5000克。",
            "1千克 = 1000克，所以3千克 = 3000克。",
        ],
        common_mistakes=[
            "混淆克和千克的使用场景——用克来描述人的体重",
            "进率搞错——认为1千克=100克",
            "估算物品质量时数量级偏差大——认为一本书重100千克",
        ],
    ),

    KnowledgePoint(
        id="math_g2_021",
        name="数学广角—推理",
        grade=2,
        semester="下册",
        unit="数学广角—推理",
        difficulty=Difficulty.HARD,
        description="初步体验逻辑推理的过程。能根据已知条件，通过排除法、连线法或列表法，推理出正确结论。能在三个或多个条件中进行简单的逻辑推理。",
        prerequisites=["math_g2_013"],
        examples=[
            "小红、小明、小刚分别参加了语文、数学、英语兴趣班。小红不参加语文，小明参加数学。推理：小明→数学，小红→英语，小刚→语文。",
            "三个人的年龄分别是7岁、8岁、9岁。小军不是最大的，小红的年龄是偶数。推理出每个人的年龄。",
        ],
        common_mistakes=[
            "推理过程中没有利用所有已知条件",
            "用猜测代替推理——没有逻辑依据",
            "排除法使用不当——过早排除正确选项",
        ],
    ),

    KnowledgePoint(
        id="math_g2_022",
        name="数学广角—搭配(一)",
        grade=2,
        semester="上册",
        unit="数学广角—搭配(一)",
        difficulty=Difficulty.HARD,
        description="初步感受排列与组合的数学思想。能用连线、列表等有序的方法找出简单的搭配方案。理解'有序思考、不重不漏'的原则。能解决简单的排列问题（如用数字卡片组数）和组合问题（如衣服搭配）。",
        prerequisites=["math_g2_009"],
        examples=[
            "用1、2、3三张数字卡片，能组成几个不同的两位数？答：12、13、21、23、31、32，共6个。",
            "2件上衣和3条裤子，有几种不同的搭配方法？答：2×3=6种。",
        ],
        common_mistakes=[
            "列举时遗漏或重复——没有按顺序排列",
            "排列和组合混淆——'组两位数'是有顺序的，'搭配衣服'要看具体问题",
            "不理解'不重不漏'的重要性——随意列举导致遗漏",
        ],
    ),
]


# ══════════════════════════════════════════════
# 汇总 & 查询函数
# ══════════════════════════════════════════════

ALL_POINTS: list[KnowledgePoint] = GRADE_1_POINTS + GRADE_2_POINTS

# 索引字典（构建一次，加速查找）
_BY_ID: dict[str, KnowledgePoint] = {p.id: p for p in ALL_POINTS}


def get_point_by_id(point_id: str) -> Optional[KnowledgePoint]:
    """根据知识点 ID 查找并返回对应的知识点，不存在则返回 None。"""
    return _BY_ID.get(point_id)


def get_points_by_grade(grade: int) -> list[KnowledgePoint]:
    """返回指定年级的全部知识点列表。"""
    return [p for p in ALL_POINTS if p.grade == grade]


def get_points_by_difficulty(difficulty: Difficulty) -> list[KnowledgePoint]:
    """返回指定难度等级的全部知识点列表。"""
    return [p for p in ALL_POINTS if p.difficulty == difficulty]


def get_prerequisites_chain(point_id: str) -> list[str]:
    """返回某知识点的完整前置知识链（递归展开，按依赖顺序排列，无重复）。"""
    visited: list[str] = []
    seen: set[str] = set()

    def _walk(pid: str) -> None:
        point = get_point_by_id(pid)
        if point is None:
            return
        for pre in point.prerequisites:
            if pre not in seen:
                seen.add(pre)
                _walk(pre)
                visited.append(pre)

    _walk(point_id)
    return visited
