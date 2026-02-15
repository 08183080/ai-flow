#!/usr/bin/env python3
"""
每日项目同步脚本
在GitHub Actions中运行，将当天的项目数据保存到GitHub仓库
"""

import os
import json
import datetime
import subprocess
import sys

def sync_daily_projects():
    """同步当天的项目数据到data目录"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    print(f"🔄 开始同步 {today} 的项目数据...")
    
    # 读取今天的日志文件
    log_file = f'logs/{today}.txt'
    
    if not os.path.exists(log_file):
        print(f"⚠️ 今天的日志文件不存在: {log_file}")
        # 尝试查找其他格式的文件
        possible_files = [
            f'logs/{today}_email.html',
            f'logs/{today}_emergency_beautiful.html',
            f'logs/{today}_immediate_email.html'
        ]
        
        for file in possible_files:
            if os.path.exists(file):
                log_file = file
                print(f"✅ 找到替代文件: {log_file}")
                break
        else:
            print(f"❌ 没有找到今天的项目文件")
            return False
    
    # 读取内容
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📄 读取文件成功: {len(content)} 字符")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 保存为Markdown格式
    md_file = f'data/projects_{today}.md'
    try:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f'# GitHub Trending Python 项目 - {today}\n\n')
            f.write('> 每日21:00自动爬取并发送给121个订阅用户\n\n')
            f.write('**维护者**: 谢小果 (openclaw机器人，谢苹果的数字员工)\n\n')
            f.write('---\n\n')
            f.write(content)
        print(f"✅ Markdown文件已保存: {md_file}")
    except Exception as e:
        print(f"❌ 保存Markdown文件失败: {e}")
        return False
    
    # 保存为JSON格式（用于程序化访问）
    json_file = f'data/projects_{today}.json'
    try:
        projects = content.strip().split('\n')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': today,
                'project_count': len(projects),
                'content': content,
                'synced_at': datetime.datetime.now().isoformat(),
                'maintainer': '谢小果 (openclaw机器人，谢苹果的数字员工)'
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON文件已保存: {json_file}")
    except Exception as e:
        print(f"❌ 保存JSON文件失败: {e}")
        # 不因为JSON失败而中止整个流程
    
    # 创建README索引文件
    readme_file = 'data/README.md'
    try:
        if os.path.exists(readme_file):
            with open(readme_file, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        else:
            readme_content = '# AI信息流项目数据归档\n\n'
            readme_content += '> 每日自动同步的项目数据\n\n'
        
        # 添加今天的条目
        new_entry = f'## {today}\n\n'
        new_entry += f'- [projects_{today}.md](projects_{today}.md) - {len(content)} 字符\n'
        new_entry += f'- [projects_{today}.json](projects_{today}.json) - JSON格式\n\n'
        
        # 插入到开头
        readme_content = readme_content.replace('# AI信息流项目数据归档\n\n', 
                                                f'# AI信息流项目数据归档\n\n{new_entry}')
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ README索引已更新: {readme_file}")
    except Exception as e:
        print(f"⚠️ 更新README失败: {e}")
    
    print(f"🎉 项目同步完成: {today}")
    return True

if __name__ == '__main__':
    success = sync_daily_projects()
    sys.exit(0 if success else 1)