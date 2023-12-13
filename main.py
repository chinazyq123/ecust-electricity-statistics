from contextlib import suppress
from pathlib import Path
import json
import datetime
import os
import requests
import re
import smtplib
from email.mime.text import MIMEText

# Retrieve data from the specified URL
url = os.environ.get('URL').strip()
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'yktyd.ecust.edu.cn',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.1.2; zh-cn; Chitanda/Akari) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30 MicroMessenger/6.0.0.58_r884092.501 NetType/WIFI'
    # ... headers ...
}
response = requests.get(url, headers=header)
remain = float(re.findall(r"(\d+(\.\d+)?)度", response.text)[0][0])

# Update data in the JSON file
originstring = '[]'
data = []
date = datetime.datetime.now().strftime("%Y-%m-%d")

with suppress(FileNotFoundError):
    with open("data.js", 'r', encoding='utf-8') as f:
        originstring = f.read().lstrip("data=")

data = json.loads(originstring)
if len(data) != 0 and date in data[-1].values():
    data[-1]['kWh'] = remain
else:
    data.append({"time": date, "kWh": remain})

originstring = json.dumps(data, indent=4, ensure_ascii=False)
Path("data.js").write_text("data=" + originstring)

# Send email if remaining electricity is below 30
if remain < 30:
    sender_email = os.environ.get('MAIL').strip()
    receiver_emails = ["bestzyq@foxmail.com", "1162358837@qq.com", "2776820836@qq.com", "1305955806@qq.com"]
    subject = "低电量提醒"
    message = f"剩余电量不足20度，请及时充电。剩余电量：{remain} kWh."

    # Create a plain text email message
    email = MIMEText(message)
    email["Subject"] = subject
    email["From"] = sender_email
    email["To"] = ", ".join(receiver_emails)
    
    # 明确打印 MAIL 和 PWD 的值
    print(f"DEBUG: MAIL={os.environ.get('MAIL')}")
    print(f"DEBUG: PWD={os.environ.get('PWD')}")
    
    # 输出明文值到日志
    print("MAIL=" + os.environ.get('MAIL'))
    print("PWD=" + os.environ.get('PWD'))

    # Send the email using SSL
    smtp_server = "smtp.exmail.qq.com"
    smtp_port = 465  # 使用 SSL 连接的常见端口号
    smtp_username = sender_email
    smtp_password = os.environ.get('PWD').strip()

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.send_message(email)
