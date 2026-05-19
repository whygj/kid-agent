"""知识图谱 - 管理知识点和依赖关系"""

from collections import defaultdict
from typing import Any

from src.knowledge.math_g3g5 import ALL_POINTS, KnowledgePoint


class KnowledgeGraph:
    """知识图谱类"""

    def __init__(self, points: list[KnowledgePoint] | None = None):
        """初始化知识图谱"""
        self._points: dict[str, KnowledgePoint] = {}
        self._prereq_graph: dict[str, set[str]] = defaultdict(set)
        self._dependent_graph: dict[str, set[str]] = defaultdict(set)

        if points:
            for point in points:
                self.add_point(point)

    def add_point(self, point: KnowledgePoint) -> None:
        """添加知识点"""
        self._points[point.id] = point

        # 构建前置关系
        for prereq_id in point.prerequisites:
            self._prereq_graph[point.id].add(prereq_id)
            self._dependent_graph[prereq_id].add(point.id)

    def get_point(self, point_id: str) -> KnowledgePoint | None:
        """获取知识点"""
        return self._points.get(point_id)

    def get_all_points(self) -> list[KnowledgePoint]:
        """获取所有知识点"""
        return list(self._points.values())

    def get_prerequisites(self, point_id: str) -> list[KnowledgePoint]:
        """获取知识点的前置知识"""
        prereq_ids = self._prereq_graph.get(point_id, set())
        return [self._points[pid] for pid in prereq_ids if pid in self._points]

    def get_prerequisites_recursive(self, point_id: str) -> list[KnowledgePoint]:
        """递归获取所有前置知识点（包括间接依赖）"""
        visited: set[str] = set()
        result: list[KnowledgePoint] = []

        def _dfs(pid: str):
            if pid in visited or pid not in self._points:
                return
            visited.add(pid)
            prereq_ids = self._prereq_graph.get(pid, set())
            for prereq_id in prereq_ids:
                _dfs(prereq_id)
                if prereq_id in self._points:
                    result.append(self._points[prereq_id])

        _dfs(point_id)
        return result

    def get_dependents(self, point_id: str) -> list[KnowledgePoint]:
        """获取依赖该知识点的后续知识点"""
        dep_ids = self._dependent_graph.get(point_id, set())
        return [self._points[did] for did in dep_ids if did in self._points]

    def get_weak_points(self, mastered: set[str]) -> list[KnowledgePoint]:
        """找出薄弱点：已掌握知识点的后续未掌握知识点"""
        weak: list[KnowledgePoint] = []

        for point_id in mastered:
            deps = self.get_dependents(point_id)
            for dep in deps:
                if dep.id not in mastered:
                    # 检查该点的前置是否都已掌握
                    prereqs = self.get_prerequisites_recursive(dep.id)
                    prereq_ids = {p.id for p in prereqs}
                    if prereq_ids.issubset(mastered):
                        if dep not in weak:
                            weak.append(dep)

        return weak

    def find_learning_path(self, target_id: str, mastered: set[str]) -> list[KnowledgePoint]:
        """找到从已掌握到目标知识点的学习路径"""
        path: list[KnowledgePoint] = []
        visited: set[str] = set()

        def _dfs(pid: str):
            if pid in visited:
                return
            visited.add(pid)

            if pid in mastered:
                return

            prereqs = self.get_prerequisites_recursive(pid)
            for prereq in prereqs:
                if prereq.id not in mastered:
                    _dfs(prereq.id)
                    if prereq not in path:
                        path.insert(0, prereq)

            if pid in self._points and self._points[pid] not in path:
                path.append(self._points[pid])

        _dfs(target_id)
        return path

    def get_points_by_grade(self, grade: int) -> list[KnowledgePoint]:
        """按年级获取知识点"""
        return [p for p in self._points.values() if p.grade == grade]

    def get_points_by_difficulty(self, difficulty: int) -> list[KnowledgePoint]:
        """按难度获取知识点"""
        return [p for p in self._points.values() if p.difficulty.value == difficulty]

    def to_dict(self) -> dict[str, Any]:
        """导出为字典"""
        return {
            "points": [
                {
                    "id": p.id,
                    "name": p.name,
                    "grade": p.grade,
                    "difficulty": p.difficulty.value,
                    "prerequisites": p.prerequisites,
                    "description": p.description,
                }
                for p in self._points.values()
            ],
            "graph": {pid: list(deps) for pid, deps in self._prereq_graph.items()},
        }


# 默认知识图谱实例
_default_graph: KnowledgeGraph | None = None


def get_graph() -> KnowledgeGraph:
    """获取默认知识图谱实例"""
    global _default_graph
    if _default_graph is None:
        _default_graph = KnowledgeGraph(ALL_POINTS)
    return _default_graph