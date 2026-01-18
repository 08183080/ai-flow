import os
import yagmail

def get_emails(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def send_email(src, dst, subject, contents, attachments):
    pwd = os.environ.get('wangyi_emai_auth')
    yag = yagmail.SMTP(user=src, password=pwd, host='smtp.163.com', port='465')
    yag.send(to=dst, subject=subject, contents=contents, attachments=attachments)
    yag.close()

def send_announcement():
    src = '19121220286@163.com'
    tos = get_emails('emails.txt')
    subject = 'AI信息流复活通知'
    contents = '''各位老客户们好！

AI信息流复活了，继续存在一年。

各位老客户们随缘付费，接下来每天晚上会继续自动智能推送。

谢谢支持！

---
谢苹果
AI信息流 2.0'''
    
    print(f'准备发送邮件给 {len(tos)} 位客户...')
    for i, to in enumerate(tos, 1):
        try:
            send_email(src, to, subject, contents, 'AI信息流.jpg')
            print(f'{i}/{len(tos)} ✓ {to}')
        except Exception as e:
            print(f'{i}/{len(tos)} ✗ {to} - {e}')
    
    print('发送完成！')

if __name__ == '__main__':
    send_announcement()
