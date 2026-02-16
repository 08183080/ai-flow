#!/usr/bin/env python3
"""
arXiv论文信息流程序
独立于GitHub项目系统，每天下午4:00（16:00）自动运行
获取AI/ML领域最新论文，发送给订阅用户
"""

import os
import sys
import json
import datetime
import yagmail
import arxiv
from typing import List, Dict
import requests

# 导入现有配置
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_today_str() -> str:
    """返回当前日期字符串"""
    return datetime.datetime.now().strftime('%Y-%m-%d')

def scrape_arxiv_papers(categories: List[str] = None, max_results: int = 20) -> List[Dict]:
    """
    从arXiv爬取指定类别的最新论文
    
    Args:
        categories: arXiv类别列表，如['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'stat.ML']
        max_results: 最大获取数量
        
    Returns:
        论文信息列表
    """
    if categories is None:
        categories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'stat.ML']
    
    print(f"🚀 开始爬取arXiv论文，类别: {categories}")
    
    # 构建查询字符串
    query_parts = []
    for cat in categories:
        query_parts.append(f'cat:{cat}')
    query = ' OR '.join(query_parts)
    
    # 搜索最新论文
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    try:
        for result in client.results(search):
            paper = {
                'id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [str(author) for author in result.authors],
                'summary': result.summary,
                'published': result.published.strftime('%Y-%m-%d %H:%M:%S'),
                'updated': result.updated.strftime('%Y-%m-%d %H:%M:%S') if result.updated else '',
                'pdf_url': result.pdf_url,
                'primary_category': result.primary_category if hasattr(result, 'primary_category') else '',
                'categories': result.categories if hasattr(result, 'categories') else [],
                'comment': result.comment if hasattr(result, 'comment') and result.comment else '',
                'journal_ref': result.journal_ref if hasattr(result, 'journal_ref') and result.journal_ref else ''
            }
            papers.append(paper)
            print(f"  已获取: {paper['title'][:50]}...")
            
    except Exception as e:
        print(f"❌ arXiv爬取失败: {e}")
    
    print(f"✅ 成功获取 {len(papers)} 篇论文")
    return papers

def select_top_papers(papers: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    精选top_n篇论文
    基于：新鲜度、标题重要性、摘要完整性
    """
    if len(papers) <= top_n:
        return papers
    
    # 简单筛选：优先考虑今天或昨天的论文
    today = datetime.datetime.now().date()
    selected = []
    others = []
    
    for paper in papers:
        try:
            paper_date = datetime.datetime.strptime(paper['published'][:10], '%Y-%m-%d').date()
            days_old = (today - paper_date).days
            if days_old <= 2:
                selected.append((days_old, paper))
            else:
                others.append((days_old, paper))
        except:
            others.append((99, paper))
    
    # 按新鲜度排序
    selected.sort(key=lambda x: x[0])
    others.sort(key=lambda x: x[0])
    
    # 组合结果
    result = []
    for days_old, paper in selected:
        result.append(paper)
        if len(result) >= top_n:
            break
    
    if len(result) < top_n:
        for days_old, paper in others:
            result.append(paper)
            if len(result) >= top_n:
                break
    
    return result

def get_ai_analysis(papers: List[Dict]) -> str:
    """
    使用智谱AI分析论文趋势
    
    Args:
        papers: 论文列表
        
    Returns:
        AI分析报告
    """
    api_key = os.environ.get('ZHIPUAI_API_KEY')
    if not api_key:
        print("⚠️ 未设置ZHIPUAI_API_KEY环境变量，跳过AI分析")
        return "今日arXiv论文精选"
    
    # 构建论文摘要
    papers_summary = ""
    for i, paper in enumerate(papers[:5], 1):  # 只取前5篇进行分析
        papers_summary += f"{i}. {paper['title']}\n   摘要: {paper['summary'][:200]}...\n"
    
    prompt = f"""你是一个AI研究专家，请分析以下arXiv论文并回答：
1. 这些论文主要集中在哪些研究主题？
2. 有什么技术突破或创新点？
3. 对AI/ML领域的发展有什么启示？
4. 用简洁的中文总结今日AI研究趋势。

论文列表：
{papers_summary}

请用中文回答，保持简洁专业。"""
    
    try:
        from zhipuai import ZhipuAI
        client = ZhipuAI(api_key=api_key)
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        analysis = response.choices[0].message.content.strip()
        print("✅ AI分析完成")
        return analysis
    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        return "今日arXiv论文趋势：AI/ML领域持续快速发展，关注大模型、多模态、强化学习等前沿方向。"

def translate_and_summarize(text: str, max_length: int = 150) -> str:
    """
    使用智谱AI翻译并精简文本
    
    Args:
        text: 英文文本
        max_length: 最大长度
        
    Returns:
        翻译并精简后的中文文本
    """
    api_key = os.environ.get('ZHIPUAI_API_KEY')
    if not api_key:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    try:
        from zhipuai import ZhipuAI
        client = ZhipuAI(api_key=api_key)
        
        prompt = f"""请将以下英文论文摘要翻译成中文，并精简到{max_length}字以内：
        
{text}

要求：
1. 准确翻译专业术语
2. 保持学术严谨性
3. 精简摘要，突出核心贡献
4. 输出纯中文文本，不加引号或额外说明"""

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        translated = response.choices[0].message.content.strip()
        
        # 进一步精简
        if len(translated) > max_length:
            # 简单截断，保留完整句子
            sentences = translated.split('。')
            result = []
            current_length = 0
            for sent in sentences:
                if sent:
                    sent_with_period = sent + '。'
                    if current_length + len(sent_with_period) <= max_length:
                        result.append(sent_with_period)
                        current_length += len(sent_with_period)
                    else:
                        break
            translated = ''.join(result)
            if not translated:
                translated = translated[:max_length] + "..."
        
        return translated
    except Exception as e:
        print(f"⚠️ 翻译失败，使用原文本: {e}")
        # 回退：简单截取
        return text[:max_length] + "..." if len(text) > max_length else text

def format_paper_email(papers: List[Dict], analysis: str = "") -> str:
    """
    格式化论文邮件内容（简洁翻译版）
    
    Args:
        papers: 论文列表
        analysis: AI分析结果
        
    Returns:
        格式化后的邮件内容
    """
    today = get_today_str()
    content = f"""🚀 arXiv AI/ML论文精选 - {today} {datetime.datetime.now().strftime('%H:%M')}
{"="*60}

📚 今日精选（{len(papers)}篇）：
{"="*60}

"""
    
    for i, paper in enumerate(papers, 1):
        # 提取作者姓氏
        authors = paper['authors']
        if len(authors) > 2:
            author_str = f"{authors[0].split()[-1]} 等"  # 取姓氏
        else:
            # 只取姓氏
            author_names = [a.split()[-1] for a in authors[:2]]
            author_str = ", ".join(author_names)
        
        # 清理标题
        title = paper['title'].replace('\n', ' ')
        
        # 翻译并精简摘要
        summary_en = paper['summary']
        summary_cn = translate_and_summarize(summary_en, max_length=120)
        
        content += f"""{i}. 【{paper['primary_category']}】{title}
    👤 {author_str} | 📅 {paper['published'][:10]}
    📖 {summary_cn}
    🔗 https://arxiv.org/abs/{paper['id']}
    
"""
    
    content += f"""{"="*60}

💡 趋势分析：
{analysis}

{"="*60}

🤖 我是谢小果，openclaw机器人，谢苹果的数字员工。
📬 此邮件每天下午4点自动发送，同步到GitHub存档。

"""
    
    return content

def send_email(content: str, to: str = None, subject: str = None) -> bool:
    """
    发送邮件
    
    Args:
        content: 邮件内容
        to: 收件人，默认为用户邮箱
        subject: 邮件主题
        
    Returns:
        是否成功
    """
    # 获取邮箱配置
    email = '19121220286@163.com'
    pwd = os.environ.get('WANGYI_EMAIL_AUTH')
    
    if not pwd:
        print("❌ 未设置WANGYI_EMAIL_AUTH环境变量")
        return False
    
    # 设置收件人
    if to is None:
        to = 'pxxhl@qq.com'  # 用户邮箱
    
    if subject is None:
        today = get_today_str()
        subject = f"🚀 arXiv AI/ML论文精选 - {today} {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    try:
        # 发送邮件
        yag = yagmail.SMTP(email, pwd, host='smtp.163.com')
        yag.send(to=to, subject=subject, contents=content)
        print(f"✅ 邮件已发送到: {to}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def send_to_all_subscribers(content: str, subject: str = None) -> bool:
    """
    发送给所有订阅用户
    """
    emails_file = 'emails.txt'
    if not os.path.exists(emails_file):
        print(f"⚠️ 订阅列表不存在: {emails_file}")
        return False
    
    try:
        with open(emails_file, 'r', encoding='utf-8') as f:
            emails = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ 读取订阅列表失败: {e}")
        return False
    
    print(f"📧 准备发送给 {len(emails)} 个订阅用户")
    
    # 用户要求立即群发给所有用户
    success_count = 0
    for i, email in enumerate(emails, 1):
        print(f"  正在发送 ({i}/{len(emails)}) → {email}")
        if send_email(content, to=email, subject=subject):
            success_count += 1
            if i < len(emails):  # 不是最后一个
                import time
                time.sleep(2)  # 避免发送过快被限制
    
    print(f"📊 发送完成: {success_count}/{len(emails)} 成功")
    return success_count > 0

def daily_task():
    """每日任务：爬取、分析、发送"""
    print(f"📅 {get_today_str()} arXiv论文信息流任务开始...")
    
    # 1. 爬取论文
    papers = scrape_arxiv_papers(
        categories=['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'stat.ML'],
        max_results=25
    )
    
    if not papers:
        print("❌ 未获取到论文，任务终止")
        return False
    
    # 2. 精选10篇
    selected_papers = select_top_papers(papers, top_n=10)
    print(f"🎯 精选 {len(selected_papers)} 篇论文")
    
    # 3. AI分析
    analysis = get_ai_analysis(selected_papers)
    
    # 4. 格式化邮件
    content = format_paper_email(selected_papers, analysis)
    
    # 5. 发送邮件
    today = get_today_str()
    subject = f"🚀 arXiv AI/ML论文精选 - {today} {datetime.datetime.now().strftime('%H:%M:%S')}"
    success = send_to_all_subscribers(content, subject)
    
    # 6. 保存日志
    log_file = f"arxiv_logs/{get_today_str()}.txt"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ arXiv论文任务完成，日志保存到: {log_file}")
    return success

def test_immediate():
    """立即测试发送"""
    print("⚡ 立即测试arXiv论文信息流...")
    
    # 创建日志目录
    os.makedirs('arxiv_logs', exist_ok=True)
    
    # 执行任务
    success = daily_task()
    
    if success:
        print("🎉 测试成功！请检查邮箱")
    else:
        print("❌ 测试失败")
    
    return success

def run_scheduled():
    """定时运行模式"""
    import schedule
    import time
    
    print("⏰ arXiv论文信息流定时服务启动...")
    print("📅 配置：每天16:00 (CST) 自动执行")
    
    # 设置定时任务
    schedule.every().day.at("16:00").do(daily_task)
    
    # 立即执行一次（现在16:04，补发今天的）
    print("🚀 立即执行今天16:00的任务...")
    daily_task()
    
    print("✅ arXiv定时服务已启动，等待下一次执行...")
    
    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # 立即执行测试并启动定时服务
    print("="*60)
    print("🚀 arXiv论文信息流 v1.0 - 立即部署")
    print("="*60)
    
    # 立即执行一次（群发给所有用户）
    test_immediate()
    
    # 启动定时服务
    print("\n" + "="*60)
    print("⚙️ 启动定时服务...")
    print("="*60)
    run_scheduled()