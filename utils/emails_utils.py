import imaplib
import email
from email.header import decode_header
import re
import time

def fetch_otp(username, app_password_2):
    time.sleep(20)
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, app_password_2)
    imap.select("inbox")
    
    # Search for all emails
    status, messages = imap.search(None, "ALL")
    message_ids = messages[0].split()[-5:]  # Get the last 5 email IDs

    otp_list = []  # To store all found OTPs

    # Loop through the messages
    for mail_id in message_ids:
        status, msg_data = imap.fetch(mail_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the email
                msg = email.message_from_bytes(response_part[1])

                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')

                # Check if the subject matches "OTP for Net Banking login"
                if subject == "OTP for Net Banking login":
                    body = msg.as_string()     
                    # Use regex to extract the OTP (4-6 digit number)
                    otp_match = re.search(r'\b\d{6}\b', body)
                    if otp_match:
                        otp = otp_match.group(0)
                        otp_list.append({
                            'subject': subject,
                            'otp': otp,
                            'from': msg.get("From")
                        })
                        print(f"OTP found: {otp}")
                        break

    return otp if otp_list else None
