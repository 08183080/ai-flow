#!/usr/bin/env python3
import os
import yagmail
import datetime
import requests
import schedule
import time
from pyquery import PyQuery as pq
import codecs

def get_emails(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

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
        r = requests.get(url, headers=HEADERS, timeout=45)
    except Exception as e:
        print(f"域名连接失败: {e}")
        # 如果域名连接失败，尝试IP直连
        try:
            r = requests.get('https://140.82.121.3/trending/python', 
                            headers={**HEADERS, 'Host': 'github.com'}, 
                            timeout=45, verify=False)
            print("IP直连成功")
        except Exception as e2:
            print(f"IP直连也失败: {e2}")
            return None
    
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

def create_text_display(projects):
    """创建纯文本展示"""
    if not projects:
        return "没有获取到项目数据"
    
    text = f"🚀 GitHub Trending Python 项目 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 70 + "\n\n"
    
    for project in projects:
        text += f"#{project['index']:2d} {project['repo_name']}\n"
        text += f"   仓库: {project['title']}\n"
        text += f"   链接: {project['url']}\n"
        text += f"   描述: {project['description'] or '无描述'}\n"
        text += "-" * 50 + "\n"
    
    # 添加用户要求的自我介绍
    text += "\n" + "=" * 70 + "\n"
    text += "💡 我是谢小果，是openclaw机器人，谢苹果的数字员工，从今天开始由我这个智能体负责AI信息流项目的所有维护。\n"
    
    return text

def send_email(src, dst, subject, contents, attachments=None):
    pwd = os.environ.get('WANGYI_EMAIL_AUTH')
    
    # 确保密码是字符串类型
    if isinstance(pwd, bytes):
        pwd = pwd.decode('utf-8')
    
    # 直接使用SMTP，不依赖keyring
    yag = yagmail.SMTP(user=src, password=pwd, host='smtp.163.com', port='465')
    
    if attachments:
        yag.send(to=dst, subject=subject, contents=contents, attachments=attachments)
    else:
        yag.send(to=dst, subject=subject, contents=contents)
    
    yag.close()

def send_emails(src, tos, subject, contents, attachments=None):
    for to in tos:
        send_email(src, to, subject, contents, attachments)

def simple_job():
    """简单的任务：爬取项目并生成文本展示"""
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    os.makedirs('logs', exist_ok=True)
    txt_filename = f'logs/{strdate}_simple.txt'
    
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} 开始简单爬取任务...')
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        try:
            print(f'第 {attempts+1} 次尝试爬取数据...')
            projects = scrape_simple_display('python')
            
            if projects:
                print(f'✅ 成功爬取 {len(projects)} 个项目')
                
                # 生成文本内容
                text_content = create_text_display(projects)
                
                # 保存到文件
                with open(txt_filename, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                return {
                    'text': text_content,
                    'projects': projects,
                    'filename': txt_filename
                }
            else:
                print('❌ 爬取失败，项目列表为空')
                attempts += 1
                if attempts < max_attempts:
                    time.sleep(60)  # 等待1分钟后重试
        
        except Exception as e:
            print(f'❌ 尝试 {attempts+1} 失败: {e}')
            attempts += 1
            if attempts < max_attempts:
                time.sleep(60)  # 等待1分钟后重试
    
    print(f'❌ 所有 {max_attempts} 次尝试均失败')
    return None

def simple_daily_task():
    """简单的每日任务：爬取项目并发送邮件"""
    try:
        result = simple_job()
        
        if not result:
            print('❌ 任务执行失败，无法发送邮件')
            return
        
        src = '19121220286@163.com'
        tos = get_emails('emails.txt')
        subject = f'GitHub Trending Python 项目 - {datetime.datetime.now().strftime("%Y-%m-%d")}'
        contents = result['text']
        
        print(f'📧 准备发送邮件给 {len(tos)} 个订阅用户...')
        send_emails(src, tos, subject, contents)
        print(f'✅ 邮件发送完成')
        
    except Exception as e:
        print(f'❌ 每日任务执行失败: {e}')

def test_send_to_user(email='pxxhl@qq.com'):
    """测试发送邮件到指定用户"""
    try:
        result = simple_job()
        
        if not result:
            print('❌ 测试失败：无法获取项目数据')
            return False
        
        src = '19121220286@163.com'
        subject = f'GitHub Trending Python 项目 - 测试 {datetime.datetime.now().strftime("%H:%M:%S")}'
        contents = result['text']
        
        print(f'📧 测试发送邮件到 {email}...')
        send_email(src, email, subject, contents)
        print(f'✅ 测试邮件已发送到 {email}')
        
        return True
        
    except Exception as e:
        print(f'❌ 测试发送失败: {e}')
        return False

if __name__ == '__main__':
    # 立即测试发送给用户
    print("🚀 立即测试简单展示版本...")
    success = test_send_to_user()
    
    if success:
        print("\n✅ 测试成功！")
        print("💡 如果你对邮件格式满意，我可以：")
        print("   1. 停止当前复杂版本的app.py")
        print("   2. 启动这个简单版本作为主程序")
        print("   3. 设置定时任务（默认21:00）")
    else:
        print("\n❌ 测试失败，请查看上面的错误信息")