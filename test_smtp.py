#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime

def test_smtp():
    # SMTP configuration
    smtp_server = 'smtp.163.com'
    smtp_port = 465
    username = '19121220286@163.com'
    password = 'AMrFUvW36qjpC5Cs'  # 授权码
    
    # Create message
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'SMTP测试 {current_time}'
    body = '这是一个简单的SMTP连接测试。'
    
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = username
    msg['To'] = 'pxxhl@qq.com'
    
    print(f'📧 测试SMTP连接...')
    print(f'服务器: {smtp_server}:{smtp_port}')
    print(f'发件人: {username}')
    print(f'收件人: pxxhl@qq.com')
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        print('✅ SSL连接成功')
        
        # Login
        server.login(username, password)
        print('✅ 登录成功')
        
        # Send email
        server.sendmail(username, ['pxxhl@qq.com'], msg.as_string())
        print('✅ 邮件发送成功')
        
        server.quit()
        return True
        
    except smtplib.SMTPException as e:
        print(f'❌ SMTP错误: {e}')
        return False
    except Exception as e:
        print(f'❌ 其他错误: {e}')
        return False

if __name__ == '__main__':
    test_smtp()