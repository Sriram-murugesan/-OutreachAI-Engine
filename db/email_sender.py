import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from db.supabase_client import supabase

load_dotenv()


def send_email(to_email: str, subject: str, body: str, email_id: str) -> tuple[bool, str]:
    """Send a cold email via SendGrid and update status in Supabase.
    Returns (success, error_message)."""

    lines = body.strip().splitlines()
    subject_line = subject
    email_body = body

    for i, line in enumerate(lines):
        if line.startswith("Subject:"):
            subject_line = line.replace("Subject:", "").strip()
            email_body = "\n".join(lines[i + 1:]).strip()
            break

    sender = os.getenv("SENDER_EMAIL")
    if not sender:
        return False, "SENDER_EMAIL not set in environment"

    message = Mail(
        from_email=sender,
        to_emails=to_email,
        subject=subject_line,
        plain_text_content=email_body
    )

    try:
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            return False, "SENDGRID_API_KEY not set in environment"

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code in [200, 202]:
            from datetime import datetime, timezone
            supabase.table("emails").update({
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", email_id).execute()
            return True, ""
        else:
            return False, f"SendGrid returned status {response.status_code}: {response.body}"

    except Exception as e:
        return False, str(e)