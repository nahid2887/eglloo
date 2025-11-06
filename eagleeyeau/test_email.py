"""
Test script to verify email sending functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eagleeyeau.settings')
django.setup()

from authentication.utils import send_otp_email
from authentication.models import OTP

def test_email():
    print("Testing email configuration...")
    print("-" * 50)
    
    # Test email
    test_email_address = "nahid2887@gmail.com"
    test_otp = "1234"
    
    print(f"Sending test OTP to: {test_email_address}")
    print(f"Test OTP: {test_otp}")
    
    result = send_otp_email(test_email_address, test_otp, 'password_reset')
    
    if result:
        print("✅ Email sent successfully!")
        print("Please check your inbox.")
    else:
        print("❌ Failed to send email.")
        print("Please check your email configuration in .env file")
    
    print("-" * 50)

if __name__ == "__main__":
    test_email()
