import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from fastapi import HTTPException

class EmailService:
    """
    Service for handling email verification and notifications
    """
    def __init__(
        self, 
        smtp_host: str = 'smtp.gmail.com', 
        smtp_port: int = 587
    ):
        """
        Initialize email service with SMTP configuration
        
        Args:
            smtp_host (str, optional): SMTP server host. Defaults to Gmail.
            smtp_port (int, optional): SMTP server port. Defaults to 587.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = os.getenv('EMAIL_USER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')

    def send_verification_email(
        self, 
        recipient_email: str, 
        verification_token: str
    ) -> bool:
        """
        Send email verification link to user
        
        Args:
            recipient_email (str): Recipient's email address
            verification_token (str): Unique verification token
        
        Returns:
            bool: True if email sent successfully
        
        Raises:
            HTTPException: If email sending fails
        """
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = 'Email Verification'

            # Verification link (replace with your actual frontend URL)
            verification_link =f"http://127.0.0.1:8002/auth/verify-email?token={verification_token}"

            # Email body
            body = f"""
            Hello,

            Please verify your email by clicking the link below:
            {verification_link}

            This link will expire in 30 minutes.

            Best regards,
            Your File Sharing System
            """

            message.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            return True

        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send verification email: {str(e)}"
            )

# Create a singleton instance
email_service = EmailService()