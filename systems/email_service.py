"""
Email service for multiplayer mode using SendGrid.
"""

import os
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailService:
    """Handles all email operations for multiplayer mode"""

    def __init__(self):
        api_key = os.environ.get("SENDGRID_API_KEY")
        if not api_key:
            raise EnvironmentError("SENDGRID_API_KEY environment variable is required for multiplayer mode")

        self.client = SendGridAPIClient(api_key)
        self.from_email = os.environ.get("FROM_EMAIL", "noreply@integrationquest.com")

    def send_welcome_email(self, to_email: str, username: str, token: str) -> bool:
        """Send welcome email with login token to new player"""
        subject = "Welcome to Integration Quest! 🎮"
        body = f"""Welcome, {username}!

Your Integration Quest account has been created.

═══════════════════════════════════════════
YOUR LOGIN TOKEN (keep this safe!):
{token}
═══════════════════════════════════════════

Use this token to authenticate when playing:
  login("{to_email}", "{token}")

This token is your password. Keep it safe!
If you ever forget it, use refresh_token("{to_email}") to get a new one.

Now venture forth, Integration Hero, and may your APIs always return 200 OK! ⚡

---
Integration Quest: The Workato RPG
Connect the disconnected. Automate the manual. Defeat the bugs.
"""
        return self._send(to_email, subject, body)

    def send_token_refresh_email(self, to_email: str, username: str, token: str) -> bool:
        """Send new token when player requests refresh"""
        subject = "Integration Quest - New Login Token 🔑"
        body = f"""Hi {username},

Your login token has been refreshed.

═══════════════════════════════════════════
YOUR NEW LOGIN TOKEN:
{token}
═══════════════════════════════════════════

Your old token no longer works.

To login, use:
  login("{to_email}", "{token}")

Happy questing! ⚡

---
Integration Quest: The Workato RPG
"""
        return self._send(to_email, subject, body)

    def _send(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email via SendGrid"""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )

        try:
            response = self.client.send(message)
            return response.status_code in (200, 201, 202)
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
