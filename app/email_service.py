# ============================================================================
# EMAIL FUNCTIONALITY DISABLED - COMMENTED OUT FOR FUTURE UPDATES
# ============================================================================
# To re-enable email functionality:
# 1. Uncomment all code in this file
# 2. Uncomment email import in app/routers/messages.py
# 3. Uncomment email sending code in app/routers/messages.py
# 4. Set ENABLE_EMAIL=True in .env file
# 5. Configure SMTP settings in .env file
# ============================================================================

# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from pydantic import EmailStr
# from typing import List, Optional
# import logging

# logger = logging.getLogger(__name__)

# # Email configuration will be initialized when needed
# _fm: Optional[FastMail] = None


# def get_email_service():
#     """Get or create the FastMail instance."""
#     global _fm
#     if _fm is None:
#         from app.database import settings
#         conf = ConnectionConfig(
#             MAIL_USERNAME=settings.mail_username,
#             MAIL_PASSWORD=settings.mail_password,
#             MAIL_FROM=settings.mail_from,
#             MAIL_PORT=settings.mail_port,
#             MAIL_SERVER=settings.mail_server,
#             MAIL_FROM_NAME=settings.mail_from_name,
#             MAIL_STARTTLS=settings.mail_starttls,
#             MAIL_SSL_TLS=settings.mail_ssl_tls,
#             USE_CREDENTIALS=True,
#             VALIDATE_CERTS=True
#         )
#         _fm = FastMail(conf)
#     return _fm


# async def send_email(
#     recipient_email: EmailStr,
#     subject: str,
#     body: str,
#     sender_name: Optional[str] = None,
#     sender_email: Optional[EmailStr] = None
# ) -> bool:
#     """
#     Send an email to a recipient.
#     
#     Args:
#         recipient_email: Email address of the recipient
#         subject: Email subject
#         body: Email body content
#         sender_name: Name of the sender (optional)
#         sender_email: Email of the sender (optional, uses default if not provided)
#     
#     Returns:
#         bool: True if email sent successfully, False otherwise
#     """
#     try:
#         from app.database import settings
#         if not settings.enable_email:
#             logger.warning("Email sending is disabled")
#             return False
#         
#         fm = get_email_service()
#         
#         # Format the email body with sender information if provided
#         if sender_name:
#             formatted_body = f"From: {sender_name}"
#             if sender_email:
#                 formatted_body += f" ({sender_email})"
#             formatted_body += f"\n\n{body}"
#         else:
#             formatted_body = body
#         
#         message = MessageSchema(
#             subject=subject or "PrivateRoute Message",
#             recipients=[recipient_email],
#             body=formatted_body,
#             subtype="plain"
#         )
#         
#         await fm.send_message(message)
#         logger.info(f"Email sent successfully to {recipient_email}")
#         return True
#     except Exception as e:
#         logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
#         return False


# async def send_html_email(
#     recipient_email: EmailStr,
#     subject: str,
#     html_body: str,
#     sender_name: Optional[str] = None,
#     sender_email: Optional[EmailStr] = None
# ) -> bool:
#     """
#     Send an HTML email to a recipient.
#     
#     Args:
#         recipient_email: Email address of the recipient
#         subject: Email subject
#         html_body: HTML email body content
#         sender_name: Name of the sender (optional)
#         sender_email: Email of the sender (optional)
#     
#     Returns:
#         bool: True if email sent successfully, False otherwise
#     """
#     try:
#         from app.database import settings
#         if not settings.enable_email:
#             logger.warning("Email sending is disabled")
#             return False
#         
#         fm = get_email_service()
#         
#         # Format the HTML body with sender information if provided
#         if sender_name:
#             sender_info = f"<p><strong>From:</strong> {sender_name}"
#             if sender_email:
#                 sender_info += f" ({sender_email})"
#             sender_info += "</p>"
#             formatted_html = f"{sender_info}<hr/>{html_body}"
#         else:
#             formatted_html = html_body
#         
#         message = MessageSchema(
#             subject=subject or "PrivateRoute Message",
#             recipients=[recipient_email],
#             body=formatted_html,
#             subtype="html"
#         )
#         
#         await fm.send_message(message)
#         logger.info(f"HTML email sent successfully to {recipient_email}")
#         return True
#     except Exception as e:
#         logger.error(f"Failed to send HTML email to {recipient_email}: {str(e)}")
#         return False

