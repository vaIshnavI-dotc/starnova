import sqlite3
from app.core.database import connect


def table_columns(db: sqlite3.Connection, table_name: str) -> set[str]:
    cursor = db.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def add_column_if_missing(db: sqlite3.Connection, table_name: str, col_name: str, col_def: str):
    cols = table_columns(db, table_name)
    if col_name not in cols:
        db.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")


def run_migrations():
    with connect() as db:
        # 1. Existing table column migrations (nullable / safe defaults)
        add_column_if_missing(db, "sources", "user_id", "TEXT NULL")
        add_column_if_missing(db, "sources", "is_demo", "INTEGER DEFAULT 0")

        add_column_if_missing(db, "tips", "user_id", "TEXT NULL")
        add_column_if_missing(db, "tips", "is_demo", "INTEGER DEFAULT 0")
        add_column_if_missing(db, "tips", "stock_name", "TEXT NULL")
        add_column_if_missing(db, "tips", "claim", "TEXT NULL")
        add_column_if_missing(db, "tips", "red_flags", "TEXT NULL DEFAULT '[]'")

        add_column_if_missing(db, "scored_tips", "return_7d", "REAL NULL")
        add_column_if_missing(db, "scored_tips", "return_30d", "REAL NULL")
        add_column_if_missing(db, "scored_tips", "return_90d", "REAL NULL")
        add_column_if_missing(db, "scored_tips", "status_7d", "TEXT NULL")
        add_column_if_missing(db, "scored_tips", "status_30d", "TEXT NULL")
        add_column_if_missing(db, "scored_tips", "status_90d", "TEXT NULL")

        add_column_if_missing(db, "source_stats", "user_id", "TEXT NULL")
        add_column_if_missing(db, "source_stats", "label", "TEXT NULL")

        # 2. New tables
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_demo INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            tip_id TEXT NULL,
            stage TEXT NOT NULL DEFAULT 'intake',
            questions_asked INTEGER NOT NULL DEFAULT 0,
            questions_max INTEGER NOT NULL DEFAULT 6,
            questions_history TEXT DEFAULT '[]',
            thesis TEXT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL,
            image_url TEXT NULL,
            blocks TEXT NOT NULL,
            quick_replies TEXT NULL,
            FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
        );

        CREATE TABLE IF NOT EXISTS decisions (
            decision_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            tip_id TEXT NOT NULL,
            action TEXT NULL,
            timeframe_days INTEGER NULL,
            exit_target REAL NULL,
            max_loss_pct REAL NULL,
            confidence INTEGER NULL,
            thesis TEXT NULL,
            gaps_count INTEGER DEFAULT 0,
            locked INTEGER NOT NULL DEFAULT 0,
            locked_at TEXT NULL,
            created_at TEXT NOT NULL,
            price_at_decision REAL NULL,
            jump_7d_at_decision REAL NULL,
            outcome_loss INTEGER DEFAULT 0,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(tip_id) REFERENCES tips(tip_id)
        );

        CREATE TABLE IF NOT EXISTS investments (
            investment_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            avg_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            linked_tip_id TEXT NULL,
            created_at TEXT NOT NULL,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS investment_drafts (
            confirm_token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            draft_data TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            tip_id TEXT NOT NULL,
            source_name TEXT NOT NULL,
            results TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            is_demo INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS thesis_links (
            link_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            tip_id TEXT NOT NULL,
            text TEXT NOT NULL,
            status TEXT NOT NULL,
            evidence_summary TEXT NULL,
            evidence_source_url TEXT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
        );

        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
        CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_decisions_user ON decisions(user_id);
        CREATE INDEX IF NOT EXISTS idx_decisions_tip ON decisions(tip_id);
        CREATE INDEX IF NOT EXISTS idx_investments_user ON investments(user_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
        CREATE INDEX IF NOT EXISTS idx_thesis_links_conv ON thesis_links(conversation_id);
        """)
