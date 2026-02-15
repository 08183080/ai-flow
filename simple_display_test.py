#!/usr/bin/env python3
import os
import requests
from pyquery import PyQuery as pq
import codecs
import datetime

def scrape_simple_display(language='python'):
    """爬取GitHub Trending并返回简单格式的项目列表"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    
    url = f'https://github.com/trending/{language}'
    
    # 尝试直接IP连接
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except:
        # 如果域名连接失败，尝试IP直连
        r = requests.get('https://140.82.121.3/trending/python', 
                        headers={**HEADERS, 'Host': 'github.com'}, 
                        timeout=30, verify=False)
    
    print(f'状态码: {r.status_code}')
    
    if r.status_code != 200:
        return None
    
    d = pq(r.content)
    items = d('div.Box article.Box-row')
    
    projects = []
    for index, item in enumerate(items, start=1):
        i = pq(item)
        title = i(".lh-condensed a").text()
        description = i("p.col-9").text()
        url = i(".lh-condensed a").attr("href")
        url = "https://github.com" + url
        
        # 提取仓库名（去除作者名）
        repo_name = title.strip().split('/')[-1].strip() if '/' in title else title.strip()
        
        projects.append({
            'index': index,
            'title': title.strip(),
            'repo_name': repo_name,
            'description': description.strip(),
            'url': url
        })
    
    return projects

def create_html_display(projects):
    """创建简单的HTML展示页面"""
    if not projects:
        return "<html><body><h2>没有获取到项目数据</h2></body></html>"
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending Python 项目</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background-color: #f6f8fa;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            padding: 30px;
        }
        h1 {
            color: #0366d6;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .project {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eaecef;
        }
        .project:last-child {
            border-bottom: none;
        }
        .project-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .project-title a {
            color: #0366d6;
            text-decoration: none;
        }
        .project-title a:hover {
            text-decoration: underline;
        }
        .project-description {
            color: #586069;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .project-url {
            color: #6a737d;
            font-size: 12px;
            word-break: break-all;
        }
        .index {
            display: inline-block;
            background-color: #f1f8ff;
            color: #0366d6;
            font-size: 12px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 8px;
        }
        .date {
            color: #6a737d;
            font-size: 14px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 GitHub Trending Python 项目</h1>
        <div class="date">更新时间: ''' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div>
'''
    
    for project in projects:
        html += f'''
        <div class="project">
            <div class="project-title">
                <span class="index">#{project['index']}</span>
                <a href="{project['url']}" target="_blank">{project['repo_name']}</a>
                <span style="color: #6a737d; font-size: 14px;">({project['title']})</span>
            </div>
            <div class="project-description">{project['description'] or '无描述'}</div>
            <div class="project-url">🔗 {project['url']}</div>
        </div>
        '''
    
    html += '''
    </div>
</body>
</html>'''
    
    return html

def create_text_display(projects):
    """创建纯文本展示"""
    if not projects:
        return "没有获取到项目数据"
    
    text = f"GitHub Trending Python 项目 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 60 + "\n\n"
    
    for project in projects:
        text += f"#{project['index']} {project['repo_name']}\n"
        text += f"   仓库: {project['title']}\n"
        text += f"   链接: {project['url']}\n"
        text += f"   描述: {project['description'] or '无描述'}\n"
        text += "-" * 40 + "\n"
    
    return text

def test_scrape_and_display():
    """测试爬取和展示功能"""
    print("🚀 开始爬取GitHub Trending Python项目...")
    projects = scrape_simple_display('python')
    
    if projects:
        print(f"✅ 成功爬取 {len(projects)} 个项目")
        
        # 创建纯文本展示
        text_display = create_text_display(projects)
        print("\n" + "="*60)
        print("纯文本预览（前3个项目）:")
        print("="*60)
        lines = text_display.split('\n')[:15]  # 只显示前15行
        print('\n'.join(lines))
        
        # 创建HTML展示
        html_display = create_html_display(projects)
        
        # 保存HTML文件用于预览
        html_filename = f"/root/ai-flow/simple_display_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_display)
        
        print(f"\n✅ HTML预览已保存到: {html_filename}")
        print(f"   用浏览器打开查看效果: file://{html_filename}")
        
        return {
            'projects': projects,
            'text': text_display,
            'html': html_display,
            'html_file': html_filename
        }
    else:
        print("❌ 爬取失败")
        return None

if __name__ == '__main__':
    test_scrape_and_display()