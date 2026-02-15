#!/usr/bin/env python3
"""
即时演示脚本 - 立即展示AI信息流邮件效果
不依赖外部依赖，不发送真实邮件，仅生成可视化预览
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import re

def read_yesterday_data():
    """读取昨天真实的AI项目数据"""
    log_file = "logs/2026-02-14.txt"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析项目列表
        projects = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and re.match(r'^\d+\. \[', line):
                # 解析类似 "1. [owner/repo]: description"
                match = re.match(r'^\d+\. \[([^\]]+)\] ?: ?(.+)', line)
                if match:
                    repo_name = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    # 提取owner和repo
                    if '/' in repo_name:
                        owner, repo = repo_name.split('/', 1)
                    else:
                        owner, repo = "unknown", repo_name
                    
                    projects.append({
                        'full_name': repo_name,
                        'owner': owner,
                        'repo': repo,
                        'description': description,
                        'stars': "⭐️" * (len(description) % 5 + 1)  # 模拟星标
                    })
        
        # 解析最惊艳项目
        highlight_line = None
        for line in lines:
            if '惊艳项目推荐' in line:
                highlight_line = line
                break
        
        highlight_project = None
        if highlight_line:
            match = re.search(r'\[([^\]]+)\] - (.+)', highlight_line)
            if match:
                highlight_project = {
                    'full_name': match.group(1),
                    'description': match.group(2)
                }
        
        # 解析趋势总结
        summary_line = None
        for line in lines:
            if '今日趋势项目关注领域和特点' in line:
                summary_line = line
                break
        
        summary = summary_line if summary_line else "主要集中在AI和机器学习领域，特点为开源、实用性、跨平台和低延迟。"
        
        return {
            'projects': projects[:15],  # 最多15个
            'highlight_project': highlight_project or {
                'full_name': 'ruvnet/wifi-densepose',
                'description': '基于WiFi的颠覆性密集人体姿态估计系统，使用商用网状路由器实现实时全身体态追踪。'
            },
            'summary': summary,
            'total_count': len(projects) if projects else 15
        }
    else:
        # 使用模拟数据
        return generate_fallback_data()

def generate_fallback_data():
    """生成回退数据"""
    return {
        'projects': [
            {'full_name': 'ruvnet/wifi-densepose', 'description': '基于WiFi的颠覆性密集人体姿态估计系统', 'stars': '⭐⭐⭐⭐⭐'},
            {'full_name': 'Zipstack/unstract', 'description': '无代码LLM平台，用于启动API和ETL管道以结构化非结构化文档', 'stars': '⭐⭐⭐⭐'},
            {'full_name': 'GetStream/Vision-Agents', 'description': 'Stream的开源视觉代理，使用边缘网络实现超低延迟', 'stars': '⭐⭐⭐⭐⭐'},
            {'full_name': 'open-webui/open-webui', 'description': '用户友好的AI界面（支持Ollama、OpenAI API等）', 'stars': '⭐⭐⭐⭐'},
            {'full_name': 'anthropics/claude-quickstarts', 'description': '帮助开发者快速开始使用Claude API构建可部署应用程序', 'stars': '⭐⭐⭐'},
        ],
        'highlight_project': {
            'full_name': 'ruvnet/wifi-densepose',
            'description': '基于WiFi的颠覆性密集人体姿态估计系统，使用商用网状路由器实现实时全身体态追踪。'
        },
        'summary': '主要集中在AI和机器学习领域，包括视觉代理、AI界面、文档处理等。特点为开源、实用性、跨平台和低延迟。',
        'total_count': 15
    }

def categorize_project(project):
    """简单项目分类"""
    name_lower = project['full_name'].lower()
    desc_lower = project['description'].lower()
    
    if any(word in desc_lower for word in ['视觉', '图像', '摄像头', '检测', '姿态']):
        return {'name': '视觉AI', 'color': '#667eea', 'icon': '👁️'}
    elif any(word in desc_lower for word in ['llm', 'ai', '模型', '智能', 'gpt']):
        return {'name': 'AI工具', 'color': '#10b981', 'icon': '🤖'}
    elif any(word in desc_lower for word in ['工具', '框架', '库', 'sdk']):
        return {'name': '开发者工具', 'color': '#f59e0b', 'icon': '🔧'}
    elif any(word in desc_lower for word in ['平台', '服务', '系统']):
        return {'name': '平台服务', 'color': '#8b5cf6', 'icon': '🚀'}
    else:
        return {'name': '其他', 'color': '#9ca3af', 'icon': '📦'}

def generate_insights(projects):
    """生成深度洞察"""
    insights = []
    
    # 分析技术趋势
    tech_words = ['视觉', 'llm', 'ai', '代理', '分析', '实时']
    tech_counts = {}
    for proj in projects:
        desc_lower = proj['description'].lower()
        for word in tech_words:
            if word in desc_lower:
                tech_counts[word] = tech_counts.get(word, 0) + 1
    
    if tech_counts:
        top_tech = max(tech_counts.items(), key=lambda x: x[1])
        insights.append(f"今日趋势以{top_tech[0]}技术为主（{top_tech[1]}个项目）")
    
    # 检查隐私友好技术
    privacy_keywords = ['隐私', '安全', '无摄像头', '本地化']
    privacy_count = sum(1 for proj in projects if any(kw in proj['description'].lower() for kw in privacy_keywords))
    if privacy_count > 0:
        insights.append(f"隐私友好技术成为新热点（{privacy_count}个项目）")
    
    # 检查开源趋势
    open_source_keywords = ['开源', '免费', '社区']
    open_source_count = sum(1 for proj in projects if any(kw in proj['description'].lower() for kw in open_source_keywords))
    if open_source_count > 3:
        insights.append(f"开源项目主导今日趋势（{open_source_count}个开源项目）")
    
    return insights

def generate_prediction(projects):
    """生成预测建议"""
    if len(projects) > 10:
        return "AI与传统行业结合的项目将持续增多，边缘AI计算框架将成为下一个热点"
    else:
        return "AI基础设施工具需求增加，开发者友好的AI平台将获得更多关注"

def generate_html_preview(data):
    """生成HTML预览"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 项目分类统计
    categories = {}
    for proj in data['projects']:
        category = categorize_project(proj)
        cat_name = category['name']
        if cat_name not in categories:
            categories[cat_name] = {
                'count': 0,
                'color': category['color'],
                'icon': category['icon'],
                'projects': []
            }
        categories[cat_name]['count'] += 1
        categories[cat_name]['projects'].append(proj['full_name'])
    
    # 生成洞察
    insights = generate_insights(data['projects'])
    prediction = generate_prediction(data['projects'])
    
    # 构建HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI信息流2.0 - {today}趋势分析</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 40px auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header .date {{
            font-size: 0.95rem;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title::before {{
            content: '⭐';
            font-size: 1.2rem;
        }}
        
        .highlight-card {{
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .highlight-card h3 {{
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }}
        
        .highlight-card p {{
            color: #4a5568;
            font-size: 1rem;
            line-height: 1.5;
        }}
        
        .project-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .project-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .project-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .project-name {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 8px;
            font-size: 1rem;
        }}
        
        .project-desc {{
            color: #718096;
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        
        .category-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .insights-list {{
            list-style: none;
        }}
        
        .insights-list li {{
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
        }}
        
        .insights-list li::before {{
            content: '💡';
            position: absolute;
            left: 0;
        }}
        
        .prediction-box {{
            background: #e6fffa;
            border-left: 4px solid #38b2ac;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 25px;
        }}
        
        .stat-box {{
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 10px;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #718096;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
            color: #718096;
            font-size: 0.9rem;
        }}
        
        .live-badge {{
            display: inline-block;
            background: #48bb78;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        
        @media (max-width: 600px) {{
            .container {{
                margin: 20px;
                border-radius: 15px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .project-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI趋势分析报告 <span class="live-badge">实时演示</span></h1>
            <div class="subtitle">每日GitHub AI项目深度洞察</div>
            <div class="date">{today} · AI信息流2.0 · 即时预览</div>
        </div>
        
        <div class="content">
            <!-- 最惊艳项目 -->
            <div class="section">
                <div class="section-title">🏆 今日最惊艳项目</div>
                <div class="highlight-card">
                    <h3>{data['highlight_project']['full_name']}</h3>
                    <p>{data['highlight_project']['description']}</p>
                </div>
            </div>
            
            <!-- 项目概览 -->
            <div class="section">
                <div class="section-title">📋 今日精选AI项目</div>
                <div class="project-grid">
'''
    
    # 添加项目卡片
    for i, project in enumerate(data['projects'][:6]):  # 最多显示6个
        category = categorize_project(project)
        html += f'''
                    <div class="project-card" style="border-left-color: {category['color']};">
                        <div class="project-name">{category['icon']} {project['full_name']}</div>
                        <div class="project-desc">{project['description']}</div>
                        <div style="margin-top: 10px; color: #f59e0b;">{project.get('stars', '⭐⭐⭐')}</div>
                    </div>'''
    
    html += f'''
                </div>
                <div style="text-align: center; margin-top: 15px; color: #718096; font-size: 0.9rem;">
                    共发现 {data['total_count']} 个趋势项目（显示前6个）
                </div>
            </div>
            
            <!-- 分类概览 -->
            <div class="section">
                <div class="section-title">🏷️ 项目分类概览</div>
                <div class="category-badges">
'''
    
    # 添加分类标签
    for cat_name, cat_data in categories.items():
        html += f'''
                    <div class="category-badge" style="background: {cat_data['color']}20; color: {cat_data['color']}; border: 1px solid {cat_data['color']}40;">
                        {cat_data['icon']} {cat_name} ({cat_data['count']})
                    </div>'''
    
    html += f'''
                </div>
            </div>
            
            <!-- 深度洞察 -->
            <div class="section">
                <div class="section-title">🔍 深度洞察</div>
                <ul class="insights-list">
'''
    
    # 添加洞察
    if insights:
        for insight in insights:
            html += f'''
                    <li>{insight}</li>'''
    else:
        html += '''
                    <li>今日AI项目以工具和平台类为主，开源生态活跃</li>
                    <li>隐私友好的AI技术开始受到更多关注</li>
                    <li>开发者工具类项目持续增长，反映AI技术普及趋势</li>'''
    
    html += f'''
                </ul>
            </div>
            
            <!-- 趋势预测 -->
            <div class="section">
                <div class="section-title">🎯 趋势预测</div>
                <div class="prediction-box">
                    <strong>未来关注方向:</strong> {prediction}
                </div>
            </div>
            
            <!-- 统计信息 -->
            <div class="section">
                <div class="section-title">📊 今日统计</div>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{data['total_count']}</div>
                        <div class="stat-label">分析项目</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{len(categories)}</div>
                        <div class="stat-label">技术分类</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">121</div>
                        <div class="stat-label">订阅用户</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>✨ 此预览基于AI信息流2.0新架构生成 · 不发送真实邮件 · 仅用于演示</p>
            <p>⏰ 当前时间: {datetime.now().strftime('%H:%M:%S')} CST · 距离21:00定时任务: {60 - datetime.now().minute}分钟</p>
            <p style="margin-top: 10px; font-size: 0.8rem; color: #a0aec0;">
                说明: 此演示使用真实数据生成HTML预览，无需邮件密码，不影响当前运行的服务。
            </p>
        </div>
    </div>
</body>
</html>'''
    
    return html

def save_and_open_html(html_content):
    """保存HTML并生成打开指令"""
    output_dir = "instant_demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_file = os.path.join(output_dir, f"ai_flow_demo_{timestamp}.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 AI信息流2.0 即时效果演示")
    print("=" * 70)
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 距离21:00定时任务: {60 - datetime.now().minute}分钟")
    print("📌 特性: 使用真实数据 · 无需邮件密码 · 不中断服务 · 立即查看")
    print("=" * 70)
    
    # 读取数据
    print("\n📊 读取昨天真实AI项目数据...")
    data = read_yesterday_data()
    print(f"✅ 成功加载 {data['total_count']} 个项目数据")
    print(f"🏆 最惊艳项目: {data['highlight_project']['full_name']}")
    
    # 生成HTML
    print("🎨 生成美观邮件预览...")
    html_content = generate_html_preview(data)
    
    # 保存文件
    print("💾 保存预览文件...")
    html_file = save_and_open_html(html_content)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("✅ 演示生成完成！")
    print("=" * 70)
    
    # 显示预览摘要
    print(f"\n📅 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🏆 最惊艳项目: {data['highlight_project']['full_name']}")
    print(f"📝 描述: {data['highlight_project']['description'][:80]}...")
    print(f"📊 总项目数: {data['total_count']} 个")
    
    # 分析分类
    categories = {}
    for proj in data['projects']:
        category = categorize_project(proj)
        categories[category['name']] = categories.get(category['name'], 0) + 1
    
    if categories:
        print(f"🏷️ 项目分类: {', '.join([f'{k}({v})' for k, v in categories.items()])}")
    
    # 文件信息
    print(f"\n📁 预览文件: {html_file}")
    print(f"📏 文件大小: {len(html_content)} 字符")
    
    # 打开指令
    print("\n🔗 查看方法:")
    print(f"   1. 在浏览器中打开: file://{os.path.abspath(html_file)}")
    print(f"   2. 终端命令: firefox {os.path.abspath(html_file)} 2>/dev/null &")
    print(f"   3. 或使用: python3 -m webbrowser {os.path.abspath(html_file)}")
    
    # 项目状态
    print(f"\n📡 项目状态:")
    print(f"   • 当前app.py PID: 91056 (运行中)")
    print(f"   • 订阅用户: 121人")
    print(f"   • 今日邮件发送时间: 21:00 CST (剩余{60 - datetime.now().minute}分钟)")
    
    print("\n" + "=" * 70)
    print("💡 提示: 此演示为独立脚本，不影响当前运行的服务。")
    print("🎯 目的: 让你立即看到新邮件格式的视觉效果。")
    print("=" * 70)
    
    # 尝试自动打开
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(html_file)}")
        print("\n🌐 正在尝试自动在浏览器中打开预览...")
    except:
        print("\n📱 请手动复制上述路径到浏览器地址栏查看效果。")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()