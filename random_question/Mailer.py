import smtplib
from email.message import EmailMessage
from password import passw  # Make sure this is a strong Gmail App Password

class Mail:

    def send_mail(self, recipient_email,ip_address,token):
        # Gmail account settings
        GMAIL_ADDRESS = '02syedshaiksha@gmail.com'
        GMAIL_APP_PASSWORD = passw

        # Create the email message
        msg = EmailMessage()
        msg['Subject'] = "Your Coding Test Question Assignment"
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Reply-To'] = GMAIL_ADDRESS
        msg['Return-Path'] = GMAIL_ADDRESS

        # Email body (avoid casual "hey", avoid links if not needed)
        msg.set_content(f"""
Dear Student,

You have been assigned a coding test question through the SkillAssess platform.

    link for the test: http://{ip_address}:5010/test/{token}

Please log in to the SkillAssess exam portal and begin your test. Do not share this ID.

If you have any concerns, please reach out to your exam coordinator.

Best regards,  
SkillAssess Exam Team  
contact@skillassess.in
""")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.send_message(msg)
                print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {e}")
            return f"Failed to send email to {recipient_email}: {e}"
