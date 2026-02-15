#!/usr/bin/env python3
"""
即时测试脚本 - 立即测试ai-flow完整流程
创建：2026-02-15 20:40
"""
import os
import sys
import time
import requests
import codecs
from datetime import datetime
from pyquery import PyQuery as pq
from zhipuai import ZhipuAI
import yagmail

# 配置
TEST_EMAILS = [
    "houlongapple@icloud.com",  # 第一个邮箱用于测试
    # "pxxhl@qq.com"  # 可选：第二个测试邮箱
]

def get_emails(path):
    """读取邮箱列表"""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def scrape_now():
    """立即爬取当前GitHub趋势"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    
    print("🌐 开始爬取GitHub Python趋势...")
    url = 'https://github.com/trending/python'
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(f"✅ 爬取成功，状态码: {r.status_code}")
        
        if r.status_code != 200:
            print(f"⚠️ 状态码异常: {r.status_code}")
            return None
            
        d = pq(r.content)
        items = d('div.Box article.Box-row')
        projects = []
        
        print(f"📊 发现 {len(items)} 个项目")
        for index, item in enumerate(items[:10], start=1):  # 只取前10个
            i = pq(item)
            title = i(".lh-condensed a").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            full_url = "https://github.com" + url if url else ""
            
            project_info = f"{index}. [{title}]: {description} ({full_url})"
            projects.append(project_info)
            
            if index <= 3:  # 打印前3个项目
                print(f"   {project_info}")
                
        return "\n".join(projects)
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        return None

def ai_analyze_now(trends_text):
    """使用智谱AI分析趋势"""
    print("\n🤖 AI分析中...")
    try:
        api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not api_key:
            print("❌ ZHIPUAI_API_KEY 未设置")
            return None
            
        client = ZhipuAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": """你是GitHub趋势分析专家。请将英文项目信息翻译为中文，并选出1个最惊艳的项目详细说明。
同时分析今日技术趋势，提供3个关键洞察。
输出格式：
## 今日GitHub趋势即时测试

### 最惊艳项目
[项目名称] - [中文描述]
惊艳原因：[详细解释]

### 今日趋势洞察
1. [洞察1]
2. [洞察2]
3. [洞察3]

### 测试时间
[当前时间]

我是谢苹果，AI信息流2.0测试版，由nanobot优化。"""},
                {"role": "user", "content": trends_text}
            ],
        )
        
        analysis = response.choices[0].message.content
        print("✅ AI分析完成")
        return analysis
    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        return None

def send_test_email(analysis_text):
    """发送测试邮件"""
    print("\n📧 准备发送测试邮件...")
    
    # 获取邮件配置
    sender_email = "19121220286@163.com"
    sender_password = os.environ.get("wangyi_emai_auth")  # 注意：小写
    
    if not sender_password:
        print("❌ wangyi_emai_auth 环境变量未设置")
        return False
        
    try:
        # 创建美观的HTML邮件内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header .subtitle {{ opacity: 0.9; margin-top: 10px; }}
        .content {{ background: white; padding: 30px; margin-top: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .highlight {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; }}
        .badge {{ background: #667eea; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin-right: 8px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
        .test-info {{ background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 AI信息流2.0 - 即时测试</h1>
        <div class="subtitle">GitHub Python趋势分析 • 即时测试版本</div>
    </div>
    
    <div class="content">
        <div class="test-info">
            <p><strong>测试说明：</strong>这是ai-flow项目的即时功能测试邮件，测试新界面效果和邮件发送功能。</p>
            <p><strong>测试时间：</strong>{timestamp}</p>
            <p><strong>测试类型：</strong>完整流程测试（爬虫 → AI分析 → 邮件发送）</p>
        </div>
        
        <div class="highlight">
            <h3>📈 AI分析结果</h3>
            {analysis_text.replace('\n', '<br>')}
        </div>
        
        <div style="margin-top: 30px;">
            <span class="badge">新界面</span>
            <span class="badge">即时测试</span>
            <span class="badge">AI分析</span>
            <span class="badge">邮件系统</span>
        </div>
    </div>
    
    <div class="footer">
        <p>🔧 技术支持：nanobot智能优化 • AI信息流2.0测试版</p>
        <p>📅 生成时间：{timestamp}</p>
        <p><small>此邮件为测试邮件，请勿回复</small></p>
    </div>
</body>
</html>
        """
        
        # 发送邮件
        print(f"📤 发送到 {len(TEST_EMAILS)} 个测试邮箱: {', '.join(TEST_EMAILS)}")
        
        yag = yagmail.SMTP(user=sender_email, password=sender_password, 
                          host='smtp.163.com', port='465')
        
        subject = f"🎯 AI信息流2.0测试 - {timestamp}"
        
        for to_email in TEST_EMAILS:
            print(f"  正在发送到: {to_email}")
            yag.send(
                to=to_email,
                subject=subject,
                contents=[html_content],
                attachments=[]
            )
            print(f"  ✅ {to_email} 发送成功")
            time.sleep(1)  # 避免发送过快
        
        yag.close()
        print("\n🎉 所有测试邮件发送完成！")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI信息流2.0 - 即时测试脚本")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"距离21:00还有: {60 - datetime.now().minute}分钟")
    print()
    
    # 1. 爬取趋势
    trends = scrape_now()
    if not trends:
        print("❌ 爬取失败，测试终止")
        return
    
    # 2. AI分析
    analysis = ai_analyze_now(trends)
    if not analysis:
        print("❌ AI分析失败，测试终止")
        return
    
    # 3. 发送测试邮件
    print("\n" + "=" * 60)
    print("📋 测试摘要:")
    print(f"   爬取项目: {trends.count('http')} 个")
    print(f"   AI分析长度: {len(analysis)} 字符")
    print(f"   测试邮箱: {len(TEST_EMAILS)} 个")
    print("=" * 60)
    
    confirm = input("\n⚠️  是否发送测试邮件？(y/n): ").strip().lower()
    if confirm != 'y':
        print("测试取消")
        return
    
    success = send_test_email(analysis)
    
    # 4. 结果报告
    print("\n" + "=" * 60)
    print("📊 测试结果报告")
    print("=" * 60)
    print(f"✅ 爬取: {'成功' if trends else '失败'}")
    print(f"✅ AI分析: {'成功' if analysis else '失败'}")
    print(f"✅ 邮件发送: {'成功' if success else '失败'}")
    print(f"🕐 总耗时: {time.time() - start_time:.1f}秒")
    print(f"📅 测试完成时间: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 测试成功！请检查测试邮箱是否收到邮件。")
        print("   邮件应为美观的HTML格式，包含AI分析结果。")
    else:
        print("\n❌ 测试失败，请检查日志。")
    
    print("\n🔧 注意事项:")
    print("   1. 当前生产app.py仍在运行，不影响21:00的正常发送")
    print("   2. 测试邮件仅发送到指定测试邮箱")
    print("   3. 如需调整测试邮箱，请修改TEST_EMAILS列表")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()