"""知识库数据库连接和初始化模块"""

import logging
from pathlib import Path
from typing import Optional

import sqlite3
from sqlite3 import Connection

from src.config.settings import get_config

logger = logging.getLogger(__name__)


class KnowledgeDB:
    """知识库数据库连接管理器

    负责数据库连接、初始化、建表等基础操作。
    """

    def __init__(self, db_path: Optional[str | Path] = None):
        """初始化知识库数据库

        Args:
            db_path: 数据库文件路径，默认为 data/knowledge.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "knowledge.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[Connection] = None

    def connect(self) -> Connection:
        """获取数据库连接

        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._conn.row_factory = sqlite3.Row  # 返回字典行
            # 启用外键约束
            self._conn.execute("PRAGMA foreign_keys = ON")
            # 启用WAL模式提高并发性能
            self._conn.execute("PRAGMA journal_mode = WAL")
            logger.debug(f"Connected to knowledge database: {self.db_path}")
        return self._conn

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.debug("Knowledge database connection closed")

    def is_initialized(self) -> bool:
        """检查数据库是否已初始化

        Returns:
            bool: 数据库是否包含核心表
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='subjects'"
        )
        result = cursor.fetchone()
        return result is not None

    def init_schema(self, force: bool = False) -> None:
        """初始化数据库Schema

        Args:
            force: 是否强制重建数据库（删除所有表）
        """
        if force and self.is_initialized():
            logger.warning("Force rebuild enabled, dropping existing tables...")
            self._drop_all_tables()

        if self.is_initialized():
            logger.info("Knowledge database already initialized, skipping schema creation")
            return

        # 读取并执行Schema SQL
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.executescript(schema_sql)
            conn.commit()
            logger.info("Knowledge database schema initialized successfully")
            self._insert_default_data()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def _insert_default_data(self) -> None:
        """插入默认数据：数学学科"""
        conn = self.connect()
        cursor = conn.cursor()

        default_data = [
            # 学科
            ("math", "数学", "Mathematics", "primary", 1),
            ("chinese", "语文", "Chinese", "primary", 2),
            ("english", "英语", "English", "primary", 3),
        ]

        cursor.executemany(
            "INSERT OR IGNORE INTO subjects (id, name, name_en, phase, sort_order) VALUES (?, ?, ?, ?, ?)",
            default_data,
        )

        # 数学教材
        math_books = []
        for grade in range(1, 7):
            for semester_idx, semester in enumerate(["上", "下"], 1):
                math_books.append((
                    f"math_{grade}{semester}_rjb",
                    "math",
                    grade,
                    semester,
                    "人教版",
                    "2022",
                    f"数学{grade}年级{semester}",
                ))

        cursor.executemany(
            """INSERT OR IGNORE INTO books (id, subject_id, grade, semester, publisher, version, title)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            math_books,
        )

        conn.commit()
        logger.info(f"Inserted {len(default_data)} subjects and {len(math_books)} books")

    def _drop_all_tables(self) -> None:
        """删除所有表（用于强制重建）"""
        conn = self.connect()
        cursor = conn.cursor()

        # 临时禁用外键约束以便删除表
        cursor.execute("PRAGMA foreign_keys = OFF")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]

        for table in tables:
            if table.startswith("sqlite_"):
                continue
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            logger.debug(f"Dropped table: {table}")

        # 重新启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")

        conn.commit()

    def vacuum(self) -> None:
        """清理数据库，回收空间"""
        conn = self.connect()
        conn.execute("VACUUM")
        conn.commit()
        logger.info("Database vacuumed")

    def get_info(self) -> dict:
        """获取数据库信息

        Returns:
            dict: 数据库信息，包括路径、大小、表信息等
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT count(*) FROM subjects")
        subject_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM concepts")
        concept_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM exercises")
        exercise_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM relation_prerequisite")
        relation_count = cursor.fetchone()[0]

        file_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            "path": str(self.db_path),
            "size_mb": round(file_size / 1024 / 1024, 2),
            "subjects": subject_count,
            "concepts": concept_count,
            "exercises": exercise_count,
            "relations": relation_count,
            "initialized": self.is_initialized(),
        }

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局数据库实例
_db: Optional[KnowledgeDB] = None


def get_db(force_reconnect: bool = False) -> KnowledgeDB:
    """获取知识库数据库实例（单例模式）

    Args:
        force_reconnect: 是否强制重新连接

    Returns:
        KnowledgeDB: 数据库实例
    """
    global _db
    if _db is None or force_reconnect:
        _db = KnowledgeDB()
    return _db


def init_knowledge_db(force: bool = False) -> None:
    """初始化知识库数据库

    Args:
        force: 是否强制重建
    """
    db = get_db()
    db.init_schema(force=force)


def close_knowledge_db() -> None:
    """关闭知识库数据库连接"""
    global _db
    if _db:
        _db.close()
        _db = None