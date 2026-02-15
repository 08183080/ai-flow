"""
邮件发送模块
"""
import os
import yagmail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from jinja2 import Template


class EmailSender:
    """邮件发送器"""
    
    def __init__(
        self,
        smtp_host: str = "smtp.163.com",
        smtp_port: int = 465,
        sender_email: str = "",
        sender_password: str = "",
        use_ssl: bool = True
    ):
        """
        初始化邮件发送器
        
        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP端口
            sender_email: 发件人邮箱
            sender_password: 发件人密码
            use_ssl: 是否使用SSL
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_ssl = use_ssl
        
        # 验证配置
        if not self.sender_email or not self.sender_password:
            raise ValueError("发件人邮箱和密码必须设置")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        发送单个邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件正文（纯文本）
            html_content: HTML内容（可选）
            attachments: 附件列表（可选）
            
        Returns:
            是否发送成功
        """
        try:
            print(f"📧 准备发送邮件到: {to_email}")
            
            # 使用yagmail发送邮件（简化实现）
            yag = yagmail.SMTP(
                user=self.sender_email,
                password=self.sender_password,
                host=self.smtp_host,
                port=self.smtp_port
            )
            
            # 构建邮件内容
            mail_contents = []
            if html_content:
                mail_contents.append(html_content)
            else:
                mail_contents.append(content)
            
            # 发送邮件
            yag.send(
                to=to_email,
                subject=subject,
                contents=mail_contents,
                attachments=attachments or []
            )
            
            yag.close()
            print(f"✅ 邮件成功发送到: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ 发送邮件到 {to_email} 失败: {e}")
            return False
    
    def send_batch_emails(
        self,
        to_emails: List[str],
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        批量发送邮件
        
        Args:
            to_emails: 收件人邮箱列表
            subject: 邮件主题
            content: 邮件正文
            html_content: HTML内容（可选）
            attachments: 附件列表（可选）
            
        Returns:
            发送结果字典 {邮箱: 是否成功}
        """
        results = {}
        total = len(to_emails)
        
        print(f"📨 开始批量发送邮件，共 {total} 个收件人...")
        
        for i, email in enumerate(to_emails, 1):
            print(f"📤 发送进度: {i}/{total} ({email})")
            
            success = self.send_email(
                to_email=email,
                subject=subject,
                content=content,
                html_content=html_content,
                attachments=attachments
            )
            
            results[email] = success
            
            # 为了避免被邮件服务器限制，添加延迟
            if i < total:
                import time
                time.sleep(1)  # 1秒延迟
        
        # 统计结果
        success_count = sum(1 for success in results.values() if success)
        print(f"📊 批量发送完成: {success_count}/{total} 成功")
        
        return results
    
    def send_trending_email(
        self,
        to_emails: List[str],
        language: str,
        date: str,
        analysis_result: str,
        template_path: Optional[str] = None,
        tracking_url: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        发送趋势分析邮件
        
        Args:
            to_emails: 收件人列表
            language: 语言（python/web3）
            date: 日期
            analysis_result: 分析结果
            template_path: HTML模板路径（可选）
            tracking_url: 跟踪URL（可选）
            
        Returns:
            发送结果
        """
        try:
            # 构建邮件主题
            if language.lower() == "python":
                subject = f"🚀 {date} AI趋势分析报告"
            elif language.lower() == "rust":
                subject = f"🔗 {date} Web3趋势分析报告"
            else:
                subject = f"📊 {date} GitHub趋势分析报告"
            
            # 处理HTML内容
            html_content = None
            if template_path and os.path.exists(template_path):
                html_content = self.render_html_template(
                    template_path,
                    {
                        "date": date,
                        "language": language,
                        "analysis": analysis_result,
                        "highlight_project": {
                            "title": "待解析项目",
                            "description": "通过AI分析选出的最惊艳项目",
                            "tag_class": "ai",
                            "tag": "AI创新"
                        },
                        "categories": [
                            {"name": "AI平台", "count": 3, "examples": "项目A、项目B、项目C"},
                            {"name": "开发者工具", "count": 5, "examples": "项目D、项目E"}
                        ],
                        "trends": ["AI技术创新", "开源工具增多", "实用性提升"],
                        "insights": ["洞察点1", "洞察点2", "洞察点3"],
                        "prediction": "基于今日趋势的分析预测",
                        "project_count": 15,
                        "category_count": 5,
                        "subscriber_count": len(to_emails)
                    }
                )
            
            # 发送邮件
            results = self.send_batch_emails(
                to_emails=to_emails,
                subject=subject,
                content=analysis_result,
                html_content=html_content
            )
            
            # 记录发送日志
            self.log_email_sending(date, language, len(to_emails), results)
            
            return results
            
        except Exception as e:
            print(f"❌ 发送趋势分析邮件失败: {e}")
            return {}
    
    def render_html_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        渲染HTML模板
        
        Args:
            template_path: 模板文件路径
            context: 模板上下文
            
        Returns:
            渲染后的HTML
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            html_content = template.render(**context)
            
            return html_content
            
        except Exception as e:
            print(f"❌ 渲染HTML模板失败: {e}")
            return ""
    
    def log_email_sending(
        self,
        date: str,
        language: str,
        total_recipients: int,
        results: Dict[str, bool]
    ):
        """
        记录邮件发送日志
        
        Args:
            date: 日期
            language: 语言
            total_recipients: 总收件人数
            results: 发送结果
        """
        log_dir = "logs/email_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"{date}_{language}.json")
        
        log_data = {
            "date": date,
            "language": language,
            "sent_at": datetime.now().isoformat(),
            "total_recipients": total_recipients,
            "success_count": sum(1 for success in results.values() if success),
            "failure_count": sum(1 for success in results.values() if not success),
            "recipients": list(results.keys())[:10]  # 只记录前10个
        }
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            print(f"📝 邮件发送日志已保存到: {log_file}")
            
        except Exception as e:
            print(f"❌ 保存邮件日志失败: {e}")
    
    def test_connection(self) -> bool:
        """测试邮件服务器连接"""
        try:
            print(f"🔍 测试邮件服务器连接: {self.smtp_host}:{self.smtp_port}")
            
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            server.login(self.sender_email, self.sender_password)
            server.quit()
            
            print("✅ 邮件服务器连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 邮件服务器连接失败: {e}")
            return False