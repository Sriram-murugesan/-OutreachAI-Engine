import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from db.supabase_client import supabase

load_dotenv()


def send_email(to_email: str, subject: str, body: str, email_id: str) -> bool:
    """Send a cold email via SendGrid and update status in Supabase."""

    # Parse subject line from email body (our format: first line is "Subject: ...")
    lines = body.strip().splitlines()
    subject_line = subject
    email_body = body

    for i, line in enumerate(lines):
        if line.startswith("Subject:"):
            subject_line = line.replace("Subject:", "").strip()
            email_body = "\n".join(lines[i + 1:]).strip()
            break

    message = Mail(
        from_email=os.getenv("SENDER_EMAIL"),
        to_emails=to_email,
        subject=subject_line,
        plain_text_content=email_body
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        if response.status_code in [200, 202]:
            # Update status in Supabase
            from datetime import datetime, timezone
            supabase.table("emails").update({
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", email_id).execute()
            return True
        return False

    except Exception as e:
        print(f"SendGrid error: {e}")
        return False