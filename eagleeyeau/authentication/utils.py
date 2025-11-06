from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email, otp, purpose):
    """
    Send OTP email to user
    """
    if purpose == 'email_verification':
        subject = 'Verify Your Email - Lignaflow'
        message = f'''
        Hello,
        
        Thank you for registering with Lignaflow!
        
        Your OTP for email verification is: {otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Lignaflow Team
        '''
    elif purpose == 'password_reset':
        subject = 'Reset Your Password - Lignaflow'
        message = f'''
        Hello,
        
        You have requested to reset your password.
        
        Your OTP for password reset is: {otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Lignaflow Team
        '''
    else:
        return False
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_invitation_email(email, role, token, company_name, base_url):
    """
    Send invitation email to user
    """
    # Frontend registration link
    invitation_link = "http://localhost:5173/register-via-link"
    
    subject = 'You are invited to join Lignaflow'
    message = f'''
Hello,

You have been invited to join Lignaflow.

Your Email: {email}

Your Role: {role}

Company Name: {company_name}

Your Token: {token}

Registration URL: {invitation_link}

Please use the token above to complete your registration at the provided URL.

Note: Your email, role, and company name are pre-assigned and cannot be changed.

This invitation will expire in 7 days.

Best regards,
Lignaflow Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending invitation email: {e}")
        return False
        print(f"Error sending email: {e}")
        return False
