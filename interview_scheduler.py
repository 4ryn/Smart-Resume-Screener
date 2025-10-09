import sqlite3
import smtplib
import random
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import DB_PATH, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

# Check if mock mode is enabled
MOCK_EMAIL_MODE = os.getenv('MOCK_EMAIL_MODE', 'false').lower() == 'true'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INTERVIEW_SLOTS = [
    "Monday, 10:00 AM",
    "Tuesday, 2:00 PM",
    "Wednesday, 11:30 AM",
    "Thursday, 4:00 PM",
    "Friday, 1:00 PM"
]

def generate_email(name, job_title, interview_slot):
    subject = f"Interview Invitation for {job_title}"
    body = f"""
Dear {name},

Congratulations! Based on your profile, you have been shortlisted for the role of <b>{job_title}</b>.

We would like to invite you for an interview on <b>{interview_slot}</b>. The interview will be conducted via Google Meet and will last approximately 45 minutes.

Please confirm your availability by replying to this email.

Best regards,<br>
<b>HR Team</b>
"""
    return subject, body

def send_email(recipient_email, subject, body):
    if not recipient_email:
        raise ValueError("Recipient email address is missing.")
    
    # Mock mode - just log the email instead of sending
    if MOCK_EMAIL_MODE:
        logging.info("🚀 MOCK EMAIL MODE - Email would be sent:")
        logging.info(f"  📧 To: {recipient_email}")
        logging.info(f"  📌 Subject: {subject}")
        logging.info(f"  📝 Body: {body[:100]}...")
        logging.info("✅ Mock email 'sent' successfully!")
        return
    
    msg = MIMEMultipart("alternative")
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Debug logging
    logging.info(f"Attempting to send email to: {recipient_email}")
    logging.info(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    logging.info(f"SMTP User: {SMTP_USER}")
    logging.info(f"SMTP Password configured: {'Yes' if SMTP_PASSWORD else 'No'}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logging.info("Connecting to SMTP server...")
            server.starttls()
            logging.info("Starting TLS...")
            server.login(SMTP_USER, SMTP_PASSWORD)
            logging.info("Login successful, sending message...")
            server.send_message(msg)
            logging.info(f"Email sent successfully to {recipient_email}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication failed: {e}")
        raise RuntimeError(f"Email authentication failed for {recipient_email}. Please check: 1) Gmail 2FA is enabled, 2) App Password is correct, 3) Account settings allow less secure apps. Error: {e}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        raise RuntimeError(f"SMTP error for {recipient_email}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Failed to send email to {recipient_email}: {e}")

def ensure_email_sent_column(cursor):
    cursor.execute("PRAGMA table_info(shortlisted_candidates)")
    if 'email_sent' not in [col[1] for col in cursor.fetchall()]:
        cursor.execute("ALTER TABLE shortlisted_candidates ADD COLUMN email_sent INTEGER DEFAULT 0")

def schedule_interviews():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ensure_email_sent_column(cursor)

    cursor.execute("""
        SELECT sc.id, sc.name, sc.email, j.job_title
        FROM shortlisted_candidates sc
        JOIN jobs j ON sc.job_id = j.id
        WHERE sc.email_sent = 0
    """)
    candidates = cursor.fetchall()

    if not candidates:
        logging.info("All shortlisted candidates have already received interview emails.")
        conn.close()
        return

    for sc_id, name, email, job_title in candidates:
        logging.info(f"Preparing to send email to: {name} ({email}) for role: {job_title}")
        try:
            if not email:
                raise ValueError(f"Missing email for candidate ID {sc_id}")

            slot = random.choice(INTERVIEW_SLOTS)
            subject, body = generate_email(name, job_title, slot)
            send_email(email, subject, body)

            cursor.execute("UPDATE shortlisted_candidates SET email_sent = 1 WHERE id = ?", (sc_id,))
            logging.info(f" Email successfully sent to {email}")

        except Exception as e:
            logging.error(f"Failed to send interview email to {name} ({email}): {e}")

    conn.commit()
    conn.close()
    logging.info("Email job completed and database updated.")

if __name__ == "__main__":
    schedule_interviews()
