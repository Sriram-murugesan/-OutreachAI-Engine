import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

message = Mail(
    from_email=os.getenv("SENDER_EMAIL"),
    to_emails="freelelo07@gmail.com",
    subject="Test email - direct SendGrid check",
    plain_text_content="This is a raw test bypassing the app."
)

try:
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    response = sg.send(message)
    print("Status code:", response.status_code)
    print("Headers:", response.headers)
    print("Body:", response.body)
except Exception as e:
    print("Exception:", type(e).__name__, str(e))