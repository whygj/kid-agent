"""知识图谱 - 管理知识点和依赖关系"""

import logging
from collections import defaultdict
from typing import Any

from src.knowledge.loader import KnowledgePoint, get_prerequisites, get_dependents

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """知识图谱类

    从数据库加载前置依赖关系，兼容原有接口。
    """

    def __init__(self, points: list[KnowledgePoint] | None = None):
        """初始化知识图谱"""
        self._points: dict[str, KnowledgePoint] = {}
        self._prereq_graph: dict[str, set[str]] = defaultdict(set)
        self._dependent_graph: dict[str, set[str]] = defaultdict(set)

        if points:
            for point in points:
                self.add_point(point)
        else:
            self._load_from_database()

    def add_point(self, point: KnowledgePoint) -> None:
        """添加知识点"""
        self._points[point.id] = point

        # 构建前置关系：优先使用知识点的prerequisites，再从数据库查找
        prereq_ids = point.prerequisites if point.prerequisites else []
        if not prereq_ids:
            # 尝试从数据库获取
            prereq_ids = get_prerequisites(point.id)

        for prereq_id in prereq_ids:
            self._prereq_graph[point.id].add(prereq_id)
            self._dependent_graph[prereq_id].add(point.id)

    def _load_from_database(self) -> None:
        """从数据库加载所有知识点和关系"""
        try:
            from src.knowledge.loader import get_all_points, clear_cache

            # 清除缓存确保获取最新数据
            clear_cache()

            points = get_all_points()
            for point in points:
                self.add_point(point)

            logger.info(f"Loaded {len(self._points)} points from database")
        except Exception as e:
            logger.warning(f"Failed to load from database: {e}, using empty graph")

    def get_point(self, point_id: str) -> KnowledgePoint | None:
        """获取知识点"""
        # 先从缓存返回
        if point_id in self._points:
            return self._points[point_id]

        # 尝试从数据库加载
        from src.knowledge.loader import get_point

        point = get_point(point_id)
        if point:
            self._points[point_id] = point
            # 加载前置关系
            prereq_ids = get_prerequisites(point_id)
            for prereq_id in prereq_ids:
                self._prereq_graph[point.id].add(prereq_id)
                self._dependent_graph[prereq_id].add(point_id)
            return point

        return None

    def get_all_points(self) -> list[KnowledgePoint]:
        """获取所有知识点"""
        # 如果缓存为空，从数据库加载
        if not self._points:
            self._load_from_database()
        return list(self._points.values())

    def get_prerequisites(self, point_id: str) -> list[KnowledgePoint]:
        """获取知识点的前置知识"""
        # 优先使用内部构建的前置图
        prereq_ids = self._prereq_graph.get(point_id, set())
        if not prereq_ids:
            prereq_ids = set(get_prerequisites(point_id))
        return [self._points.get(pid) for pid in prereq_ids if pid in self._points]

    def get_prerequisites_recursive(self, point_id: str) -> list[KnowledgePoint]:
        """递归获取所有前置知识点（包括间接依赖）"""
        visited: set[str] = set()
        result: list[KnowledgePoint] = []

        def _dfs(pid: str):
            if pid in visited:
                return
            visited.add(pid)

            # 使用内部图获取前置依赖
            prereq_ids = self._prereq_graph.get(pid, set())
            if not prereq_ids:
                prereq_ids = set(get_prerequisites(pid))

            for prereq_id in prereq_ids:
                _dfs(prereq_id)
                if prereq_id in self._points and prereq_id not in [p.id for p in result]:
                    point = self._points.get(prereq_id)
                    if point:
                        result.append(point)

        _dfs(point_id)
        return result

    def get_dependents(self, point_id: str) -> list[KnowledgePoint]:
        """获取依赖该知识点的后续知识点"""
        # 优先使用内部构建的依赖图
        dep_ids = self._dependent_graph.get(point_id, set())
        if not dep_ids:
            # Fallback: 从数据库加载
            dep_ids = set(get_dependents(point_id))
        return [self._points.get(did) for did in dep_ids if did in self._points]

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
        if not self._points:
            self._load_from_database()
        return [p for p in self._points.values() if p.grade == grade]

    def get_points_by_difficulty(self, difficulty: int) -> list[KnowledgePoint]:
        """按难度获取知识点"""
        if not self._points:
            self._load_from_database()
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
        _default_graph = KnowledgeGraph()
    return _default_graph