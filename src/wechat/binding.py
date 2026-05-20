"""微信用户与学生账号绑定管理"""

import logging

from src.memory.store import get_store

logger = logging.getLogger(__name__)


class UserBinding:
    """微信用户与学生账号绑定管理"""

    def __init__(self):
        """初始化绑定管理器"""
        self._store = None

    async def _get_store(self):
        """获取存储实例"""
        if self._store is None:
            self._store = await get_store()
        return self._store

    async def bind(self, wechat_user_id: str, student_id: str, role: str = "student") -> str:
        """绑定微信用户到学生账号

        Args:
            wechat_user_id: 微信用户OpenID
            student_id: 学生ID
            role: 角色（student/parent）

        Returns:
            str: 绑定结果消息
        """
        store = await self._get_store()

        # 检查学生是否存在
        student = await store.get_student(student_id)
        if not student:
            return f"❌ 找不到学生 '{student_id}'，请检查学生ID是否正确"

        # 检查是否已绑定
        existing = await store.get_wechat_binding(wechat_user_id, role)
        if existing:
            await store.update_wechat_binding(wechat_user_id, student_id, role)
            logger.info(f"Updated binding: {wechat_user_id} -> {student_id} ({role})")
            return f"✅ 已更新绑定：{student.name}"

        # 创建新绑定
        await store.create_wechat_binding(wechat_user_id, student_id, role)

        logger.info(f"New binding: {wechat_user_id} -> {student_id} ({role})")
        return f"✅ 绑定成功！你的账号已关联到：{student.name}"

    async def get_student_id(self, wechat_user_id: str, role: str = "student") -> str | None:
        """根据微信user_id查找student_id

        Args:
            wechat_user_id: 微信用户OpenID
            role: 角色（student/parent）

        Returns:
            str | None: 学生ID
        """
        store = await self._get_store()
        binding = await store.get_wechat_binding(wechat_user_id, role)
        return binding.student_id if binding else None

    async def get_parent_binding(self, student_id: str) -> str | None:
        """根据student_id查找绑定的家长微信user_id

        Args:
            student_id: 学生ID

        Returns:
            str | None: 家长微信OpenID
        """
        store = await self._get_store()
        binding = await store.get_wechat_binding_by_student(student_id, "parent")
        return binding.wechat_user_id if binding else None

    async def get_student_binding(self, student_id: str) -> str | None:
        """根据student_id查找绑定的学生微信user_id

        Args:
            student_id: 学生ID

        Returns:
            str | None: 学生微信OpenID
        """
        store = await self._get_store()
        binding = await store.get_wechat_binding_by_student(student_id, "student")
        return binding.wechat_user_id if binding else None

    async def unbind(self, wechat_user_id: str, role: str = "student") -> bool:
        """解绑微信用户

        Args:
            wechat_user_id: 微信用户OpenID
            role: 角色（student/parent）

        Returns:
            bool: 是否解绑成功
        """
        store = await self._get_store()
        result = await store.delete_wechat_binding(wechat_user_id, role)
        if result:
            logger.info(f"Unbound: {wechat_user_id} ({role})")
        return result


# 默认绑定管理器实例
_default_binding: UserBinding | None = None


def get_user_binding() -> UserBinding:
    """获取默认绑定管理器实例（懒加载）"""
    global _default_binding
    if _default_binding is None:
        _default_binding = UserBinding()
    return _default_binding