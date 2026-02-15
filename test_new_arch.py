#!/usr/bin/env python3
"""
新架构测试脚本
快速展示新架构效果，不影响当前运行的app.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import config
from config.prompts import PYTHON_ANALYSIS_PROMPT
from core.scraper import GitHubTrendingScraper
from core.ai_analyzer import AIAnalyzer
from core.email_sender import EmailSender


def test_scraper():
    """测试爬虫功能"""
    print("🚀 开始测试爬虫功能...")
    scraper = GitHubTrendingScraper()
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # 测试文件路径
    raw_file = os.path.join(test_dir, "test_raw.txt")
    
    # 尝试爬取数据
    attempts = 0
    while attempts < 3:
        try:
            print(f"📡 爬取Python趋势 (尝试 {attempts + 1}/3)...")
            if scraper.scrape('python', raw_file):
                print(f"✅ 爬虫成功! 数据保存在: {raw_file}")
                
                # 显示爬取的项目数量
                with open(raw_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    projects = [line for line in lines if line.strip() and not line.startswith('#')]
                    print(f"📊 共爬取到 {len(projects)} 个项目")
                    if projects:
                        print("📋 前5个项目:")
                        for i, proj in enumerate(projects[:5]):
                            print(f"  {i+1}. {proj.strip()}")
                return raw_file
            attempts += 1
        except Exception as e:
            print(f"❌ 爬虫出错: {e}")
            attempts += 1
    
    print("⚠️  爬虫测试失败，使用模拟数据进行后续测试")
    # 创建模拟数据
    with open(raw_file, 'w', encoding='utf-8') as f:
        f.write("# Python Trending Projects - Test Data\n")
        f.write("test-owner/awesome-ai - 用于AI研究的精选资源列表\n")
        f.write("ml-research/llm-benchmarks - 开源LLM基准测试框架\n")
        f.write("vision-ai/real-time-detection - 实时目标检测系统\n")
    return raw_file


def test_ai_analysis(raw_file):
    """测试AI分析功能"""
    print("\n🧠 开始测试AI分析功能...")
    
    # 检查API密钥
    if not config.ai.api_key:
        print("⚠️  ZHIPUAI_API_KEY未设置，AI分析将使用模拟数据")
        # 创建模拟分析结果
        test_result = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "summary": "测试AI分析 - 由于缺少API密钥，使用模拟数据",
            "most_impressive": {
                "name": "test-owner/awesome-ai",
                "description": "用于AI研究的精选资源列表",
                "stars": 1500,
                "reason": "项目组织良好，资源丰富"
            },
            "categories": [
                {"name": "AI工具", "count": 3, "projects": ["test-owner/awesome-ai", "ml-research/llm-benchmarks"]},
                {"name": "计算机视觉", "count": 1, "projects": ["vision-ai/real-time-detection"]}
            ],
            "trend_insights": [
                "AI工具类项目持续增多",
                "开源LLM基准测试成为热点"
            ],
            "predictions": ["未来更多AI与行业结合的项目"]
        }
    else:
        try:
            print("🤖 使用智谱AI进行分析...")
            analyzer = AIAnalyzer(model=config.ai.model)
            result = analyzer.analyze_trends(raw_file, PYTHON_ANALYSIS_PROMPT)
            
            # 保存分析结果
            test_dir = "test_output"
            result_file = os.path.join(test_dir, "test_analysis.json")
            analyzer.save_analysis(result, result_file)
            
            print(f"✅ AI分析成功! 结果保存在: {result_file}")
            
            # 显示分析摘要
            print(f"📝 分析摘要: {result.get('summary', '无摘要')}")
            print(f"🏆 最惊艳项目: {result.get('most_impressive', {}).get('name', '无数据')}")
            
            return result
            
        except Exception as e:
            print(f"❌ AI分析出错: {e}")
            return None
    
    # 保存模拟结果
    test_dir = "test_output"
    result_file = os.path.join(test_dir, "test_analysis.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(test_result, f, ensure_ascii=False, indent=2)
    
    print(f"📄 模拟分析结果保存在: {result_file}")
    return test_result


def test_email_template(analysis_result):
    """测试邮件模板生成"""
    print("\n🎨 开始测试邮件模板...")
    
    try:
        from core.email_sender import EmailSender
        
        # 初始化邮件发送器（不实际发送）
        sender = EmailSender(
            smtp_host="smtp.163.com",
            smtp_port=465,
            sender_email="test@example.com",
            sender_password="dummy"
        )
        
        # 生成HTML内容
        strdate = datetime.now().strftime('%Y-%m-%d')
        html_content = sender._render_template(
            template_path='templates/email_python.html',
            language='python',
            date=strdate,
            analysis_result=analysis_result,
            tracking_url=None
        )
        
        # 保存HTML文件
        test_dir = "test_output"
        html_file = os.path.join(test_dir, "email_preview.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML邮件模板生成成功!")
        print(f"📧 邮件预览保存为: {html_file}")
        print(f"📂 文件大小: {len(html_content)} 字符")
        
        # 提取预览信息
        lines = html_content.split('\n')
        title_line = next((line for line in lines if '<title>' in line), '')
        h1_line = next((line for line in lines if '<h1' in line), '')
        
        if title_line:
            print(f"🏷️  邮件标题: {title_line.replace('<title>', '').replace('</title>', '').strip()}")
        if h1_line:
            print(f"📰 邮件主标题: {h1_line.replace('<h1', '').replace('</h1>', '').replace('>', ' ').strip()}")
        
        return html_file
        
    except Exception as e:
        print(f"❌ 邮件模板测试出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_pipeline(with_email_send=False):
    """测试完整流程"""
    print("=" * 60)
    print("🧪 AI信息流新架构测试")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 测试爬虫
    raw_file = test_scraper()
    
    # 2. 测试AI分析
    analysis_result = test_ai_analysis(raw_file)
    
    if analysis_result:
        # 3. 测试邮件模板
        html_file = test_email_template(analysis_result)
        
        # 4. 可选的邮件发送测试
        if with_email_send and config.email.sender_password:
            print("\n📤 开始测试邮件发送...")
            try:
                # 读取测试邮箱（使用前2个邮箱）
                test_emails = []
                if os.path.exists('emails.txt'):
                    with open('emails.txt', 'r', encoding='utf-8') as f:
                        all_emails = [line.strip() for line in f if line.strip()]
                        test_emails = all_emails[:2] if len(all_emails) >= 2 else all_emails[:1]
                
                if test_emails:
                    sender = EmailSender(
                        smtp_host=config.email.smtp_host,
                        smtp_port=config.email.smtp_port,
                        sender_email=config.email.sender_email,
                        sender_password=config.email.sender_password
                    )
                    
                    sender.send_trending_email(
                        to_emails=test_emails,
                        language='python',
                        date=datetime.now().strftime('%Y-%m-%d'),
                        analysis_result=analysis_result,
                        template_path='templates/email_python.html',
                        tracking_url=config.tracking.base_url
                    )
                    print(f"✅ 测试邮件已发送到: {', '.join(test_emails)}")
                else:
                    print("⚠️  未找到测试邮箱，跳过邮件发送测试")
            except Exception as e:
                print(f"❌ 邮件发送测试出错: {e}")
        elif with_email_send:
            print("⚠️  WANGYI_EMAIL_AUTH未设置，跳过邮件发送测试")
    
    print("\n" + "=" * 60)
    print("🧪 测试完成!")
    print("📁 所有测试文件保存在: test_output/")
    print("🔍 要查看HTML邮件预览，请打开:")
    print("   file:///root/ai-flow/test_output/email_preview.html")
    print("=" * 60)


def quick_preview():
    """快速预览模式 - 只生成HTML邮件预览"""
    print("🎨 快速预览邮件模板...")
    
    # 创建模拟分析结果用于预览
    preview_result = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "summary": "今日GitHub Python趋势分析：AI工具类项目增多，开源LLM基准测试成为新热点",
        "most_impressive": {
            "name": "vision-ai/real-time-detection",
            "description": "基于YOLOv8的实时目标检测系统，支持多种硬件加速",
            "stars": 850,
            "reason": "项目实用性强，文档完善，社区活跃"
        },
        "categories": [
            {"name": "AI工具", "count": 5, "projects": ["ai-org/llm-tools", "ml-dev/model-zoo"]},
            {"name": "计算机视觉", "count": 3, "projects": ["vision-ai/detection", "cv-lib/segmentation"]},
            {"name": "开发者工具", "count": 4, "projects": ["dev-tools/debugger", "tool-org/cli-helper"]}
        ],
        "trend_insights": [
            "AI工具类项目持续增多，反映AI技术普及化趋势",
            "开源LLM基准测试工具成为新热点",
            "跨平台AI部署方案受到关注"
        ],
        "predictions": [
            "更多AI与传统行业结合的项目",
            "边缘AI计算框架将增多",
            "AI开发工具链进一步完善"
        ]
    }
    
    html_file = test_email_template(preview_result)
    
    if html_file:
        print("\n✨ 快速预览完成!")
        print("📧 邮件预览文件: test_output/email_preview.html")
        print("💡 提示: 可以在浏览器中打开该文件查看效果")
        
        # 显示文件路径
        abs_path = os.path.abspath(html_file)
        print(f"📂 绝对路径: {abs_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AI信息流新架构测试工具')
    parser.add_argument('--mode', choices=['full', 'quick', 'scraper', 'analysis'], 
                       default='quick', help='测试模式 (default: quick)')
    parser.add_argument('--send-email', action='store_true', 
                       help='是否测试邮件发送 (需要WANGYI_EMAIL_AUTH)')
    
    args = parser.parse_args()
    
    # 创建测试输出目录
    os.makedirs("test_output", exist_ok=True)
    
    if args.mode == 'full':
        test_full_pipeline(with_email_send=args.send_email)
    elif args.mode == 'quick':
        quick_preview()
    elif args.mode == 'scraper':
        test_scraper()
    elif args.mode == 'analysis':
        raw_file = test_scraper()
        test_ai_analysis(raw_file)
    
    print("\n✅ 测试脚本执行完成!")
    print("⏰ 当前时间:", datetime.now().strftime('%H:%M:%S'))
    print("📝 注意: 现有app.py进程仍在运行，未受影响")