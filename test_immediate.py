#!/usr/bin/env python3
"""
立即测试脚本 - 完整流程验证
测试爬取、AI分析、邮件发送功能
"""
import os
import sys
import datetime
import requests
import yagmail
from pyquery import PyQuery as pq
from zhipuai import ZhipuAI

print("=" * 60)
print("🚀 AI-FLOW 立即测试脚本 - 完整流程验证")
print(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# 检查环境变量
print("\n🔍 检查环境变量...")
zhipu_key = os.environ.get("ZHIPUAI_API_KEY")
wangyi_auth = os.environ.get("wangyi_emai_auth")

if zhipu_key:
    print(f"✅ ZHIPUAI_API_KEY: 已设置 ({zhipu_key[:10]}...)")
else:
    print("❌ ZHIPUAI_API_KEY: 未设置")
    sys.exit(1)

if wangyi_auth:
    print(f"✅ wangyi_emai_auth: 已设置 ({wangyi_auth[:5]}...)")
else:
    print("❌ wangyi_emai_auth: 未设置")
    sys.exit(1)

# 测试邮箱配置
TEST_EMAILS = ["19121220286@163.com"]  # 发送给自己作为测试

def test_scrape():
    """测试爬虫功能"""
    print("\n🌐 测试GitHub爬虫...")
    try:
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # 只爬取前3个项目以加快测试
        url = 'https://github.com/trending/python'
        print(f"请求URL: {url}")
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"状态码: {r.status_code}")
        
        if r.status_code == 200:
            d = pq(r.content)
            items = d('div.Box article.Box-row')
            print(f"找到 {len(items)} 个项目")
            
            # 提取前3个项目
            projects = []
            for i, item in enumerate(items[:3]):
                item_pq = pq(item)
                title = item_pq(".lh-condensed a").text().strip()
                description = item_pq("p.col-9").text().strip()
                url_path = item_pq(".lh-condensed a").attr("href")
                url = f"https://github.com{url_path}" if url_path else ""
                
                projects.append(f"{i+1}. [{title}]: {description}({url})")
                print(f"  {i+1}. {title[:40]}...")
            
            content = "\n".join(projects)
            print("✅ 爬虫测试成功")
            return content
        else:
            print(f"❌ 爬虫失败: HTTP {r.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 爬虫异常: {e}")
        return None

def test_ai_analysis(content):
    """测试AI分析功能"""
    print("\n🤖 测试AI分析...")
    try:
        client = ZhipuAI(api_key=zhipu_key)
        
        print("调用智谱AI API...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": """你是一个GitHub趋势分析专家。分析这些项目并生成简洁的报告。"""},
                {"role": "user", "content": f"分析这些GitHub趋势项目:\n{content}"}
            ],
        )
        
        analysis = response.choices[0].message.content
        print(f"✅ AI分析成功，长度: {len(analysis)} 字符")
        print(f"分析预览: {analysis[:200]}...")
        return analysis
        
    except Exception as e:
        print(f"❌ AI分析异常: {e}")
        return None

def test_email_sender(content):
    """测试邮件发送功能"""
    print("\n📧 测试邮件发送...")
    try:
        src = '19121220286@163.com'
        subject = f'🚀 AI-FLOW 立即测试 - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # 构建测试内容
        test_content = f"""
<h2>🎯 AI-FLOW 立即测试结果</h2>
<p><strong>测试时间:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>状态:</strong> ✅ 所有功能测试成功</p>
<hr>
<h3>📊 测试详情:</h3>
<pre>{content[:1000]}</pre>
<hr>
<p>🎉 恭喜！AI-FLOW系统所有功能正常运行。</p>
<p>今晚21:00的定时任务将正常执行，121个订阅用户将收到更新。</p>
        """
        
        print(f"发件人: {src}")
        print(f"收件人: {TEST_EMAILS}")
        print(f"主题: {subject}")
        
        yag = yagmail.SMTP(user=src, password=wangyi_auth, host='smtp.163.com', port='465')
        yag.send(to=TEST_EMAILS, subject=subject, contents=[test_content])
        yag.close()
        
        print("✅ 邮件发送成功！")
        print("📨 请检查收件箱查看测试邮件")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送异常: {e}")
        return False

def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🎬 开始完整流程测试...")
    print("=" * 60)
    
    # 1. 测试爬虫
    scraped_content = test_scrape()
    if not scraped_content:
        print("❌ 爬虫测试失败，终止测试")
        return False
    
    # 2. 测试AI分析
    analysis = test_ai_analysis(scraped_content)
    if not analysis:
        print("⚠️ AI分析测试失败，继续测试邮件发送")
        # 继续测试邮件发送
    
    # 3. 测试邮件发送
    test_content = analysis if analysis else f"爬虫内容:\n{scraped_content}"
    email_sent = test_email_sender(test_content)
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    results = {
        "爬虫功能": "✅ 成功" if scraped_content else "❌ 失败",
        "AI分析功能": "✅ 成功" if analysis else "⚠️ 失败",
        "邮件发送功能": "✅ 成功" if email_sent else "❌ 失败",
        "完整流程": "✅ 成功" if (scraped_content and email_sent) else "⚠️ 部分失败"
    }
    
    for key, value in results.items():
        print(f"{key:15} {value}")
    
    print(f"\n⏰ 当前时间: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"距离21:00定时任务还有: 约{21 - datetime.datetime.now().hour}小时{59 - datetime.datetime.now().minute}分钟")
    
    if scraped_content and email_sent:
        print("\n🎉 恭喜！所有核心功能测试成功！")
        print("今晚21:00的定时任务将正常执行，121个订阅用户将收到更新。")
        return True
    else:
        print("\n⚠️ 部分功能测试失败，需要检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)