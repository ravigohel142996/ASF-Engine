"""
Email service for authentication-related emails
Handles verification emails, password reset, and notifications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import secrets
from datetime import datetime


class EmailService:
    """
    Service for sending authentication-related emails
    """
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('SMTP_USER', 'noreply@asf-engine.com')
        self.app_name = os.getenv('APP_NAME', 'ASF-Engine')
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8501')
        
        # Check if SMTP is configured
        self.is_configured = bool(self.smtp_user and self.smtp_password)
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
        """
        Send an email using SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured:
            print(f"⚠️ SMTP not configured. Email would be sent to: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {text_body or html_body[:100]}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, verification_token: str, user_name: str = "") -> bool:
        """
        Send email verification link
        
        Args:
            email: User's email
            verification_token: Verification token
            user_name: User's name for personalization
            
        Returns:
            True if sent successfully
        """
        verification_url = f"{self.base_url}/verify-email?token={verification_token}"
        
        subject = f"Verify Your {self.app_name} Account"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 {self.app_name}</h1>
                    <p>AI System Failure Monitoring Platform</p>
                </div>
                <div class="content">
                    <h2>Welcome{' ' + user_name if user_name else ''}!</h2>
                    <p>Thank you for signing up for {self.app_name}. To complete your registration, please verify your email address.</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #666;">{verification_url}</p>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    <p>If you didn't create an account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to {self.app_name}!
        
        Thank you for signing up. To complete your registration, please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        ---
        {self.app_name} Team
        """
        
        return self._send_email(email, subject, html_body, text_body)
    
    def send_password_reset_email(self, email: str, reset_token: str, user_name: str = "") -> bool:
        """
        Send password reset link
        
        Args:
            email: User's email
            reset_token: Password reset token
            user_name: User's name for personalization
            
        Returns:
            True if sent successfully
        """
        reset_url = f"{self.base_url}/reset-password?token={reset_token}"
        
        subject = f"Reset Your {self.app_name} Password"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 {self.app_name}</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello{' ' + user_name if user_name else ''}!</h2>
                    <p>We received a request to reset your password for your {self.app_name} account.</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #666;">{reset_url}</p>
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hello{' ' + user_name if user_name else ''}!
        
        We received a request to reset your password for your {self.app_name} account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email and your password will remain unchanged.
        
        ---
        {self.app_name} Team
        """
        
        return self._send_email(email, subject, html_body, text_body)
    
    def send_welcome_email(self, email: str, user_name: str = "") -> bool:
        """
        Send welcome email after successful verification
        
        Args:
            email: User's email
            user_name: User's name
            
        Returns:
            True if sent successfully
        """
        dashboard_url = f"{self.base_url}"
        
        subject = f"Welcome to {self.app_name}!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .features {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to {self.app_name}!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    <p>Your email has been verified and your account is now active.</p>
                    <p style="text-align: center;">
                        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                    </p>
                    <div class="features">
                        <h3>Get Started:</h3>
                        <ul>
                            <li>🤖 Monitor your ML systems in real-time</li>
                            <li>📊 Track performance metrics</li>
                            <li>🔔 Receive intelligent alerts</li>
                            <li>📈 Predict failures 24-72 hours in advance</li>
                        </ul>
                    </div>
                    <p>If you have any questions, don't hesitate to reach out to our support team.</p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to {self.app_name}!
        
        Hello {user_name}!
        
        Your email has been verified and your account is now active.
        
        Visit your dashboard: {dashboard_url}
        
        Get started with:
        - Monitor your ML systems in real-time
        - Track performance metrics
        - Receive intelligent alerts
        - Predict failures 24-72 hours in advance
        
        ---
        {self.app_name} Team
        """
        
        return self._send_email(email, subject, html_body, text_body)


def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)
