# Kid Agent 项目当前状态
# 更新时间: 2026-05-20

## 项目位置
- 笔记本Linux: ~/projects/kid-agent/ (主仓库，通过Tailscale SSH访问)
- 服务器本地: /home/ubuntu/projects/kid-agent/ (工作副本)
- Win11: D:/projects/kid-agent/

## 当前代码状态
- Phase 5已完成: Docker+Systemd+Nginx部署全部就绪
- 知识库完整集成: 304个数学知识点（1-9年级），已接入主教学流程
- 最新提交: 知识库增强 - 视频引擎+FTS修复+向量嵌入+多学科支持 (commit 17100ee)
- 测试: 270/274通过，4跳过 (集成测试需要API密钥)

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
- 习题: 0个 (待生成)

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

## 最新完成功能 (2026-05-20)

### 视频生成引擎
- `src/engine/video/` - 数学概念讲解视频生成（Manim+TTS）
  - models.py: 视频任务、配置、状态模型
  - selector.py: 智能选择视频框架
  - math_video.py: 数学可视化视频生成

### 全文搜索修复
- 重建FTS表支持自动同步（触发器）
- 修复ConceptCRUD.search查询
- `scripts/rebuild_fts.py`: FTS表重建脚本
- `scripts/sync_fts.py`: FTS索引同步脚本

### 向量嵌入支持
- `src/knowledge/semantic_search.py`: 语义搜索服务
  - cosine_similarity计算
  - EmbeddingClient: GLM嵌入API客户端
  - SemanticSearch: 向量检索服务
  - search_hybrid: 混合搜索（全文+语义）
- `scripts/generate_embeddings.py`: 生成嵌入向量脚本

### 多学科支持
- `src/knowledge/multisubject.py`: 跨学科知识点管理
  - Subject枚举和SubjectInfo
  - MultiSubjectService: 多学科服务
  - 跨学科搜索和推荐
  - 跨年级进度追踪

### 习题数据生成
- `scripts/generate_exercises.py`: AI生成习题脚本
- 支持选择题、填空题、计算题、应用题
- 自动关联知识点

### 真实LLM教学闭环测试
- `tests/test_real_teaching.py`: 集成测试
- 验证完整教学流程（出题-判题-讲解）

## 待办事项
- [ ] 运行习题生成脚本（需要API密钥）
- [ ] 运行嵌入向量生成脚本（需要API密钥）
- [ ] 添加更多学科的知识点数据

## 参考资源
- K12-KGraph (北大): github.com/haolpku/K12-Dataset
- EDUKG (清华): github.com/THU-KEG/EDUKG
- 人教版目录: renjiaoshe.com

## 技术栈
- Python 3.12 + FastAPI + SQLite + WebSocket
- 微信公众号接入 + TTS语音
- 前端: 静态HTML/JS
- 部署: Docker + Nginx + Systemd