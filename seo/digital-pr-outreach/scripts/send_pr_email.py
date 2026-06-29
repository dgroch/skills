#!/usr/bin/env python3
"""
Send PR emails via IMAP/SMTP from media@figandbloom.com.
NEVER use gws or Gmail API. NEVER send from admin@.

Usage:
  python3 send_pr_email.py --to "journalist@example.com" --subject "Subject" --body-file /path/to/body.txt
  python3 send_pr_email.py --to "journalist@example.com" --subject "Subject" --body "Inline body text"

BCCs admin@figandbloom.com on every email automatically.
"""
import smtplib, ssl, argparse, sys
from email.message import EmailMessage

# Read credentials from director .env
env = {}
with open('/opt/data/profiles/director/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('EMAIL_') and '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            env[key] = val

SMTP_HOST = env.get('EMAIL_SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(env.get('EMAIL_SMTP_PORT', '587'))
MEDIA_ADDR = env.get('EMAIL_ADDRESS', 'media@figandbloom.com')
MEDIA_PASS = env.get('EMAIL_PASSWORD', '')
BCC_ADDR = 'admin@figandbloom.com'

def send_pr_email(to_addr, subject, body):
    msg = EmailMessage()
    msg['From'] = f"Dan Groch | Fig & Bloom <{MEDIA_ADDR}>"
    msg['To'] = to_addr
    msg['Bcc'] = BCC_ADDR
    msg['Subject'] = subject
    msg.set_content(body)
    
    context = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(MEDIA_ADDR, MEDIA_PASS)
    server.send_message(msg, from_addr=MEDIA_ADDR, to_addrs=[to_addr, BCC_ADDR])
    server.quit()
    print(f"Sent to {to_addr} from {MEDIA_ADDR}")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send PR email from media@figandbloom.com')
    parser.add_argument('--to', required=True, help='Recipient email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', help='Email body (inline)')
    parser.add_argument('--body-file', help='File containing email body')
    args = parser.parse_args()
    
    if args.body_file:
        with open(args.body_file, 'r') as f:
            body = f.read()
    elif args.body:
        body = args.body
    else:
        print("Error: --body or --body-file required", file=sys.stderr)
        sys.exit(1)
    
    try:
        send_pr_email(args.to, args.subject, body)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)