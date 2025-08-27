#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加日期字段
"""
import sqlite3
import os
from datetime import date, timedelta

def migrate_database():
    """迁移数据库，添加新的日期字段"""
    
    # 检查可能的数据库文件路径
    possible_db_paths = [
        'instance/app.db',
        'instance/cert_autofill.db',
        'instance/tuv_nord.db'
    ]
    
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path):
            db_path = path
            print(f'找到数据库文件: {db_path}')
            break
    
    if not db_path:
        print(f'❌ 未找到数据库文件，检查了以下路径: {possible_db_paths}')
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute('PRAGMA table_info(form_data)')
        columns = [column[1] for column in cursor.fetchall()]
        print(f'当前 form_data 表的列: {columns}')
        
        # 需要添加的新列
        new_columns = {
            'approval_date': (date.today() - timedelta(days=14)).isoformat(),
            'test_date': (date.today() - timedelta(days=7)).isoformat(),
            'report_date': date.today().isoformat()
        }
        
        # 添加新列（如果不存在）
        for col_name, default_value in new_columns.items():
            if col_name not in columns:
                print(f'添加列: {col_name}，默认值: {default_value}')
                cursor.execute(f'ALTER TABLE form_data ADD COLUMN {col_name} DATE DEFAULT "{default_value}"')
                print(f'✅ 成功添加列 {col_name}')
            else:
                print(f'列 {col_name} 已存在')
        
        # 更新现有记录的日期字段（如果为空）
        for col_name, default_value in new_columns.items():
            cursor.execute(f'UPDATE form_data SET {col_name} = ? WHERE {col_name} IS NULL', (default_value,))
            updated_count = cursor.rowcount
            if updated_count > 0:
                print(f'更新了 {updated_count} 条记录的 {col_name} 字段')
        
        conn.commit()
        print('✅ 数据库迁移完成！')
        return True
        
    except Exception as e:
        print(f'❌ 迁移失败: {str(e)}')
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
