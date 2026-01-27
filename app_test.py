
import os
import schedule
import time
from datetime import datetime
from config.settings import config
from config.prompts import PYTHON_ANALYSIS_PROMPT
from core.scraper import GitHubTrendingScraper
from core.ai_analyzer import AIAnalyzer
from core.email_sender import EmailSender


def get_emails(path):
    """读取邮箱列表"""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def job():
    """执行每日任务"""
    strdate = datetime.now().strftime('%Y-%m-%d')
    os.makedirs('logs', exist_ok=True)
    filename = f'logs/{strdate}.json'
    raw_file = f'logs/{strdate}_raw.txt'

    print(f'{strdate} start Python trending job...')

    # 1. 爬取数据
    scraper = GitHubTrendingScraper()
    attempts = 0
    while attempts < config.ai.max_retries:
        try:
            print(f'Attempt {attempts + 1} to scrape Python trends...')
            if scraper.scrape('python', raw_file):
                break
            attempts += 1
            time.sleep(config.ai.retry_delay)
    else:
        raise Exception("All attempts to scrape data have failed.")

    # 2. AI分析
    analyzer = AIAnalyzer(model=config.ai.model)
    result = analyzer.analyze_trends(raw_file, PYTHON_ANALYSIS_PROMPT)
    analyzer.save_analysis(result, filename)

    # 3. 发送邮件
    sender = EmailSender(
        smtp_host=config.email.smtp_host,
        smtp_port=config.email.smtp_port,
        sender_email=config.email.sender_email,
        sender_password=config.email.sender_password
    )

    tos = get_emails('emails.txt')
    sender.send_trending_email(
        to_emails=tos,
        language='python',
        date=strdate,
        analysis_result=result,
        template_path='templates/email_python.html',
        tracking_url=config.tracking.base_url
    )

    print(f'Python trending job completed for {strdate}')


def daily_task():
    """每日任务包装器"""
    try:
        job()
    except Exception as e:
        print(f"Error in daily_task: {e}")


if __name__ == '__main__':
    try:
        # Run immediately for testing
        daily_task()
        # schedule.every().day.at('21:00').do(daily_task)
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
