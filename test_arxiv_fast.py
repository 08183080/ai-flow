#!/usr/bin/env python3
"""
arXiv快速测试 - 爬取少量数据并发送
"""

import os
import sys
import datetime
import yagmail
import arxiv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from arxiv_app import translate_and_summarize, get_ai_analysis, send_email

def get_today_str() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d')

def scrape_arxiv_fast(max_results: int = 5):
    """快速爬取少量论文用于测试"""
    print(f"🚀 快速爬取arXiv论文（{max_results}篇）...")
    
    categories = ['cs.AI', 'cs.LG']
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query='cat:cs.AI OR cat:cs.LG',
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        for result in client.results(search):
            paper = {
                'id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [str(author) for author in result.authors],
                'summary': result.summary,
                'published': result.published.strftime('%Y-%m-%d %H:%M:%S'),
                'primary_category': result.primary_category if hasattr(result, 'primary_category') else 'cs.AI',
                'pdf_url': result.pdf_url
            }
            papers.append(paper)
            print(f"  已获取: {paper['title'][:60]}...")
            
        print(f"✅ 成功获取 {len(papers)} 篇论文")
        return papers
    except Exception as e:
        print(f"❌ arXiv爬取失败: {e}")
        return []

def format_fast_email(papers):
    """快速格式化邮件"""
    today = get_today_str()
    content = f"""🚀 arXiv AI/ML论文测试版 - {today} {datetime.datetime.now().strftime('%H:%M')}
{"="*60}

📚 测试精选（{len(papers)}篇）：
{"="*60}

"""
    
    for i, paper in enumerate(papers, 1):
        # 简单作者处理
        authors = paper['authors']
        if len(authors) > 2:
            author_str = f"{authors[0].split()[-1]} 等"
        else:
            author_names = [a.split()[-1] for a in authors[:2]]
            author_str = ", ".join(author_names)
        
        # 翻译摘要（精简版）
        summary_cn = translate_and_summarize(paper['summary'], max_length=100)
        
        content += f"""{i}. 【{paper['primary_category']}】{paper['title']}
    👤 {author_str} | 📅 {paper['published'][:10]}
    📖 {summary_cn}
    🔗 https://arxiv.org/abs/{paper['id']}
    
"""
    
    # 简单趋势分析
    content += f"""{"="*60}

💡 趋势分析：
今日AI研究聚焦于大模型、多模态学习与强化学习等前沿方向。

{"="*60}

🤖 我是谢小果，openclaw机器人，谢苹果的数字员工。
📬 此邮件每天下午4点自动发送，同步到GitHub存档。
"""
    
    return content

def main():
    print("⚡ arXiv快速测试开始...")
    
    # 1. 快速爬取
    papers = scrape_arxiv_fast(5)
    if not papers:
        print("❌ 未获取到论文，测试终止")
        return False
    
    # 2. 格式化邮件
    content = format_fast_email(papers)
    
    # 3. 发送邮件
    today = get_today_str()
    subject = f"🚀 arXiv AI/ML论文测试 - {today} {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    success = send_email(content, subject=subject)
    
    if success:
        print("🎉 测试邮件已发送！请检查邮箱")
        
        # 保存日志
        log_file = f"arxiv_logs/{get_today_str()}_test.txt"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 日志保存到: {log_file}")
    else:
        print("❌ 邮件发送失败")
    
    return success

if __name__ == "__main__":
    # 设置超时时间为120秒
    import signal
    signal.alarm(120)
    
    try:
        main()
    except Exception as e:
        print(f"❌ 测试异常: {e}")