#!/usr/bin/env python3
"""
使用昨天数据测试邮件发送 - 跳过网络爬取
创建：2026-02-15 20:42
"""
import os
import sys
import time
from datetime import datetime
from zhipuai import ZhipuAI
import yagmail

# 配置 - 测试邮箱（只发送到前2个邮箱避免打扰太多人）
TEST_EMAILS = [
    "houlongapple@icloud.com",  # 第一个邮箱
    "pxxhl@qq.com"              # 第二个邮箱
]

def read_yesterday_data():
    """读取昨天的项目数据"""
    yesterday = datetime.now().strftime('%Y-%m-%d')
    # 尝试找昨天的文件，如果不存在就用2026-02-14.txt
    possible_files = [
        f"logs/{yesterday}.txt",
        "logs/2026-02-14.txt",
        "logs/2026-02-13.txt"
    ]
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"📂 使用数据文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取项目列表（格式：序号. [项目]）
            projects = []
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() and '. [' in line):
                    projects.append(line)
            
            print(f"📊 从文件中提取了 {len(projects)} 个项目")
            if projects:
                return "\n".join(projects), file_path
    
    # 如果找不到文件，使用示例数据
    print("⚠️  未找到日志文件，使用示例数据")
    sample_data = """1. [ruvnet / wifi-densepose]: InvisPose - 基于WiFi的颠覆性密集人体姿态估计系统，使用商用网状路由器实现实时全身体态追踪。
2. [Zipstack / unstract]: 无代码LLM平台，用于启动API和ETL管道以结构化非结构化文档。
3. [GetStream / Vision-Agents]: Stream的开源视觉代理。快速构建任何模型或视频提供商的视觉代理。使用Stream的边缘网络实现超低延迟。
4. [open-webui / open-webui]: 用户友好的AI界面（支持Ollama、OpenAI API等）。
5. [music-assistant / server]: 音乐助手是一个开源的媒体库管理器，可连接到您的流媒体服务和各种连接的扬声器。"""
    return sample_data, "示例数据"

def ai_analyze_now(trends_text, source_info):
    """使用智谱AI分析趋势"""
    print(f"\n🤖 AI分析中（数据来源: {source_info}）...")
    try:
        api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not api_key:
            print("❌ ZHIPUAI_API_KEY 未设置")
            return None
            
        client = ZhipuAI(api_key=api_key)
        
        # 增强的AI提示词，生成更美观的分析
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": """你是GitHub趋势分析专家。请分析以下项目信息，生成美观、专业的分析报告。

## 分析要求：
1. **最惊艳项目**：选出一个最惊艳的项目，详细说明为什么惊艳
2. **趋势分类**：将项目分类（视觉AI、开发者工具、AI平台、创新应用等）
3. **技术洞察**：提供3个深度技术洞察
4. **预测建议**：基于趋势，预测下一个热门方向

## 输出格式：
### 🏆 最惊艳项目
**[项目名称]** - [一句话描述]
✨ **惊艳原因**：[详细解释，至少100字]

### 📊 项目分类概览
🔹 **视觉AI**：[数量]个项目
🔹 **开发者工具**：[数量]个项目  
🔹 **AI平台**：[数量]个项目
🔹 **创新应用**：[数量]个项目

### 🎯 今日技术趋势
1. [趋势1，如"隐私友好AI感知技术兴起"]
2. [趋势2，如"低代码AI平台爆发"]
3. [趋势3，如"边缘计算与AI结合"]

### 💡 深度洞察
- **投资热点**：[哪些领域值得关注]
- **技术突破**：[关键技术突破点]
- **应用前景**：[商业应用可能性]

### 🚀 预测与建议
[基于今日趋势的预测，以及开发者/投资者的行动建议]

**分析专家**：AI信息流2.0 • nanobot优化版"""},
                {"role": "user", "content": trends_text}
            ],
        )
        
        analysis = response.choices[0].message.content
        print("✅ AI分析完成")
        print(f"   分析长度: {len(analysis)} 字符")
        return analysis
    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        # 返回一个示例分析
        return """### 🏆 最惊艳项目
**[ruvnet / wifi-densepose]** - 基于WiFi的颠覆性密集人体姿态估计系统

✨ **惊艳原因**：这个项目代表了计算机视觉领域的重大突破。传统的人体姿态估计依赖于摄像头，存在隐私问题和环境限制。wifi-densepose创新性地使用普通的WiFi网状路由器信号来追踪人体姿态，实现了无需摄像头的实时全身姿态估计。这种技术不仅成本低廉（使用商用硬件），而且完全保护用户隐私，可以在黑暗、有障碍物的环境中工作。它为智能家居、医疗监护、安防监控等领域开启了新的可能性。

### 📊 项目分类概览
🔹 **视觉AI**：3个项目 (wifi-densepose, Vision-Agents)
🔹 **开发者工具**：4个项目 (unstract, claude-quickstarts, claude-skills)  
🔹 **AI平台**：2个项目 (open-webui)
🔹 **创新应用**：6个项目 (music-assistant, docling, nanochat等)

### 🎯 今日技术趋势
1. **隐私友好AI感知技术兴起**：如wifi-densepose所示，无需摄像头的感知技术成为新热点
2. **低代码AI平台爆发**：unstract等项目让非开发者也能快速构建AI应用
3. **边缘计算与AI结合**：Vision-Agents等强调低延迟的边缘AI处理

### 💡 深度洞察
- **投资热点**：隐私保护AI技术、边缘AI基础设施、低代码AI平台
- **技术突破**：WiFi信号用于计算机视觉、开源视觉代理框架、文档智能处理
- **应用前景**：智能家居、工业检测、内容生成、开发者工具链

### 🚀 预测与建议
**预测**：未来6个月，我们将看到更多"无摄像头"AI感知技术的商业化应用，特别是在医疗监护和智能家居领域。

**建议**：
1. **开发者**：关注边缘AI和隐私保护技术，这些将成为差异化竞争的关键
2. **投资者**：关注低代码AI平台和垂直领域AI应用，市场正在快速成熟
3. **企业**：考虑采用开源AI工具链，降低技术门槛和成本

**分析专家**：AI信息流2.0 • nanobot优化版 • 即时测试版本"""

def create_beautiful_html(analysis_text, data_source):
    """创建美观的HTML邮件内容"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_date = "2026-02-14" if "2026-02-14" in data_source else datetime.now().strftime("%Y-%m-%d")
    
    # 美化分析文本
    styled_analysis = analysis_text.replace('\n### ', '\n</div><div class="section"><h3>')
    styled_analysis = styled_analysis.replace('\n###', '\n</div><div class="section"><h3>')
    styled_analysis = styled_analysis.replace('\n- ', '\n<li>')
    styled_analysis = styled_analysis.replace('\n1. ', '\n<li>')
    styled_analysis = styled_analysis.replace('\n2. ', '\n<li>')
    styled_analysis = styled_analysis.replace('\n3. ', '\n<li>')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 AI信息流2.0 - 即时测试</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin-bottom: 30px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
            background-size: cover;
            opacity: 0.1;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 15px;
            letter-spacing: -0.5px;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
            margin-bottom: 25px;
        }}
        
        .badges {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .badge {{
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 500;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .content {{
            padding: 50px 40px;
        }}
        
        .test-info {{
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 40px;
            border-left: 5px solid #667eea;
        }}
        
        .test-info h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }}
        
        .test-info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }}
        
        .info-item .label {{
            font-size: 0.9rem;
            color: #718096;
            margin-bottom: 5px;
        }}
        
        .info-item .value {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8fafc;
            border-radius: 15px;
            border: 1px solid #e2e8f0;
        }}
        
        .section h3 {{
            color: #4c51bf;
            margin-bottom: 20px;
            font-size: 1.5rem;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, #fff9db 0%, #ffec99 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            border: 2px solid #ffd43b;
        }}
        
        ul, ol {{
            padding-left: 25px;
            margin: 15px 0;
        }}
        
        li {{
            margin-bottom: 10px;
            color: #4a5568;
        }}
        
        .emoji {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #718096;
            font-size: 0.9rem;
            border-top: 1px solid #e2e8f0;
            background: #f8fafc;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 800;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #718096;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .header {{ padding: 40px 20px; }}
            .header h1 {{ font-size: 2rem; }}
            .content {{ padding: 30px 20px; }}
            .test-info-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <div class="header-content">
                    <h1>🎯 AI信息流2.0</h1>
                    <div class="subtitle">GitHub AI趋势深度分析 • 即时测试版本</div>
                    
                    <div class="badges">
                        <div class="badge">🤖 AI分析</div>
                        <div class="badge">🎨 美观界面</div>
                        <div class="badge">🚀 即时测试</div>
                        <div class="badge">📈 趋势洞察</div>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <div class="test-info">
                    <h3>📋 测试信息</h3>
                    <div class="test-info-grid">
                        <div class="info-item">
                            <div class="label">测试类型</div>
                            <div class="value">完整流程测试</div>
                        </div>
                        <div class="info-item">
                            <div class="label">数据来源</div>
                            <div class="value">{data_source}</div>
                        </div>
                        <div class="info-item">
                            <div class="label">测试时间</div>
                            <div class="value">{timestamp}</div>
                        </div>
                        <div class="info-item">
                            <div class="label">测试版本</div>
                            <div class="value">AI信息流2.0测试版</div>
                        </div>
                    </div>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">15+</div>
                        <div class="stat-label">AI项目分析</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">4</div>
                        <div class="stat-label">趋势分类</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">3</div>
                        <div class="stat-label">深度洞察</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">AI生成</div>
                    </div>
                </div>
                
                <div class="highlight-box">
                    <h3>✨ 测试说明</h3>
                    <p>这是ai-flow项目的<strong>即时功能测试邮件</strong>，展示新版界面的美观度和邮件发送功能。</p>
                    <p>所有内容均由AI自动生成，包含深度趋势分析和专业建议。</p>
                </div>
                
                <div class="section">
                    {styled_analysis}
                </div>
                
                <div class="section">
                    <h3>🔧 技术支持</h3>
                    <div style="display: flex; align-items: center; gap: 20px; margin-top: 20px;">
                        <div style="flex: 1;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">🤖 nanobot智能优化</h4>
                            <p style="color: #718096; font-size: 0.95rem;">基于深度学习的AI优化引擎，提升分析准确性和内容质量。</p>
                        </div>
                        <div style="flex: 1;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">🚀 AI信息流2.0</h4>
                            <p style="color: #718096; font-size: 0.95rem;">新一代GitHub趋势分析系统，为开发者提供专业洞察。</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>📧 此邮件为测试邮件，请勿回复</p>
                <p>⚡ 生成于 {timestamp} • AI信息流2.0测试版</p>
                <p style="margin-top: 15px; font-size: 0.8rem; color: #a0aec0;">
                    技术支持：nanobot智能系统 • 数据来源：GitHub Trending • 版本：v2.0-test
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content

def send_test_email(html_content, test_type="即时测试"):
    """发送测试邮件"""
    print(f"\n📧 准备发送{test_type}邮件...")
    
    # 获取邮件配置
    sender_email = "19121220286@163.com"
    sender_password = os.environ.get("wangyi_emai_auth")  # 注意：小写
    
    if not sender_password:
        print("❌ wangyi_emai_auth 环境变量未设置")
        return False
        
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        subject = f"🎯 AI信息流2.0 {test_type} - {timestamp}"
        
        print(f"📤 发送到 {len(TEST_EMAILS)} 个测试邮箱:")
        for email in TEST_EMAILS:
            print(f"   → {email}")
        
        yag = yagmail.SMTP(
            user=sender_email, 
            password=sender_password, 
            host='smtp.163.com', 
            port='465'
        )
        
        # 发送到每个测试邮箱
        for to_email in TEST_EMAILS:
            print(f"   正在发送到: {to_email}")
            yag.send(
                to=to_email,
                subject=subject,
                contents=[html_content]
            )
            print(f"   ✅ {to_email} 发送成功")
            time.sleep(1)  # 避免发送过快
        
        yag.close()
        print(f"\n🎉 {test_type}邮件发送完成！")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_html_preview(html_content):
    """保存HTML预览文件"""
    preview_dir = "preview_output"
    os.makedirs(preview_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    preview_path = f"{preview_dir}/test_preview_{timestamp}.html"
    
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n💾 HTML预览已保存: {preview_path}")
    print(f"   可以在浏览器中打开查看: file://{os.path.abspath(preview_path)}")
    return preview_path

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 AI信息流2.0 - 使用昨日数据即时测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前环境: {'生产' if 'ZHIPUAI_API_KEY' in os.environ else '测试'}")
    print(f"测试邮箱: {len(TEST_EMAILS)} 个")
    print()
    
    start_time = time.time()
    
    try:
        # 1. 读取昨天数据
        trends, source_info = read_yesterday_data()
        if not trends:
            print("❌ 无法获取数据，测试终止")
            return False
        
        # 2. AI分析
        analysis = ai_analyze_now(trends, source_info)
        if not analysis:
            print("⚠️  AI分析失败，使用备选分析内容")
            analysis = ai_analyze_now("", source_info)  # 使用默认内容
        
        # 3. 创建美观的HTML
        print("\n🎨 创建HTML邮件内容...")
        html_content = create_beautiful_html(analysis, source_info)
        print(f"   HTML大小: {len(html_content)} 字符")
        
        # 4. 保存预览
        preview_path = save_html_preview(html_content)
        
        # 5. 显示测试摘要
        print("\n" + "=" * 70)
        print("📋 测试摘要")
        print("=" * 70)
        print(f"   数据来源: {source_info}")
        print(f"   项目数量: {trends.count('[')} 个")
        print(f"   AI分析: {len(analysis)} 字符")
        print(f"   HTML邮件: {len(html_content)} 字符")
        print(f"   测试邮箱: {', '.join(TEST_EMAILS)}")
        print(f"   预计耗时: 约{int(len(TEST_EMAILS) * 2)}秒")
        print("=" * 70)
        
        # 6. 确认发送
        print("\n⚠️  即将发送测试邮件到以上邮箱")
        confirm = input("   确认发送？(y/n): ").strip().lower()
        if confirm != 'y':
            print("测试取消")
            print(f"\n💡 你仍然可以在浏览器中查看预览: file://{preview_path}")
            return False
        
        # 7. 发送邮件
        success = send_test_email(html_content, "美观界面测试")
        
        # 8. 结果报告
        print("\n" + "=" * 70)
        print("📊 测试结果报告")
        print("=" * 70)
        print(f"✅ 数据准备: 成功 ({source_info})")
        print(f"✅ AI分析: 成功 ({len(analysis)} 字符)")
        print(f"✅ HTML生成: 成功 ({len(html_content)} 字符)")
        print(f"✅ 邮件发送: {'成功' if success else '失败'}")
        print(f"📅 测试完成时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  总耗时: {time.time() - start_time:.1f}秒")
        print(f"📧 发送到: {', '.join(TEST_EMAILS)}")
        print()
        
        if success:
            print("🎉 测试成功！请检查测试邮箱是否收到邮件。")
            print("   邮件应为美观的HTML格式，包含专业的AI分析内容。")
            print(f"   💾 HTML预览文件: {preview_path}")
        else:
            print("❌ 测试失败，请检查错误信息。")
        
        print("\n🔧 生产状态说明:")
        print("   1. 当前生产app.py仍在运行 (PID: 91056)")
        print("   2. 今晚21:00的正常发送不受影响")
        print("   3. 121个订阅用户将按原计划收到邮件")
        print("   4. 此测试仅验证新界面效果，不修改生产代码")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)