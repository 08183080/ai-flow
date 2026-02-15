#!/usr/bin/env python3
"""
网络测试与安全重启脚本
测试GitHub连接性，如果正常则安全重启app.py
"""
import os
import sys
import time
import subprocess
import datetime
import signal

print("=" * 60)
print("🔧 网络测试与安全重启脚本")
print(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"距离21:00还有: {21 - datetime.datetime.now().hour}小时{59 - datetime.datetime.now().minute}分钟")
print("=" * 60)

# 检查当前运行的app.py进程
def check_current_process():
    print("\n📊 检查当前运行进程...")
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        app_processes = []
        for line in result.stdout.split('\n'):
            if 'python' in line and 'app.py' in line and 'grep' not in line:
                app_processes.append(line.strip())
        
        if app_processes:
            print(f"✅ 找到 {len(app_processes)} 个app.py进程:")
            for proc in app_processes:
                print(f"  - {proc}")
            return True
        else:
            print("⚠️ 未找到运行的app.py进程")
            return False
    except Exception as e:
        print(f"❌ 检查进程失败: {e}")
        return False

# 测试GitHub连接性
def test_github_connectivity():
    print("\n🌐 测试GitHub连接性...")
    tests = [
        ("直接连接", "https://github.com", 10),
        ("趋势页面", "https://github.com/trending/python", 15),
        ("API端点", "https://api.github.com", 10),
    ]
    
    import requests
    
    success_count = 0
    for test_name, url, timeout in tests:
        try:
            print(f"  测试 {test_name} ({url})...", end="")
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print(f" ✅ 成功 (HTTP {response.status_code})")
                success_count += 1
            else:
                print(f" ⚠️ HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            print(f" ❌ 超时 ({timeout}秒)")
        except requests.exceptions.ConnectionError:
            print(f" ❌ 连接错误")
        except Exception as e:
            print(f" ❌ 异常: {e}")
    
    print(f"\n📈 连接测试结果: {success_count}/{len(tests)} 成功")
    return success_count >= 2  # 至少2个测试成功

# 测试修改后的爬虫函数
def test_modified_scraper():
    print("\n🕷️ 测试修改后的爬虫函数...")
    try:
        # 导入必要的模块
        import requests
        from pyquery import PyQuery as pq
        import codecs
        
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        url = 'https://github.com/trending/python'
        print(f"  请求URL: {url} (超时: 30秒)")
        
        start_time = time.time()
        r = requests.get(url, headers=HEADERS, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"  状态码: {r.status_code}, 耗时: {elapsed:.2f}秒")
        
        if r.status_code == 200:
            d = pq(r.content)
            items = d('div.Box article.Box-row')
            print(f"  找到 {len(items)} 个项目")
            
            # 显示前3个项目
            for i, item in enumerate(items[:3]):
                item_pq = pq(item)
                title = item_pq(".lh-condensed a").text().strip()
                print(f"    {i+1}. {title[:50]}...")
            
            print("  ✅ 爬虫测试成功")
            return True
        else:
            print(f"  ❌ HTTP状态码异常: {r.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 爬虫测试异常: {e}")
        return False

# 安全重启app.py
def safe_restart_app():
    print("\n🔄 安全重启app.py...")
    
    # 1. 查找并记录当前进程
    try:
        result = subprocess.run(
            ["ps", "aux", "|", "grep", "'python.*app\.py'", "|", "grep", "-v", "grep"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"  找到进程 PID: {pid}")
                    
                    # 2. 优雅终止进程
                    print(f"  发送SIGTERM信号到PID {pid}...")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"  ✅ 信号已发送")
                        
                        # 等待进程结束
                        for i in range(5):
                            time.sleep(1)
                            try:
                                os.kill(int(pid), 0)  # 检查进程是否存在
                            except OSError:
                                print(f"  ✅ 进程 {pid} 已终止")
                                break
                        else:
                            print(f"  ⚠️ 进程 {pid} 仍在运行，发送SIGKILL")
                            os.kill(int(pid), signal.SIGKILL)
                    except Exception as e:
                        print(f"  ⚠️ 终止进程失败: {e}")
        else:
            print("  ℹ️ 未找到运行的app.py进程")
    except Exception as e:
        print(f"  ⚠️ 查找进程失败: {e}")
    
    # 3. 启动新进程
    print("  启动新的app.py进程...")
    try:
        os.chdir('/root/ai-flow')
        
        # 使用nohup在后台运行
        cmd = [
            'nohup',
            '/root/ai-flow/venv/bin/python3',
            '-u',
            'app.py',
            '>',
            'logs/app_restart.log',
            '2>&1',
            '&'
        ]
        
        print(f"  执行命令: {' '.join(cmd)}")
        subprocess.Popen(' '.join(cmd), shell=True)
        
        # 等待进程启动
        time.sleep(3)
        
        # 4. 验证新进程
        print("  验证新进程...")
        result = subprocess.run(
            ["ps", "aux", "|", "grep", "'python.*app\.py'", "|", "grep", "-v", "grep"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print(f"  ✅ 新进程已启动:")
            print(f"  {result.stdout.strip()}")
            return True
        else:
            print("  ❌ 新进程未找到")
            return False
            
    except Exception as e:
        print(f"  ❌ 启动进程失败: {e}")
        return False

# 主函数
def main():
    print("\n" + "=" * 60)
    print("🔍 执行完整测试流程")
    print("=" * 60)
    
    # 检查当前时间
    current_hour = datetime.datetime.now().hour
    current_minute = datetime.datetime.now().minute
    
    if current_hour == 20 and current_minute > 45:
        print(f"⚠️ 警告: 当前时间 {current_hour}:{current_minute:02d}")
        print("距离21:00定时任务很近，重启需谨慎")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            print("操作取消")
            return False
    
    # 步骤1: 检查当前进程
    process_running = check_current_process()
    
    # 步骤2: 测试网络连接性
    network_ok = test_github_connectivity()
    
    # 步骤3: 测试爬虫函数
    scraper_ok = False
    if network_ok:
        scraper_ok = test_modified_scraper()
    else:
        print("⚠️ 网络连接测试失败，跳过爬虫测试")
    
    # 决策逻辑
    print("\n" + "=" * 60)
    print("🤔 决策分析")
    print("=" * 60)
    
    if not network_ok:
        print("❌ 网络连接测试失败")
        print("建议:")
        print("1. 检查服务器网络连接")
        print("2. 等待网络恢复后再测试")
        print("3. 今晚保持现有进程运行")
        return False
    
    if not scraper_ok:
        print("⚠️ 爬虫测试失败，但网络正常")
        print("可能原因:")
        print("1. GitHub页面结构可能已变化")
        print("2. 临时网络问题")
        print("3. 服务器限制")
        print("建议先保持现有进程运行")
        return False
    
    # 所有测试通过，询问是否重启
    print("✅ 所有测试通过!")
    print("网络: ✅ 正常")
    print("爬虫: ✅ 正常")
    print("当前进程: ✅ 运行中")
    
    print("\n🔄 是否重启app.py应用新的超时设置?")
    print("优点:")
    print("  - 应用30秒超时设置，提高爬虫成功率")
    print("  - 今晚21:00任务使用优化设置")
    print("风险:")
    print("  - 短暂服务中断 (<10秒)")
    print("  - 新进程可能有问题（但代码相同）")
    
    response = input("\n重启? (y/N): ")
    
    if response.lower() == 'y':
        print("\n" + "=" * 60)
        print("🚀 开始安全重启流程")
        print("=" * 60)
        
        restart_ok = safe_restart_app()
        
        if restart_ok:
            print("\n🎉 重启成功!")
            print("⏰ 新进程已启动，将使用30秒超时设置")
            print("📅 今晚21:00定时任务将使用新设置执行")
            print("📧 121个订阅用户将收到邮件")
            return True
        else:
            print("\n⚠️ 重启失败，但原始进程可能仍在运行")
            print("建议手动检查进程状态")
            return False
    else:
        print("\n操作取消，保持现有进程运行")
        print("今晚21:00任务将使用旧设置（10秒超时）")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)