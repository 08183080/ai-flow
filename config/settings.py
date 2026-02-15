"""
配置设置模块
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class AIConfig:
    """AI配置"""
    api_key: str
    model: str = "glm-4-flash"
    max_retries: int = 6
    retry_delay: int = 300  # 秒
    timeout: int = 120  # 秒

@dataclass
class EmailConfig:
    """邮件配置"""
    sender_email: str
    sender_password: str
    smtp_host: str = "smtp.163.com"
    smtp_port: int = 465
    default_subject: str = "今日AI+头条项目"

@dataclass
class ScraperConfig:
    """爬虫配置"""
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    timeout: int = 30
    max_retries: int = 3
    base_url: str = "https://github.com/trending"

@dataclass
class TrackingConfig:
    """跟踪配置"""
    enabled: bool = False
    base_url: Optional[str] = None

@dataclass
class AppConfig:
    """应用配置"""
    log_dir: str = "logs"
    emails_file: str = "emails.txt"
    web3_emails_file: str = "web3_emails.txt"
    schedule_time: str = "21:00"  # 每日执行时间

class Config:
    """配置管理器"""
    
    def __init__(self):
        # 从环境变量获取敏感信息
        zhipu_api_key = os.environ.get("ZHIPUAI_API_KEY", "")
        email_password = os.environ.get("WANGYI_EMAIL_AUTH", "")
        sender_email = os.environ.get("SENDER_EMAIL", "19121220286@163.com")
        
        # 初始化配置
        self.ai = AIConfig(
            api_key=zhipu_api_key,
            model="glm-4-flash"
        )
        
        self.email = EmailConfig(
            sender_email=sender_email,
            sender_password=email_password
        )
        
        self.scraper = ScraperConfig()
        self.tracking = TrackingConfig()
        self.app = AppConfig()
        
    def validate(self) -> bool:
        """验证配置完整性"""
        if not self.ai.api_key:
            print("⚠️  警告: ZHIPUAI_API_KEY 未设置")
            return False
            
        if not self.email.sender_password:
            print("⚠️  警告: WANGYI_EMAIL_AUTH 未设置")
            return False
            
        return True

# 全局配置实例
config = Config()