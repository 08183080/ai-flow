#!/usr/bin/env python3
"""
快速预览脚本 - 不依赖外部依赖，直接展示邮件模板效果
"""

import os
import json
from datetime import datetime
from pathlib import Path


def read_template(template_path):
    """读取HTML模板文件"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取模板失败: {e}")
        # 返回一个基本模板
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI趋势分析</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #667eea; color: white; padding: 30px; border-radius: 10px; }
        .project { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .tag { display: inline-block; padding: 5px 10px; margin: 5px; border-radius: 15px; }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>"""


def generate_preview_data():
    """生成预览数据"""
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "highlight_project": {
            "title": "ruvnet/wifi-densepose",
            "description": "基于WiFi的密集人体姿态估计系统，无需摄像头，仅通过WiFi信号就能追踪人体姿态",
            "tag": "视觉AI",
            "tag_class": "visual"
        },
        "categories": [
            {"name": "AI工具", "count": 5, "examples": "awesome-ai, llm-tools, model-zoo"},
            {"name": "计算机视觉", "count": 3, "examples": "wifi-densepose, real-time-detection"},
            {"name": "开发者工具", "count": 4, "examples": "debugger, cli-helper"}
        ],
        "trends": ["AI工具增多", "隐私友好技术", "边缘计算"],
        "insights": [
            "AI工具类项目持续增多，反映AI技术普及化趋势",
            "隐私友好的感知技术成为新热点（如WiFi姿态估计）",
            "开源LLM基准测试工具需求增加"
        ],
        "prediction": "未来更多AI与传统行业结合的项目，边缘AI计算框架将增多",
        "project_count": 15,
        "category_count": 8,
        "subscriber_count": 121
    }


def render_template(template_html, data):
    """简单模板渲染"""
    html = template_html
    
    # 替换所有变量
    html = html.replace('{{ date }}', data['date'])
    html = html.replace('{{ highlight_project.title }}', data['highlight_project']['title'])
    html = html.replace('{{ highlight_project.description }}', data['highlight_project']['description'])
    html = html.replace('{{ highlight_project.tag }}', data['highlight_project']['tag'])
    html = html.replace('{{ highlight_project.tag_class }}', data['highlight_project']['tag_class'])
    
    # 项目分类 - 简单处理
    categories_html = ""
    for cat in data['categories']:
        categories_html += f'<div style="margin: 15px 0;"><strong>{cat["name"]} ({cat["count"]}个):</strong><div style="color: #718096; font-size: 0.95rem; margin-top: 5px;">{cat["examples"]}</div></div>'
    html = html.replace('{% for category in categories %}\n                {% for category in categories %}', '')
    html = html.replace('{% endfor %}', categories_html)
    
    # 技术趋势
    trends_html = ""
    for trend in data['trends']:
        trends_html += f'<span class="trend-badge">{trend}</span> '
    html = html.replace('{% for trend in trends %}\n                <span class="trend-badge">{{ trend }}</span>\n                {% endfor %}', trends_html)
    
    # 深度洞察
    insights_html = ""
    for insight in data['insights']:
        insights_html += f'<div class="insight-item">{insight}</div>'
    html = html.replace('{% for insight in insights %}\n                    <div class="insight-item">{{ insight }}</div>\n                    {% endfor %}', insights_html)
    
    # 其他变量
    html = html.replace('{{ prediction }}', data['prediction'])
    html = html.replace('{{ project_count }}', str(data['project_count']))
    html = html.replace('{{ category_count }}', str(data['category_count']))
    html = html.replace('{{ subscriber_count }}', str(data['subscriber_count']))
    
    return html


def main():
    """主函数"""
    print("🎨 生成AI信息流邮件预览...")
    print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查模板文件
    template_paths = [
        'templates/email_python.html',
        'email_python.html',
        '/root/ai-flow/templates/email_python.html'
    ]
    
    template_html = None
    template_used = None
    
    for path in template_paths:
        if os.path.exists(path):
            template_html = read_template(path)
            template_used = path
            print(f"✅ 找到模板文件: {path}")
            break
    
    if not template_html:
        print("⚠️  未找到模板文件，使用内置模板")
        template_html = read_template('')
        template_used = "内置模板"
    
    # 生成预览数据
    print("📊 生成模拟数据...")
    preview_data = generate_preview_data()
    
    # 渲染模板
    print("🖌️  渲染HTML...")
    rendered_html = render_template(template_html, preview_data)
    
    # 保存预览文件
    output_dir = "preview_output"
    os.makedirs(output_dir, exist_ok=True)
    
    html_file = os.path.join(output_dir, "email_preview.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    # 生成简化版预览（纯文本展示）
    text_preview = f"""
{'='*60}
✨ AI信息流邮件预览生成完成！
{'='*60}

📅 日期: {preview_data['date']}
🏆 最惊艳项目: {preview_data['highlight_project']['title']}
📝 描述: {preview_data['highlight_project']['description']}

📊 项目分类:
{chr(10).join([f'  • {cat["name"]}: {cat["count"]}个项目 ({cat["examples"]})' for cat in preview_data['categories']])}

📈 技术趋势: {', '.join(preview_data['trends'])}

🔍 深度洞察:
{chr(10).join([f'  • {insight}' for insight in preview_data['insights']])}

🎯 预测: {preview_data['prediction']}

📁 预览文件已保存:
   HTML文件: {os.path.abspath(html_file)}
   文件大小: {len(rendered_html)} 字符

💡 查看方法:
   1. 在浏览器中打开: file://{os.path.abspath(html_file)}
   2. 或使用命令: firefox {os.path.abspath(html_file)} 2>/dev/null &

📊 统计:
   分析项目: {preview_data['project_count']}个
   技术分类: {preview_data['category_count']}类  
   订阅用户: {preview_data['subscriber_count']}人

⏰ 当前时间: {datetime.now().strftime('%H:%M:%S')}
   距离21:00定时任务: 约{60 - datetime.now().minute}分钟
{'='*60}
"""
    
    print(text_preview)
    
    # 尝试在终端中显示部分HTML样式
    print("🎭 终端样式预览:")
    print("┌" + "─" * 58 + "┐")
    print(f"│ {'🚀 AI趋势分析报告'.center(56)} │")
    print(f"│ {'📅 ' + preview_data['date'] + ' · AI信息流2.0'.center(56)} │")
    print("├" + "─" * 58 + "┤")
    print(f"│ {'⭐ 今日最惊艳项目'.ljust(56)} │")
    print(f"│  {preview_data['highlight_project']['title']}".ljust(58) + "│")
    print(f"│  {preview_data['highlight_project']['description'][:54]}... │")
    print("└" + "─" * 58 + "┘")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()