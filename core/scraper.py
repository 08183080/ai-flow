"""
GitHub趋势爬虫模块
"""
import requests
import time
import json
from typing import List, Optional, Tuple
from datetime import datetime
from pyquery import PyQuery as pq
import codecs


class GitHubTrendingScraper:
    """GitHub趋势爬虫"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://github.com/trending"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
    
    def scrape(self, language: str = "python", output_file: Optional[str] = None) -> Tuple[bool, List[dict]]:
        """
        爬取GitHub趋势
        
        Args:
            language: 编程语言（如python, rust等）
            output_file: 输出文件路径（可选）
            
        Returns:
            (是否成功, 项目列表)
        """
        attempts = 0
        last_error = None
        
        while attempts < self.max_retries:
            try:
                print(f"🌐 尝试爬取GitHub {language} 趋势 (尝试 {attempts + 1}/{self.max_retries})...")
                
                # 构建URL
                url = f"{self.base_url}/{language}"
                if language == "all":
                    url = self.base_url
                
                # 发送请求
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                
                print(f"📡 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    projects = self.parse_response(response.content, language)
                    
                    if projects:
                        print(f"✅ 成功爬取 {len(projects)} 个项目")
                        
                        # 保存到文件（如果需要）
                        if output_file:
                            self.save_projects(projects, output_file, language)
                        
                        return True, projects
                    else:
                        print("⚠️  爬取成功但未解析到项目")
                        return False, []
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    last_error = f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print("⏰ 请求超时")
                last_error = "Timeout"
            except requests.exceptions.ConnectionError:
                print("🔌 连接错误")
                last_error = "ConnectionError"
            except Exception as e:
                print(f"❌ 爬取失败: {e}")
                last_error = str(e)
            
            attempts += 1
            
            if attempts < self.max_retries:
                wait_time = 2 ** attempts  # 指数退避
                print(f"⏱️  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print(f"❌ 所有尝试失败: {last_error}")
        return False, []
    
    def parse_response(self, html_content: bytes, language: str) -> List[dict]:
        """
        解析HTML响应
        
        Args:
            html_content: HTML内容
            language: 编程语言
            
        Returns:
            项目列表
        """
        try:
            d = pq(html_content)
            items = d('div.Box article.Box-row')
            
            projects = []
            for index, item in enumerate(items, start=1):
                i = pq(item)
                
                # 提取项目信息
                title_element = i(".lh-condensed a")
                title = title_element.text().strip()
                
                # 提取URL
                relative_url = title_element.attr("href")
                url = f"https://github.com{relative_url}" if relative_url else ""
                
                # 提取描述
                description = i("p.col-9").text().strip()
                
                # 提取额外信息（stars, forks等）
                stars_text = i(f"span[aria-label*='star']").text().strip()
                forks_text = i(f"span[aria-label*='fork']").text().strip()
                stars_today_text = i("span.float-sm-right").text().strip()
                
                # 尝试提取stars数
                stars = self.extract_number(stars_text)
                forks = self.extract_number(forks_text)
                stars_today = self.extract_stars_today(stars_today_text)
                
                # 构建项目对象
                project = {
                    "index": index,
                    "title": title,
                    "description": description,
                    "url": url,
                    "language": language,
                    "stars": stars,
                    "forks": forks,
                    "stars_today": stars_today,
                    "full_title": title,
                    "scraped_at": datetime.now().isoformat()
                }
                
                projects.append(project)
            
            return projects
            
        except Exception as e:
            print(f"解析HTML失败: {e}")
            return []
    
    def extract_number(self, text: str) -> Optional[int]:
        """从文本中提取数字"""
        if not text:
            return None
        
        # 移除千分位逗号，提取数字
        import re
        match = re.search(r'[\d,]+', text.replace(',', ''))
        if match:
            try:
                return int(match.group())
            except ValueError:
                return None
        return None
    
    def extract_stars_today(self, text: str) -> Optional[int]:
        """提取今日stars数"""
        if not text:
            return None
        
        import re
        match = re.search(r'(\d+)\s*stars today', text.lower())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
    
    def save_projects(self, projects: List[dict], output_file: str, language: str):
        """
        保存项目到文件
        
        Args:
            projects: 项目列表
            output_file: 输出文件路径
            language: 编程语言
        """
        try:
            # 保存为JSON格式
            json_file = output_file.replace('.txt', '.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "language": language,
                    "scraped_at": datetime.now().isoformat(),
                    "total_projects": len(projects),
                    "projects": projects
                }, f, ensure_ascii=False, indent=2)
            
            # 保存为文本格式（兼容原有格式）
            with codecs.open(output_file, "w", "utf-8") as f:
                for project in projects:
                    f.write(f"{project['index']}. [{project['title']}]:{project['description']}({project['url']})\n")
            
            print(f"💾 项目数据已保存到: {output_file}")
            
        except Exception as e:
            print(f"保存文件失败: {e}")
    
    def test_connection(self) -> bool:
        """测试GitHub连接"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False