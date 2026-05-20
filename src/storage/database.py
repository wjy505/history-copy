"""SQLite 数据库管理 — 建表、CRUD、全文搜索"""
import sqlite3
import os
from dataclasses import dataclass
from typing import Optional
from .config import get_db_path


@dataclass
class ClipboardItem:
    id: int
    content_type: str  # 'text' | 'image'
    text_content: Optional[str]
    image_path: Optional[str]
    thumbnail_path: Optional[str]
    app_source: Optional[str]
    content_hash: str
    is_pinned: bool
    created_at: str
    accessed_at: Optional[str]


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS clipboard_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type    TEXT NOT NULL CHECK(content_type IN ('text', 'image')),
    text_content    TEXT,
    image_path      TEXT,
    thumbnail_path  TEXT,
    app_source      TEXT,
    content_hash    TEXT NOT NULL DEFAULT '',
    is_pinned       INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    accessed_at     TEXT
);

CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_is_pinned ON clipboard_items(is_pinned);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    text_content,
    content='clipboard_items',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON clipboard_items BEGIN
    INSERT INTO items_fts(rowid, text_content) VALUES (new.id, new.text_content);
END;

CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON clipboard_items BEGIN
    INSERT INTO items_fts(items_fts, rowid, text_content) VALUES('delete', old.id, old.text_content);
END;

CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON clipboard_items BEGIN
    INSERT INTO items_fts(items_fts, rowid, text_content) VALUES('delete', old.id, old.text_content);
    INSERT INTO items_fts(rowid, text_content) VALUES (new.id, new.text_content);
END;
"""


def _row_to_item(row: sqlite3.Row) -> ClipboardItem:
    return ClipboardItem(
        id=row["id"],
        content_type=row["content_type"],
        text_content=row["text_content"],
        image_path=row["image_path"],
        thumbnail_path=row["thumbnail_path"],
        app_source=row["app_source"],
        content_hash=row["content_hash"],
        is_pinned=bool(row["is_pinned"]),
        created_at=row["created_at"],
        accessed_at=row["accessed_at"],
    )


class ClipboardDatabase:
    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or get_db_path()
        self._conn: sqlite3.Connection | None = None

    def open(self):
        db_dir = os.path.dirname(self._db_path)
        os.makedirs(db_dir, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("数据库未打开，请先调用 open()")
        return self._conn

    # ——— 写入 ———

    def insert_item(
        self,
        content_type: str,
        text_content: str | None = None,
        image_path: str | None = None,
        thumbnail_path: str | None = None,
        app_source: str | None = None,
        content_hash: str = "",
    ) -> int:
        cursor = self.conn.execute(
            """INSERT INTO clipboard_items
               (content_type, text_content, image_path, thumbnail_path, app_source, content_hash)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (content_type, text_content, image_path, thumbnail_path, app_source, content_hash),
        )
        self.conn.commit()
        return cursor.lastrowid

    def is_duplicate(self, content_hash: str) -> bool:
        """只检查最新一条记录是否与当前内容相同（防止连续重复复制）"""
        row = self.conn.execute(
            """SELECT content_hash FROM clipboard_items
               ORDER BY created_at DESC LIMIT 1"""
        ).fetchone()
        return row is not None and row["content_hash"] == content_hash

    def update_accessed(self, item_id: int):
        self.conn.execute(
            "UPDATE clipboard_items SET accessed_at = datetime('now','localtime') WHERE id = ?",
            (item_id,),
        )
        self.conn.commit()

    # ——— 查询 ———

    def get_items(
        self,
        limit: int = 100,
        offset: int = 0,
        search_query: str | None = None,
    ) -> list[ClipboardItem]:
        if search_query and search_query.strip():
            return self._search_items(search_query, limit, offset)
        rows = self.conn.execute(
            """SELECT * FROM clipboard_items
               ORDER BY is_pinned DESC, created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def _search_items(self, query: str, limit: int, offset: int) -> list[ClipboardItem]:
        """模糊搜索 — 匹配包含搜索词的文字记录"""
        like_pattern = f"%{query}%"
        rows = self.conn.execute(
            """SELECT * FROM clipboard_items
               WHERE text_content LIKE ? ESCAPE '\\'
               ORDER BY is_pinned DESC, created_at DESC
               LIMIT ? OFFSET ?""",
            (like_pattern, limit, offset),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_item_by_id(self, item_id: int) -> ClipboardItem | None:
        row = self.conn.execute(
            "SELECT * FROM clipboard_items WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_item(row)

    def get_item_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM clipboard_items").fetchone()
        return row["cnt"]

    # ——— 更新 ———

    def pin_item(self, item_id: int, pinned: bool):
        self.conn.execute(
            "UPDATE clipboard_items SET is_pinned = ? WHERE id = ?",
            (1 if pinned else 0, item_id),
        )
        self.conn.commit()

    # ——— 删除 ———

    def delete_item(self, item_id: int) -> str | None:
        """删除记录，返回关联的图片路径（用于文件清理）"""
        row = self.conn.execute(
            "SELECT image_path FROM clipboard_items WHERE id = ?", (item_id,)
        ).fetchone()
        image_path = row["image_path"] if row else None
        self.conn.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
        self.conn.commit()
        return image_path

    def delete_old_items(self, before_datetime: str, exclude_pinned: bool = True) -> list[str]:
        """删除过期记录，返回关联的图片路径列表"""
        if exclude_pinned:
            rows = self.conn.execute(
                """SELECT image_path FROM clipboard_items
                   WHERE is_pinned = 0 AND created_at < ?""",
                (before_datetime,),
            ).fetchall()
            self.conn.execute(
                """DELETE FROM clipboard_items
                   WHERE is_pinned = 0 AND created_at < ?""",
                (before_datetime,),
            )
        else:
            rows = self.conn.execute(
                "SELECT image_path FROM clipboard_items WHERE created_at < ?",
                (before_datetime,),
            ).fetchall()
            self.conn.execute(
                "DELETE FROM clipboard_items WHERE created_at < ?",
                (before_datetime,),
            )
        self.conn.commit()
        return [r["image_path"] for r in rows if r["image_path"]]

    def delete_all(self) -> list[str]:
        """清空所有记录，返回所有图片路径"""
        rows = self.conn.execute(
            "SELECT image_path FROM clipboard_items WHERE image_path IS NOT NULL"
        ).fetchall()
        image_paths = [r["image_path"] for r in rows]
        self.conn.execute("DELETE FROM clipboard_items")
        self.conn.commit()
        return image_paths
