你是高级AI Agent架构师。请修复 kid-agent 项目的核心缺陷，使其成为真正能用的教学Agent。

项目根目录：~/projects/kid-agent/
请先阅读所有现有代码，然后完成以下修复：

## 修复1：对话历史传递（最关键）

tutor.py 中 _handle_chat、_handle_explain 等方法每次只发一条消息给LLM，没有对话上下文。

修复方案：
- 在 TutorAgent 中增加 _build_messages(session, user_message) 方法
- 从 session.messages 取最近20条对话历史（角色+内容），加上当前用户消息
- 所有调用LLM的地方都用这个方法构建 messages，而不是只发单条
- 系统prompt始终放在第一条

## 修复2：掌握状态持久化

StudentModel 的 mastery 字典只存在内存中，进程重启就丢了。

修复方案：
- 在 store.py 新增 MasteryORM 表：student_id, point_id, mastery_level(int), updated_at
- 新增方法：get_mastery(student_id) -> dict[str, int], save_mastery(student_id, point_id, level), get_all_mastery(student_id) -> list
- 在 tutor.py 的 _handle_answer 中，批改后调用 store.save_mastery 持久化
- 在 start_session 中，从数据库加载 mastery 恢复到 StudentModel

## 修复3：意图识别升级

现在用关键词匹配，太蠢了。

修复方案：
- 在 agent/ 下新建 intent.py
- 用LLM做意图识别，prompt要求返回JSON格式，包含intent字段(quiz/answer/explain/diagnose/chat)和confidence字段(0.0到1.0)
- 如果LLM调用失败，fallback到关键词匹配（保留现有逻辑作为降级方案）
- 在 session.state == QUIZ 时，如果意图识别返回chat但confidence低，自动当answer处理

## 修复4：薄弱点优先出题

现在轮询知识点，太蠢了。

修复方案：
- 在 _handle_quiz 中，先加载学生的 mastery 数据
- 找 FUZZY/UNKNOWN/FORGOTTEN 的知识点，优先出这些
- 如果没有薄弱点（新学生），按年级顺序出题
- 同一个知识点不要连续出（检查session中上一题的point_id）

## 修复5：Session 管理

session.py 中的 Session 需要增强：
- messages 列表要保存完整对话（角色、内容、时间戳、metadata）
- 增加 get_recent_messages(n) 方法
- 增加 get_last_quiz() 方法
- session 超时自动清理（超过30分钟不活动）

## 修复6：经验值和激励

批改后根据结果更新XP：
- 答对 +10 XP，连对加成（连续3题 +15，连续5题 +20）
- 答错 +3 XP（鼓励尝试）
- 升级提示：每100 XP升一级，输出祝贺信息

请一个文件一个文件地修改，确保所有修改后的代码语法正确。
修改完成后，运行 python3 -m py_compile 检查每个修改的文件。
