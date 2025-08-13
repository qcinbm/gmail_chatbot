import os
import re
import openpyxl
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes

# Phạm vi quyền Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Hàm đăng nhập Google OAuth
def gmail_login():
    # Tạo flow đăng nhập
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # Mở trình duyệt để người dùng đăng nhập
    creds = flow.run_local_server(port=0)
    return creds

# Hàm lấy email
def fetch_emails():
    creds = gmail_login()
    service = build('gmail', 'v1', credentials=creds)

    # Tìm email có từ khóa "Order Confirmation"
    results = service.users().messages().list(userId='me', q='"Order Confirmation"').execute()
    messages = results.get('messages', [])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Name", "Email"])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_data = base64.urlsafe_b64decode(msg_data['raw'])
        email_msg = message_from_bytes(raw_data)

        # Lấy nội dung
        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode(errors='ignore')
        else:
            body = email_msg.get_payload(decode=True).decode(errors='ignore')

        # Tìm email & tên
        emails_found = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', body)
        name_match = re.search(r'Name:\s*(\w+)', body)
        name = name_match.group(1) if name_match else ""

        for email_found in emails_found:
            ws.append([name, email_found])

    wb.save("data.xlsx")
    print("Đã lưu vào data.xlsx")

if __name__ == "__main__":
    fetch_emails()
