#!/usr/bin/env python3
"""
成长轨迹记录脚本
用法：python save-growth-log.py [--type daily|weekly|emotion|milestone] [--content "内容"]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_log_dir():
    """获取日志存储目录，不存在则创建"""
    log_dir = Path.home() / ".growth-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_monthly_file(log_dir: Path, log_type: str) -> Path:
    """按月份组织文件"""
    now = datetime.now()
    month_str = now.strftime("%Y-%m")
    filename = f"{month_str}-{log_type}.md"
    return log_dir / filename


def append_log(log_type: str, content: str, title: str = None):
    """追加一条记录到对应的月度文件"""
    log_dir = get_log_dir()
    filepath = get_monthly_file(log_dir, log_type)
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # 构建记录头
    type_emoji = {
        "daily": "📅",
        "weekly": "📊",
        "emotion": "🌱",
        "milestone": "🏆"
    }.get(log_type, "📝")
    
    type_label = {
        "daily": "每日复盘",
        "weekly": "每周复盘",
        "emotion": "情绪觉察",
        "milestone": "成长里程碑"
    }.get(log_type, "记录")
    
    header = f"\n---\n\n## {type_emoji} {type_label} · {date_str} {time_str}"
    if title:
        header += f" · {title}"
    header += "\n\n"
    
    # 写入文件
    with open(filepath, "a", encoding="utf-8") as f:
        # 如果是新文件，先写标题
        if filepath.stat().st_size == 0 if filepath.exists() else True:
            month_title = now.strftime("%Y年%m月")
            f.write(f"# 成长轨迹 · {month_title}\n")
        f.write(header)
        f.write(content)
        f.write("\n")
    
    return str(filepath)


def list_logs(log_type: str = None, limit: int = 5):
    """列出最近的记录"""
    log_dir = get_log_dir()
    
    if not log_dir.exists():
        print("暂无成长记录")
        return
    
    # 找到所有相关文件
    if log_type:
        files = sorted(log_dir.glob(f"*-{log_type}.md"), reverse=True)
    else:
        files = sorted(log_dir.glob("*.md"), reverse=True)
    
    if not files:
        print("暂无成长记录")
        return
    
    # 读取最新文件的内容
    latest_file = files[0]
    print(f"\n📂 成长记录文件：{latest_file}\n")
    
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 按分隔符分割，取最后 N 条
    entries = content.split("\n---\n")
    recent = entries[-limit:] if len(entries) > limit else entries
    
    print("\n---\n".join(recent))


def get_stats():
    """获取成长统计"""
    log_dir = get_log_dir()
    
    if not log_dir.exists():
        print(json.dumps({"total": 0, "message": "暂无记录"}))
        return
    
    stats = {
        "total_entries": 0,
        "by_type": {},
        "log_dir": str(log_dir),
        "files": []
    }
    
    for filepath in log_dir.glob("*.md"):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        entries = len(content.split("\n---\n")) - 1
        stats["total_entries"] += entries
        stats["files"].append({
            "file": filepath.name,
            "entries": entries
        })
        
        # 按类型统计
        for log_type in ["daily", "weekly", "emotion", "milestone"]:
            if log_type in filepath.name:
                stats["by_type"][log_type] = stats["by_type"].get(log_type, 0) + entries
    
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="成长轨迹记录工具")
    subparsers = parser.add_subparsers(dest="command")
    
    # save 命令
    save_parser = subparsers.add_parser("save", help="保存一条记录")
    save_parser.add_argument("--type", choices=["daily", "weekly", "emotion", "milestone"],
                             default="emotion", help="记录类型")
    save_parser.add_argument("--content", required=True, help="记录内容（Markdown格式）")
    save_parser.add_argument("--title", help="记录标题（可选）")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="查看最近记录")
    list_parser.add_argument("--type", choices=["daily", "weekly", "emotion", "milestone"],
                             help="筛选类型")
    list_parser.add_argument("--limit", type=int, default=3, help="显示条数")
    
    # stats 命令
    subparsers.add_parser("stats", help="查看成长统计")
    
    args = parser.parse_args()
    
    if args.command == "save":
        filepath = append_log(args.type, args.content, args.title)
        print(f"✅ 已保存到：{filepath}")
    
    elif args.command == "list":
        list_logs(getattr(args, "type", None), args.limit)
    
    elif args.command == "stats":
        get_stats()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
