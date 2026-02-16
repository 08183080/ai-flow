#!/usr/bin/env python3
"""
arXiv论文数据同步脚本
每天16:30执行，将arxiv_logs中的日志文件转换为归档格式
"""

import os
import json
import datetime
from pathlib import Path

def sync_arxiv_data():
    """同步arXiv论文数据到arxiv_data目录"""
    
    # 确保目录存在
    os.makedirs('arxiv_data', exist_ok=True)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 查找今天的日志文件
    log_file = f'arxiv_logs/{today}.txt'
    if not os.path.exists(log_file):
        print(f"❌ 今天的arXiv日志文件不存在: {log_file}")
        # 尝试查找最新日志文件
        log_files = sorted(Path('arxiv_logs').glob('*.txt'))
        if log_files:
            log_file = str(log_files[-1])
            print(f"📋 使用最新日志文件: {log_file}")
            today = Path(log_file).stem
        else:
            print("❌ 没有找到任何arXiv日志文件")
            return False
    
    print(f"📄 处理日志文件: {log_file}")
    
    # 读取日志内容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取论文数据（简化版本，实际应该解析具体结构）
    lines = content.strip().split('\n')
    
    # 保存为Markdown格式
    md_file = f'arxiv_data/arxiv_papers_{today}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f'# arXiv AI/ML论文精选 - {today}\n\n')
        f.write('> 每天16:00自动发送给121个订阅用户\n')
        f.write('> 覆盖领域: cs.AI, cs.LG, cs.CL, cs.CV, stat.ML\n\n')
        f.write(content)
    
    # 保存为JSON格式
    json_file = f'arxiv_data/arxiv_papers_{today}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'source_file': log_file,
            'content_length': len(content),
            'lines_count': len(lines),
            'synced_at': datetime.datetime.now().isoformat(),
            'projects': lines[:20] if len(lines) > 20 else lines  # 只保存前20行作为预览
        }, f, ensure_ascii=False, indent=2)
    
    # 创建索引文件
    update_index(today, md_file, json_file)
    
    print(f'✅ arXiv数据已同步:')
    print(f'   📄 Markdown: {md_file}')
    print(f'   📊 JSON: {json_file}')
    return True

def update_index(today, md_file, json_file):
    """更新数据索引文件"""
    index_file = 'arxiv_data/README.md'
    
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = '# arXiv论文数据归档\n\n| 日期 | Markdown文件 | JSON文件 | 同步时间 |\n|------|--------------|----------|----------|\n'
    
    # 检查是否已存在该日期的记录
    if today not in content:
        # 添加到索引
        sync_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_entry = f'| {today} | [{today}.md]({md_file}) | [{today}.json]({json_file}) | {sync_time} |\n'
        
        # 找到表格结束位置
        lines = content.split('\n')
        table_end = 0
        for i, line in enumerate(lines):
            if line.startswith('|') and '---' in lines[i+1]:
                table_end = i + 1
                while table_end < len(lines) and lines[table_end].startswith('|'):
                    table_end += 1
                break
        
        # 插入新行（按日期倒序）
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            if i < table_end:
                new_lines.append(line)
            elif line.startswith('|') and not inserted:
                # 比较日期
                line_date = line.split('|')[1].strip()
                if line_date < today:
                    new_lines.append(new_entry)
                    new_lines.append(line)
                    inserted = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if not inserted:
            # 如果没插入，添加到表格末尾
            for i in range(len(new_lines)-1, -1, -1):
                if new_lines[i].startswith('|'):
                    new_lines.insert(i+1, new_entry)
                    break
        
        content = '\n'.join(new_lines)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✅ 索引文件已更新: {index_file}')

if __name__ == '__main__':
    print("🚀 arXiv论文数据同步开始...")
    success = sync_arxiv_data()
    if success:
        print("🎉 arXiv论文数据同步完成")
    else:
        print("❌ arXiv论文数据同步失败")