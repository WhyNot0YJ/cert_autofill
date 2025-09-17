import os
import shutil
import sqlite3
from pathlib import Path


def find_db_file() -> Path:
    """尽可能智能地定位 SQLite 数据文件路径。"""
    backend_dir = Path(__file__).resolve().parents[1]
    candidates = [
        backend_dir / "instance" / "cert_autofill.db",
        backend_dir / "cert_autofill.db",
        backend_dir.parents[0] / "backend" / "instance" / "cert_autofill.db",
        backend_dir.parents[0] / "backend" / "cert_autofill.db",
    ]

    for p in candidates:
        if p.exists():
            return p

    # 若都不存在，返回默认建议路径（不一定存在）
    return backend_dir / "instance" / "cert_autofill.db"


def ensure_backup(db_path: Path) -> Path:
    """在同目录创建一次性备份文件。"""
    backup_path = db_path.with_suffix(db_path.suffix + ".bak")
    try:
        shutil.copy2(db_path, backup_path)
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"备份失败（将继续）：{e}")
    return backup_path


def get_existing_columns(cur) -> dict:
    cur.execute("PRAGMA table_info(form_data)")
    rows = cur.fetchall()
    return {row[1]: row for row in rows}


def main():
    # 需要补充的列及其 SQLite 类型
    required_columns = {
        # JSON 在 SQLite 中以 TEXT 存储，应用层序列化/反序列化
        "equipment": "TEXT",
        "vehicles": "TEXT",
        # 日期字段
        "approval_date": "DATE",
        "test_date": "DATE",
        "report_date": "DATE",
        # 业务布尔/文本与系统参数
        "glass_color_choice": "TEXT",
        "interlayer_total": "INTEGER",      # 布尔 0/1
        "interlayer_partial": "INTEGER",
        "interlayer_colourless": "INTEGER",
        "conductors_choice": "TEXT",
        "opaque_obscure_choice": "TEXT",
        "version_1": "INTEGER",
        "version_2": "INTEGER",
        "version_3": "INTEGER",
        "version_4": "INTEGER",
        "temperature": "TEXT",
        "ambient_pressure": "TEXT",
        "relative_humidity": "TEXT",
    }

    db_path = find_db_file()
    print(f"目标数据库: {db_path}")
    if not db_path.exists():
        print("警告: 数据库文件不存在。请确认后再运行本脚本。")
        return

    ensure_backup(db_path)

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        existing = get_existing_columns(cur)
        print("现有列:", ", ".join(sorted(existing.keys())))

        added = []
        for col, typ in required_columns.items():
            if col not in existing:
                sql = f"ALTER TABLE form_data ADD COLUMN {col} {typ}"
                print("执行:", sql)
                cur.execute(sql)
                added.append(col)

        conn.commit()
        if added:
            print("已新增列:", ", ".join(added))
        else:
            print("未新增任何列；表结构已是最新。")

        # 简单验证：尝试查询一次
        try:
            cur.execute("SELECT id FROM form_data LIMIT 1")
            cur.fetchall()
            print("校验通过：表可正常查询。")
        except Exception as e:
            print(f"校验查询失败：{e}")
    finally:
        conn.close()
        print("完成。")


if __name__ == "__main__":
    main()


