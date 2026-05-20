# Kid Agent 项目当前状态
# 更新时间: 2026-05-20

## 项目位置
- 笔记本Linux: ~/projects/kid-agent/ (主仓库，通过Tailscale SSH访问)
- 服务器本地: /home/ubuntu/projects/kid-agent-local/ (工作副本)
- Win11: D:/projects/kid-agent/

## 当前代码状态
- Phase 5已完成: Docker+Systemd+Nginx部署全部就绪 (commit cde1d5d)
- 知识库完整集成: 304个数学知识点（1-9年级），已接入主教学流程
- 测试: 280/277通过，5跳过 (集成测试需要API密钥)

## 知识库实现完成 (2026-05-20)
- 数据库schema: src/knowledge/schema.sql (7节点9边模型)
- CRUD层: src/knowledge/crud.py
- 数据库层: src/knowledge/db.py
- 服务层: src/knowledge/service.py (业务逻辑封装)
- API层: src/knowledge/api.py (FastAPI REST接口)
- 导入脚本: src/knowledge/import_points.py (1-9年级)
- E2E测试: tests/test_teaching_loop.py (8个集成测试)

### 已导入数据
- 知识点: 304个 (1-9年级)
- 前置依赖: 322条
- 常见错误: 840条
- 教材: 11本 (1-9年级)
- 学科: 3个 (数学/语文/英语)

### 知识点分布
| 年级 | 知识点数 |
|------|---------|
| 1    | 22 |
| 2    | 22 |
| 3    | 33 |
| 4    | 42 |
| 5    | 46 |
| 6    | 31 |
| 7    | 44 |
| 8    | 29 |
| 9    | 35 |
| **合计** | **304** |

## 知识库集成完成 (2026-05-20)
各模块已接入知识库：

| 模块 | 集成状态 | 主要功能 |
|------|----------|----------|
| QuizEngine | ✅ | 使用常见错误生成干扰项 |
| ExplainEngine | ✅ | 获取定义和常见错误辅助讲解 |
| DiagnoseEngine | ✅ | 使用完整前置依赖图做薄弱点分析 |
| LearningPlanner | ✅ | 用前置依赖关系生成学习路径 |
| KnowledgeGraph | ✅ | 优先使用传入数据，fallback到数据库 |
| loader.py | ✅ | 统一接口，数据库优先，Python文件fallback |

## E2E集成测试验证
8个测试全部通过，验证了：
1. 知识库基本功能（304个知识点）
2. 常见错误从数据库获取
3. 前置依赖图分析
4. 知识图谱集成
5. 下一个可学习知识点推荐
6. 学习路径生成
7. 知识点详情完整性
8. 搜索功能

## 下一步要做的事
1. 扩展习题库（当前0个习题）
2. 修复全文搜索（FTS表同步问题）
3. 添加向量嵌入支持（用于语义检索）
4. 实现多学科支持

## 参考资源
- K12-KGraph (北大): github.com/haolpku/K12-Dataset
- EDUKG (清华): github.com/THU-KEG/EDUKG
- 人教版目录: renjiaoshe.com

## 技术栈
- Python 3.12 + FastAPI + SQLite + WebSocket
- 微信公众号接入 + TTS语音
- 前端: 静态HTML/JS
- 部署: Docker + Nginx + Systemd