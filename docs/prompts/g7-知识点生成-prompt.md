你需要为中国数学Kid Agent项目创建七年级(初一)的完整知识点数据文件。

### 人教版七年级课程目录

#### 七年级上册
第一章 有理数（正数和负数、有理数、有理数的加减法、有理数的乘除法、有理数的乘方）
第二章 整式的加减（整式、整式的加减）
第三章 一元一次方程（从算式到方程、合并同类项与移项、去括号与去分母、实际问题与一元一次方程）
第四章 几何图形初步（几何图形、直线射线线段、角）

#### 七年级下册
第五章 相交线与平行线（相交线、平行线及其判定、平行线的性质、平移）
第六章 实数（平方根、立方根、实数）
第七章 平面直角坐标系（平面直角坐标系、坐标方法的简单应用）
第八章 二元一次方程组（二元一次方程组、消元法、实际问题与二元一次方程组、三元一次方程组）
第九章 不等式与不等式组（不等式、一元一次不等式、一元一次不等式组）
第十章 数据的收集整理与描述（统计调查、直方图）

创建文件：`/home/ubuntu/projects/kid-agent-local/src/knowledge/math_g7.py`

格式要求同之前：
- Difficulty IntEnum（EASY=1, MEDIUM=2, HARD=3, VERY_HARD=4, EXPERT=5）
- KnowledgePoint dataclass（id, name, grade=7, subject="数学", difficulty, prerequisites, description, examples, common_mistakes）
- GRADE_7_POINTS（至少25个知识点）
- ALL_POINTS = GRADE_7_POINTS
- get_point_by_id, get_points_by_grade, get_points_by_difficulty 函数
- ID格式：math_g7_001 ~ math_g7_025+
- prerequisites 引用六年级的知识点ID（math_g6_xxx）和七年级内部依赖
- 每个 KnowledgePoint 必须有详细的 examples 和 common_mistakes

直接写文件，不要犹豫。
