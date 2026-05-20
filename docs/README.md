# Kid Agent 项目文档索引
# 更新: 2026-05-20

## 目录结构

```
kid-agent-local/
├── PROJECT-STATUS.md          项目当前状态、待办事项
│
├── docs/
│   ├── README.md              本文件，文档索引
│   ├── KNOWLEDGE-BASE-DESIGN.md   ★核心：知识库框架设计（16KB）
│   │                              含完整SQLite建表SQL、检索方案、API设计、实施路线图
│   │
│   ├── CURRICULUM-REFERENCE.md    人教版1-12年级完整课程目录（小学+初中+高中）
│   │
│   ├── REFERENCES.md              参考资料：K12-KGraph(北大)、EDUKG(清华)、
│   │                              学而思、猿辅导、松鼠AI等平台架构研究
│   │
│   ├── SEED-DATA-STATUS.md        已生成的种子数据说明（数学1-9年级py文件）
│   │
│   ├── prompts/                   Claude Code执行时的prompt记录
│   │   ├── g12-知识点生成-prompt.md     1-2年级知识点生成指令
│   │   ├── g345-知识点扩充-prompt.md    3-5年级知识点扩充指令
│   │   ├── g6-知识点生成-prompt.md      6年级知识点生成指令
│   │   ├── g7-知识点生成-prompt.md      7年级知识点生成指令
│   │   ├── g89-知识点生成-prompt.md     8-9年级知识点生成指令
│   │   └── k12审查-prompt.md            K12审查指令
│   │
│   ├── reports/                   执行报告和分析文档
│   │   ├── K12扩展方案-20260520.md      ★K12扩展方案（24KB，515行）
│   │   │                                 含6-9年级80个知识点设计、4个Phase实施路线
│   │   ├── kid-agent审查结果.md         代码审查：发现2个BUG+测试结果
│   │   ├── bug修复方案.md               tutor.py BUG修复方案
│   │   ├── g12-执行结果.md              1-2年级知识点生成结果
│   │   ├── g345-执行结果.md             3-5年级知识点扩充结果
│   │   ├── g6-执行结果.md               6年级知识点生成结果（31个）
│   │   ├── g7-执行结果.md               7年级知识点生成结果（44个）
│   │   ├── g89-执行结果.md              8-9年级知识点生成结果（50+个）
│   │   ├── phase2-方案.md               Phase 2方案
│   │   ├── phase3-方案.md               Phase 3方案
│   │   ├── phase4-方案.md               Phase 4方案
│   │   └── phase5-方案.md               Phase 5方案
│   │
│   └── research/                  研究报告
│       └── GenericAgent-深度分析-20260520.md  GenericAgent架构研究（25KB，619行）
│
└── src/knowledge/                 种子数据（Python格式，待迁移到SQLite）
    ├── math_g1g2.py               一年级+二年级数学知识点（~40+个，45KB）
    ├── math_g3g5_v2.py            三年级+四年级+五年级数学知识点（~75+个，80KB）
    ├── math_g6.py                 六年级数学知识点（31个，38KB）
    ├── math_g7.py                 七年级数学知识点（44个，56KB）
    └── math_g8g9.py               八年级+九年级数学知识点（~50+个，68KB）

```

## 开发者快速上手

1. 先读 PROJECT-STATUS.md 了解项目状态
2. 再读 KNOWLEDGE-BASE-DESIGN.md 了解知识库架构
3. 参考CURRICULUM-REFERENCE.md获取人教版课程目录
4. 参考REFERENCES.md获取学术界和行业参考

## 下一步开发任务

1. 按KNOWLEDGE-BASE-DESIGN.md创建SQLite schema
2. 实现FastAPI CRUD API
3. 将src/knowledge/下的种子数据迁移到SQLite
4. 考虑导入K12-KGraph数据集（HuggingFace: lhpku20010120/K12-KGraph）
5. 修复tutor.py的两个BUG
