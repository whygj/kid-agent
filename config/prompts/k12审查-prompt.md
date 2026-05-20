# Kid Agent 代码审查 + K12扩展设计

通过SSH在老李笔记本上分析kid-agent项目。

## SSH
ssh -o ConnectTimeout=5 whygj@100.103.11.123 "命令"

## 项目路径
~/projects/kid-agent/

## 任务1: 代码质量审查
1. 读取所有src/下的Python文件，分析代码质量
2. 找出潜在bug、性能问题、安全隐患
3. 评估测试覆盖率
4. 给出改进建议

## 任务2: K12知识图谱扩展方案设计
当前只有3-5年级30个知识点(src/knowledge/math_g3g5.py)
设计K12全学段知识图谱：
1. 分析当前数据结构和扩展接口
2. 设计6-9年级的知识点体系（每个年级至少20个知识点）
3. 设计自适应难度引擎如何支持年级维度
4. 保持向后兼容

## 任务3: 测试评估
在笔记本上运行：cd ~/projects/kid-agent && PYTHONPATH=. python3 -m pytest tests/ --tb=short -v
分析测试结果

## 输出
将完整分析报告写入 /home/ubuntu/projects/kid-agent/reports/K12扩展方案-20260520.md
（先mkdir -p，再写入）

注意：不需要在笔记本上改代码，只做分析和报告生成。所有报告写到服务器本地。
