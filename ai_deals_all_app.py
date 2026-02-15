import os
import yagmail
import datetime
import codecs
import requests
import schedule
import time
from zhipuai import ZhipuAI
from pyquery import PyQuery as pq


def get_contents(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_emails(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def get_ai_analysis(path):
    try:
        client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY"))
        deals = get_contents(path)
        print(f'ai is reading, the info is:\n{deals[:500]}...')

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "你是一个AI优惠信息分析专家。负责分析来自Hacker News、GitHub、V2EX、国内AI平台的优惠信息。筛选出真实有效的优惠，过滤掉无关信息。将内容翻译成中文，输出整齐精致的HTML格式。使用HTML标签：<h2>、<h3>、<ul>、<li>、<a>、<strong>等。重点标注：(1)哪些平台/产品有优惠 (2)优惠力度 (3)如何获取 (4)截止时间。按优惠力度排序，推荐3个最值得薅羊毛的机会。语言简洁实用。最后一句话：我是谢苹果，AI信息流2.0，让你的token用不完。"},
                {"role": "user", "content": f'{deals}'}
            ],
        )

        ans = response.choices[0].message.content
        return ans
    except Exception as e:
        print(f'when ai analyze, {e} occurs...')
        return None


def convert_to_html_email(content):
    """
    将AI生成的内容转换为美观的HTML邮件格式
    """
    # 去掉可能存在的```html标签
    content = content.strip()
    if content.startswith('```html'):
        content = content[7:]  # 去掉开头的```html
    if content.endswith('```'):
        content = content[:-3]  # 去掉结尾的```
    content = content.strip()

    # 如果AI已经返回HTML，直接使用
    if '<html>' in content or '<h2>' in content:
        html_content = content
    else:
        # 否则进行简单的Markdown到HTML转换
        html_content = content.replace('\n', '<br>')

    # 包装在邮件模板中
    html_email = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #3498db;
                margin-top: 30px;
                border-left: 4px solid #3498db;
                padding-left: 10px;
            }}
            h3 {{
                color: #e74c3c;
                margin-top: 20px;
            }}
            ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            li {{
                background-color: #ecf0f1;
                margin: 10px 0;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                text-align: center;
                color: #7f8c8d;
                font-size: 14px;
            }}
            strong {{
                color: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 今日AI薅羊毛全网汇总</h1>
            {html_content}
            <div class="footer">
                <p>📧 这是一封自动生成的邮件</p>
                <p>如有问题，请联系：19121220286@163.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_email


def createtext(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('')


def scrape_hackernews():
    """
    爬取Hacker News上AI相关的优惠信息
    """
    print("\n=== 开始爬取 Hacker News ===")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        search_queries = [
            'AI free', 'GPT free', 'LLM free', 'AI API free',
            'ChatGPT deal', 'AI launch', 'AI beta', 'OpenAI credit',
            'Claude free', 'AI token', 'AI discount', 'AI promo'
        ]

        all_posts = []

        for query in search_queries:
            try:
                url = f'https://hn.algolia.com/api/v1/search?query={query}&tags=story&numericFilters=created_at_i>{int(time.time()) - 7*24*3600}'
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', [])

                    for hit in hits:
                        # 安全获取objectID
                        object_id = hit.get('objectID', '')
                        if not object_id:
                            continue

                        # 检查是否已存在（使用objectID去重）
                        if any(p.get('objectID') == object_id for p in all_posts):
                            continue

                        title = hit.get('title', '').lower()
                        ai_keywords = ['ai', 'gpt', 'llm', 'chatgpt', 'claude', 'openai', 'model', 'api']
                        deal_keywords = ['free', 'deal', 'discount', 'promo', 'credit', 'trial', 'launch', 'beta']

                        has_ai = any(kw in title for kw in ai_keywords)
                        has_deal = any(kw in title for kw in deal_keywords)

                        if has_ai and has_deal:
                            all_posts.append({
                                'source': 'Hacker News',
                                'title': hit.get('title', ''),
                                'url': hit.get('url', f"https://news.ycombinator.com/item?id={object_id}"),
                                'score': hit.get('points', 0),
                                'objectID': object_id,  # 保存objectID用于去重
                            })

                time.sleep(1)
            except Exception as e:
                print(f'Error searching HN for {query}: {e}')
                continue

        all_posts.sort(key=lambda x: x['score'], reverse=True)
        print(f"Hacker News: 找到 {len(all_posts[:15])} 条相关信息")
        return all_posts[:15]

    except Exception as e:
        print(f'Error in scrape_hackernews: {e}')
        return []


def scrape_github_awesome():
    """
    爬取GitHub上的Awesome列表，寻找免费AI资源
    """
    print("\n=== 开始爬取 GitHub Awesome列表 ===")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 知名的AI资源列表
        awesome_repos = [
            'LiLittleCat/awesome-free-chatgpt',
            'sindresorhus/awesome-chatgpt',
            'f/awesome-chatgpt-prompts',
            'humanloop/awesome-chatgpt',
        ]

        all_items = []

        for repo in awesome_repos:
            try:
                # 获取README内容
                url = f'https://api.github.com/repos/{repo}/readme'
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    # 也可以直接爬取网页版
                    readme_url = f'https://github.com/{repo}'
                    page_response = requests.get(readme_url, headers=headers, timeout=10)

                    if page_response.status_code == 200:
                        d = pq(page_response.content)
                        # 查找包含free, api, token等关键词的链接
                        links = d('article a')

                        for link in links:
                            link_elem = pq(link)
                            text = link_elem.text().lower()
                            href = link_elem.attr('href')

                            if any(kw in text for kw in ['free', 'api', 'token', 'credit', 'trial', '免费']):
                                all_items.append({
                                    'source': f'GitHub/{repo.split("/")[1]}',
                                    'title': link_elem.text(),
                                    'url': href if href.startswith('http') else f'https://github.com{href}',
                                    'score': 0,
                                })

                print(f"GitHub {repo}: 完成")
                time.sleep(2)
            except Exception as e:
                print(f'Error scraping {repo}: {e}')
                continue

        print(f"GitHub Awesome: 找到 {len(all_items[:10])} 条相关信息")
        return all_items[:10]

    except Exception as e:
        print(f'Error in scrape_github_awesome: {e}')
        return []


def scrape_v2ex():
    """
    爬取V2EX的AI相关节点
    """
    print("\n=== 开始爬取 V2EX ===")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # V2EX的AI相关节点
        nodes = ['ai', 'chatgpt', 'programmer', 'create']
        all_posts = []

        for node in nodes:
            try:
                url = f'https://www.v2ex.com/api/topics/hot.json'
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    topics = response.json()

                    for topic in topics:
                        title = topic.get('title', '').lower()
                        content = topic.get('content', '').lower()

                        # 检查是否包含AI和优惠关键词
                        ai_keywords = ['ai', 'gpt', 'chatgpt', 'claude', 'openai', 'llm', '大模型', 'api']
                        deal_keywords = ['free', 'deal', 'discount', 'promo', 'credit', 'trial', '免费', '优惠', '折扣', '送']

                        has_ai = any(kw in title or kw in content for kw in ai_keywords)
                        has_deal = any(kw in title or kw in content for kw in deal_keywords)

                        if has_ai and has_deal:
                            all_posts.append({
                                'source': 'V2EX',
                                'title': topic.get('title', ''),
                                'url': f"https://www.v2ex.com/t/{topic.get('id', '')}",
                                'score': topic.get('replies', 0),
                            })

                time.sleep(2)
            except Exception as e:
                print(f'Error scraping V2EX node {node}: {e}')
                continue

        all_posts.sort(key=lambda x: x['score'], reverse=True)
        print(f"V2EX: 找到 {len(all_posts[:10])} 条相关信息")
        return all_posts[:10]

    except Exception as e:
        print(f'Error in scrape_v2ex: {e}')
        return []


def scrape_all_sources(filename):
    """
    整合所有信息源
    """
    try:
        all_deals = []

        # 1. Hacker News
        hn_deals = scrape_hackernews()
        all_deals.extend(hn_deals)

        # 2. GitHub Awesome
        github_deals = scrape_github_awesome()
        all_deals.extend(github_deals)

        # 3. V2EX
        v2ex_deals = scrape_v2ex()
        all_deals.extend(v2ex_deals)

        # 写入文件
        with codecs.open(filename, "w", "utf-8") as f:
            f.write(f"=== AI优惠信息全网汇总 ({datetime.datetime.now().strftime('%Y-%m-%d')}) ===\n\n")

            # 按来源分组
            sources = {}
            for deal in all_deals:
                source = deal['source']
                if source not in sources:
                    sources[source] = []
                sources[source].append(deal)

            # 输出每个来源的信息
            for source, deals in sources.items():
                f.write(f"\n## {source} ({len(deals)}条)\n\n")
                for index, deal in enumerate(deals, start=1):
                    f.write(f"{index}. {deal['title']}\n")
                    f.write(f"   链接: {deal['url']}\n")
                    if deal['score'] > 0:
                        f.write(f"   热度: {deal['score']}\n")
                    f.write("\n")

        print(f'\n总计找到 {len(all_deals)} 条AI优惠信息')
        return len(all_deals) > 0

    except Exception as e:
        print(f'Error in scrape_all_sources: {e}')
        return False


def job():
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    os.makedirs('logs', exist_ok=True)
    filename = f'logs/ai_deals_all_{strdate}.txt'
    print(f'{strdate} 开始AI优惠全网爬取任务...')
    createtext(filename)

    attempts = 0

    while attempts < 3:  # 减少重试次数，因为有多个源
        try:
            print(f'第 {attempts + 1} 次尝试爬取...')
            success = scrape_all_sources(filename)

            if not success:
                raise Exception("No deals found")

            print('\n爬取完成，开始AI分析...\n')

            ans = get_ai_analysis(filename)
            if ans:
                print(f'AI分析结果:\n{ans}\n')

                # 保存AI分析结果
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(ans)
                return filename
            else:
                raise Exception("AI analysis failed")

        except Exception as e:
            attempts += 1
            print(f"第 {attempts} 次尝试失败: {e}")
            if attempts < 3:
                time.sleep(180)  # 等待3分钟后重试

    raise Exception("所有尝试均失败")


def send_email(src, dst, subject, contents, attachments=None):
    pwd = os.environ.get('wangyi_emai_auth')
    yag = yagmail.SMTP(user=src, password=pwd, host='smtp.163.com', port='465')
    yag.send(to=dst, subject=subject, contents=contents, attachments=attachments)
    yag.close()

def send_emails(src, tos, subject, contents, attachments=None):
    for to in tos:
        send_email(src, to, subject, contents, attachments)

def daily_task():
    try:
        path = job()
        src = '19121220286@163.com'
        tos = get_emails('emails_deals.txt')
        subject = '🎉 今日AI薅羊毛全网汇总'

        # 读取AI分析结果并转换为HTML
        content = get_contents(path)
        html_content = convert_to_html_email(content)

        # yagmail会自动识别HTML内容
        send_emails(src, tos, subject, html_content, None)  # 不需要附件
        print("邮件发送完成！")
    except Exception as e:
        print(f"daily_task出错: {e}")

if __name__ == '__main__':
    try:
        schedule.every().day.at('12:10').do(daily_task)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        print(f"程序出错: {e}")

