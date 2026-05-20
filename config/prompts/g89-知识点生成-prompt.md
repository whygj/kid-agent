你需要为中国数学Kid Agent项目创建八年级和九年级的完整知识点数据文件。

### 人教版八年级课程目录

#### 八年级上册
第十一章 三角形（与三角形有关的线段、与三角形有关的角、多边形及其内角和）
第十二章 全等三角形（全等三角形、三角形全等的判定、角的平分线的性质）
第十三章 轴对称（轴对称、画轴对称图形、等腰三角形）
第十四章 整式的乘法与因式分解（整式的乘法、乘法公式、因式分解）
第十五章 分式（分式、分式的运算、分式方程）

#### 八年级下册
第十六章 二次根式（二次根式、二次根式的乘除、二次根式的加减）
第十七章 勾股定理（勾股定理、勾股定理的逆定理）
第十八章 平行四边形（平行四边形、特殊的平行四边形——矩形菱形正方形）
第十九章 一次函数（函数、一次函数、课题学习选择方案）
第二十章 数据的分析（数据的集中趋势、数据的波动程度）

### 人教版九年级课程目录

#### 九年级上册
第二十一章 一元二次方程（一元二次方程、解一元二次方程、实际问题与一元二次方程）
第二十二章 二次函数（二次函数的图象和性质、二次函数与一元二次方程）
第二十三章 旋转（图形的旋转、中心对称）
第二十四章 圆（圆的有关性质、点和圆/直线和圆的位置关系、正多边形和圆、弧长和扇形面积）
第二十五章 概率初步（随机事件与概率、用列举法求概率、用频率估计概率）

#### 九年级下册
第二十七章 相似（图形的相似、相似三角形、位似）
第二十八章 锐角三角函数（锐角三角函数、解直角三角形）
第二十九章 投影与视图（投影、三视图）

创建文件：`/home/ubuntu/projects/kid-agent-local/src/knowledge/math_g8g9.py`

格式要求：
- Difficulty IntEnum（EASY=1, MEDIUM=2, HARD=3, VERY_HARD=4, EXPERT=5）
- KnowledgePoint dataclass（id, name, grade, subject="数学", difficulty, prerequisites, description, examples, common_mistakes）
- GRADE_8_POINTS（至少25个知识点，grade=8）
- GRADE_9_POINTS（至少25个知识点，grade=9）
- ALL_POINTS = GRADE_8_POINTS + GRADE_9_POINTS
- get_point_by_id, get_points_by_grade, get_points_by_difficulty 函数
- ID格式：math_g8_001 ~ math_g8_025+, math_g9_001 ~ math_g9_025+
- prerequisites 跨年级依赖（八年级引用七年级math_g7_xxx，九年级引用八年级math_g8_xxx）
- 每个 KnowledgePoint 必须有详细的 examples 和 common_mistakes

直接写文件，不要犹豫。
