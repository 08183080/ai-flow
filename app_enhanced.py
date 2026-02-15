"""
增强版AI信息流主程序
基于模块化架构，提供更好的可维护性和美观的邮件界面
"""
import os
import schedule
import time
import sys
from datetime import datetime
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import config
from config.prompts import PYTHON_ANALYSIS_PROMPT
from core.scraper import GitHubTrendingScraper
from core.ai_analyzer import AIAnalyzer
from core.email_sender import EmailSender


def get_emails(path: str) -> list:
    """读取邮箱列表"""
    if not os.path.exists(path):
        print(f"⚠️  邮箱文件不存在: {path}")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        emails = [line.strip() for line in f if line.strip()]
    
    print(f"📧 读取到 {len(emails)} 个订阅邮箱")
    return emails


def create_log_dir():
    """创建日志目录"""
    log_dir = config.app.log_dir
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def run_python_trending_job():
    """执行Python趋势分析任务"""
    try:
        current_time = datetime.now()
        strdate = current_time.strftime('%Y-%m-%d')
        log_dir = create_log_dir()
        
        # 文件路径
        raw_file = f"{log_dir}/{strdate}_raw.txt"
        json_file = f"{log_dir}/{strdate}.json"
        txt_file = f"{log_dir}/{strdate}.txt"
        
        print(f"🚀 {strdate} 开始Python趋势分析任务...")
        print(f"⏰ 当前时间: {current_time.strftime('%H:%M:%S')}")
        
        # 1. 验证配置
        if not config.validate():
            print("❌ 配置验证失败，请检查环境变量")
            return False
        
        # 2. 爬取数据
        print("🔍 开始爬取GitHub Python趋势...")
        scraper = GitHubTrendingScraper(
            timeout=config.scraper.timeout,
            max_retries=config.scraper.max_retries
        )
        
        success, projects = scraper.scrape('python', raw_file)
        if not success or not projects:
            print("❌ 爬取数据失败")
            return False
        
        print(f"✅ 成功爬取 {len(projects)} 个Python项目")
        
        # 3. AI分析
        print("🧠 开始AI分析...")
        analyzer = AIAnalyzer(
            api_key=config.ai.api_key,
            model=config.ai.model
        )
        
        analysis_result = analyzer.analyze_trends(raw_file, PYTHON_ANALYSIS_PROMPT)
        
        # 解析结构化数据
        structured_analysis = analyzer.parse_structured_analysis(analysis_result)
        
        # 保存分析结果
        analyzer.save_analysis(structured_analysis, json_file)
        
        # 4. 发送邮件
        print("📧 开始发送邮件...")
        sender = EmailSender(
            smtp_host=config.email.smtp_host,
            smtp_port=config.email.smtp_port,
            sender_email=config.email.sender_email,
            sender_password=config.email.sender_password
        )
        
        # 读取订阅邮箱
        emails = get_emails(config.app.emails_file)
        if not emails:
            print("⚠️  没有订阅邮箱，跳过邮件发送")
            return True
        
        # 加载HTML模板
        html_content = None
        template_path = "templates/email_python.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            # 构建模板上下文
            from jinja2 import Template
            template = Template(html_template)
            
            # 准备模板数据
            template_data = {
                "date": strdate,
                "highlight_project": {
                    "title": structured_analysis.highlight_project.title,
                    "description": structured_analysis.highlight_project.description,
                    "tag_class": "ai",
                    "tag": structured_analysis.highlight_project.category
                },
                "categories": [
                    {"name": "视觉AI", "count": 3, "examples": "项目A、项目B、项目C"},
                    {"name": "开发者工具", "count": 5, "examples": "项目D、项目E"}
                ],
                "trends": structured_analysis.trends,
                "insights": structured_analysis.insights,
                "prediction": structured_analysis.prediction,
                "project_count": structured_analysis.total_projects,
                "category_count": len(structured_analysis.trends),
                "subscriber_count": len(emails)
            }
            
            html_content = template.render(**template_data)
        
        # 发送邮件
        results = sender.send_batch_emails(
            to_emails=emails,
            subject=f"🚀 {strdate} AI趋势分析报告",
            content=analysis_result,
            html_content=html_content,
            attachments=[txt_file]
        )
        
        # 统计结果
        success_count = sum(1 for success in results.values() if success)
        print(f"📊 邮件发送完成: {success_count}/{len(emails)} 成功")
        
        # 5. 记录任务完成
        completion_log = f"{log_dir}/completion.log"
        with open(completion_log, 'a', encoding='utf-8') as f:
            f.write(f"{current_time.isoformat()}: Python趋势任务完成，发送 {success_count}/{len(emails)} 封邮件\n")
        
        print(f"✅ Python趋势分析任务完成!")
        return True
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def daily_task():
    """每日任务包装器"""
    try:
        print(f"📅 执行每日定时任务...")
        return run_python_trending_job()
    except Exception as e:
        print(f"❌ 每日任务执行失败: {e}")
        return False


def test_run():
    """测试运行"""
    print("🧪 开始测试运行...")
    success = run_python_trending_job()
    
    if success:
        print("✅ 测试运行成功!")
    else:
        print("❌ 测试运行失败")
    
    return success


def main():
    """主函数"""
    print("""
    ╔══════════════════════════════════════════╗
    ║         AI信息流2.0 - 增强版             ║
    ║         由 nanobot 智能优化              ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 检查配置
    print("🔧 检查配置...")
    if not config.validate():
        print("❌ 配置验证失败:")
        print("   请设置以下环境变量:")
        print("   - ZHIPUAI_API_KEY: 智谱AI API密钥")
        print("   - WANGYI_EMAIL_AUTH: 网易邮箱授权码")
        return
    
    print("✅ 配置验证通过")
    
    # 检查邮箱文件
    emails_file = config.app.emails_file
    if os.path.exists(emails_file):
        emails = get_emails(emails_file)
        print(f"📊 当前订阅用户: {len(emails)} 人")
    else:
        print(f"⚠️  邮箱文件不存在: {emails_file}")
        print("   请创建 emails.txt 文件并添加订阅邮箱")
    
    # 检查模板文件
    template_path = "templates/email_python.html"
    if os.path.exists(template_path):
        print(f"🎨 HTML模板: 已加载")
    else:
        print(f"⚠️  HTML模板文件不存在: {template_path}")
        print("   将使用纯文本邮件格式")
    
    # 用户选择模式
    print("\n📋 请选择运行模式:")
    print("   1. 立即运行一次测试")
    print("   2. 启动定时任务 (每日21:00)")
    print("   3. 手动运行一次任务")
    
    try:
        choice = input("请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            print("\n🧪 运行测试模式...")
            test_run()
            
        elif choice == "2":
            print(f"\n⏰ 启动定时任务，每日 {config.app.schedule_time} 执行...")
            schedule.every().day.at(config.app.schedule_time).do(daily_task)
            
            # 立即运行一次
            print("立即运行一次初始任务...")
            daily_task()
            
            print(f"\n⏳ 定时任务已启动，等待每日 {config.app.schedule_time}...")
            print("按 Ctrl+C 退出")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        elif choice == "3":
            print("\n🚀 手动运行任务...")
            daily_task()
            
        else:
            print("❌ 无效选择，程序退出")
            
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == '__main__':
    main()