from django.core.management.base import BaseCommand
from django.utils import timezone
from superadmindashboard.models import TermsAndConditions, PrivacyPolicy
from authentication.models import User


class Command(BaseCommand):
    help = 'Populate dummy data for Terms & Conditions and Privacy Policy'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating dummy data for Terms & Conditions and Privacy Policy...'))
        
        # Get or create a superadmin user for tracking
        superadmin, created = User.objects.get_or_create(
            email='admin@eagleeyeau.com',
            defaults={
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'Admin',
                'is_email_verified': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            superadmin.set_password('admin123')
            superadmin.save()
            self.stdout.write(self.style.SUCCESS(f'Created superadmin user: {superadmin.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superadmin user already exists: {superadmin.email}'))
        
        # Create Terms and Conditions
        terms_content = """
        <h1>Terms and Conditions</h1>
        
        <h2>1. Introduction</h2>
        <p>Welcome to EagleEye AU! These terms and conditions outline the rules and regulations for the use of our time tracking and employee management system.</p>
        
        <h2>2. Acceptance of Terms</h2>
        <p>By accessing this application, we assume you accept these terms and conditions. Do not continue to use EagleEye AU if you do not agree to all of the terms and conditions stated on this page.</p>
        
        <h2>3. User Accounts</h2>
        <p>When you create an account with us, you must provide information that is accurate, complete, and current at all times. Failure to do so constitutes a breach of the Terms.</p>
        <ul>
            <li>You are responsible for safeguarding the password that you use to access the Service</li>
            <li>You must not disclose it to any third party</li>
            <li>You must notify us immediately upon becoming aware of any breach of security or unauthorized use of your account</li>
        </ul>
        
        <h2>4. Time Tracking</h2>
        <p>Our time tracking system is designed to:</p>
        <ul>
            <li>Record accurate work hours for employees</li>
            <li>Generate timesheets and attendance reports</li>
            <li>Facilitate payroll processing</li>
        </ul>
        <p>Employees must clock in and out accurately. Any manipulation of time records is strictly prohibited.</p>
        
        <h2>5. Privacy and Data Protection</h2>
        <p>Your privacy is important to us. We collect and process personal data in accordance with our Privacy Policy. By using EagleEye AU, you consent to such processing and you warrant that all data provided by you is accurate.</p>
        
        <h2>6. User Responsibilities</h2>
        <p>Users agree to:</p>
        <ul>
            <li>Use the system only for lawful purposes</li>
            <li>Not interfere with or disrupt the service</li>
            <li>Not attempt to gain unauthorized access to any part of the system</li>
            <li>Maintain the confidentiality of their login credentials</li>
            <li>Report any security vulnerabilities or bugs discovered</li>
        </ul>
        
        <h2>7. Intellectual Property</h2>
        <p>The Service and its original content, features, and functionality are owned by EagleEye AU and are protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.</p>
        
        <h2>8. Limitation of Liability</h2>
        <p>In no event shall EagleEye AU, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses.</p>
        
        <h2>9. Termination</h2>
        <p>We may terminate or suspend your account immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms.</p>
        
        <h2>10. Changes to Terms</h2>
        <p>We reserve the right to modify or replace these Terms at any time. If a revision is material, we will try to provide at least 30 days' notice prior to any new terms taking effect.</p>
        
        <h2>11. Contact Us</h2>
        <p>If you have any questions about these Terms, please contact us at:</p>
        <ul>
            <li>Email: support@eagleeyeau.com</li>
            <li>Phone: +61 (0) 123 456 789</li>
        </ul>
        
        <p><strong>Last updated: October 27, 2025</strong></p>
        """
        
        terms, created = TermsAndConditions.objects.get_or_create(
            version='1.0',
            defaults={
                'title': 'Terms and Conditions',
                'content': terms_content,
                'effective_date': timezone.now().date(),
                'created_by': superadmin,
                'updated_by': superadmin,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Terms and Conditions v{terms.version}'))
        else:
            self.stdout.write(self.style.WARNING(f'Terms and Conditions v{terms.version} already exists'))
        
        # Create Privacy Policy
        privacy_content = """
        <h1>Privacy Policy</h1>
        
        <h2>1. Introduction</h2>
        <p>EagleEye AU ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our time tracking and employee management application.</p>
        
        <h2>2. Information We Collect</h2>
        
        <h3>2.1 Personal Information</h3>
        <p>We collect information that you provide directly to us, including:</p>
        <ul>
            <li><strong>Account Information:</strong> Name, email address, password, phone number</li>
            <li><strong>Profile Information:</strong> Profile picture, job title, department</li>
            <li><strong>Time Tracking Data:</strong> Clock-in/clock-out times, work hours, attendance records</li>
            <li><strong>Employment Information:</strong> Employee ID, role, hire date</li>
        </ul>
        
        <h3>2.2 Automatically Collected Information</h3>
        <p>When you access our service, we may automatically collect:</p>
        <ul>
            <li>Device information (IP address, browser type, operating system)</li>
            <li>Usage data (features used, pages visited, time spent)</li>
            <li>Location data (if enabled and with your consent)</li>
            <li>Log data and error reports</li>
        </ul>
        
        <h2>3. How We Use Your Information</h2>
        <p>We use the collected information for:</p>
        <ul>
            <li><strong>Service Provision:</strong> To provide and maintain our time tracking services</li>
            <li><strong>Account Management:</strong> To create and manage user accounts</li>
            <li><strong>Payroll Processing:</strong> To calculate work hours and generate payroll reports</li>
            <li><strong>Attendance Tracking:</strong> To monitor and record employee attendance</li>
            <li><strong>Communication:</strong> To send notifications, updates, and administrative messages</li>
            <li><strong>Improvement:</strong> To analyze usage patterns and improve our services</li>
            <li><strong>Security:</strong> To detect, prevent, and address security issues</li>
            <li><strong>Compliance:</strong> To comply with legal obligations and regulations</li>
        </ul>
        
        <h2>4. Data Sharing and Disclosure</h2>
        <p>We do not sell your personal information. We may share your information only in the following circumstances:</p>
        <ul>
            <li><strong>With Your Employer:</strong> Your time tracking data is shared with your employer for payroll and management purposes</li>
            <li><strong>Service Providers:</strong> With third-party vendors who provide services on our behalf (cloud hosting, analytics)</li>
            <li><strong>Legal Requirements:</strong> When required by law or to protect our legal rights</li>
            <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
        </ul>
        
        <h2>5. Data Security</h2>
        <p>We implement appropriate technical and organizational measures to protect your personal information, including:</p>
        <ul>
            <li>Encryption of data in transit and at rest</li>
            <li>Secure authentication mechanisms (JWT tokens, OTP verification)</li>
            <li>Regular security assessments and updates</li>
            <li>Access controls and role-based permissions</li>
            <li>Backup and disaster recovery procedures</li>
        </ul>
        <p>However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.</p>
        
        <h2>6. Data Retention</h2>
        <p>We retain your personal information for as long as:</p>
        <ul>
            <li>Your account is active</li>
            <li>Needed to provide services to you</li>
            <li>Required to comply with legal obligations</li>
            <li>Necessary to resolve disputes and enforce our agreements</li>
        </ul>
        <p>Time tracking records are typically retained for at least 7 years in accordance with employment law requirements.</p>
        
        <h2>7. Your Rights</h2>
        <p>You have the following rights regarding your personal information:</p>
        <ul>
            <li><strong>Access:</strong> Request a copy of your personal data</li>
            <li><strong>Correction:</strong> Update or correct inaccurate information</li>
            <li><strong>Deletion:</strong> Request deletion of your personal data (subject to legal requirements)</li>
            <li><strong>Portability:</strong> Request transfer of your data to another service</li>
            <li><strong>Objection:</strong> Object to certain processing of your data</li>
            <li><strong>Withdraw Consent:</strong> Withdraw consent for data processing (where applicable)</li>
        </ul>
        <p>To exercise these rights, please contact us at privacy@eagleeyeau.com</p>
        
        <h2>8. Cookies and Tracking Technologies</h2>
        <p>We use cookies and similar tracking technologies to:</p>
        <ul>
            <li>Maintain your login session</li>
            <li>Remember your preferences</li>
            <li>Analyze usage patterns</li>
            <li>Improve user experience</li>
        </ul>
        <p>You can control cookies through your browser settings, but disabling them may affect functionality.</p>
        
        <h2>9. Children's Privacy</h2>
        <p>Our service is not intended for individuals under the age of 18. We do not knowingly collect personal information from children. If we become aware that we have collected personal information from a child, we will take steps to delete such information.</p>
        
        <h2>10. International Data Transfers</h2>
        <p>Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.</p>
        
        <h2>11. Changes to This Privacy Policy</h2>
        <p>We may update this Privacy Policy from time to time. We will notify you of any changes by:</p>
        <ul>
            <li>Posting the new Privacy Policy on this page</li>
            <li>Updating the "Last Updated" date</li>
            <li>Sending an email notification (for material changes)</li>
        </ul>
        <p>Your continued use of the service after changes constitutes acceptance of the updated Privacy Policy.</p>
        
        <h2>12. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us:</p>
        <ul>
            <li><strong>Email:</strong> privacy@eagleeyeau.com</li>
            <li><strong>Phone:</strong> +61 (0) 123 456 789</li>
            <li><strong>Address:</strong> 123 Business Street, Sydney, NSW 2000, Australia</li>
        </ul>
        
        <h2>13. Compliance</h2>
        <p>We comply with applicable data protection laws, including:</p>
        <ul>
            <li>Australian Privacy Act 1988</li>
            <li>General Data Protection Regulation (GDPR) - for EU users</li>
            <li>Other applicable privacy and data protection regulations</li>
        </ul>
        
        <p><strong>Last updated: October 27, 2025</strong></p>
        """
        
        privacy, created = PrivacyPolicy.objects.get_or_create(
            version='1.0',
            defaults={
                'title': 'Privacy Policy',
                'content': privacy_content,
                'effective_date': timezone.now().date(),
                'created_by': superadmin,
                'updated_by': superadmin,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Privacy Policy v{privacy.version}'))
        else:
            self.stdout.write(self.style.WARNING(f'Privacy Policy v{privacy.version} already exists'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Dummy data creation completed!'))
        self.stdout.write(self.style.SUCCESS(f'\nSuperadmin credentials:'))
        self.stdout.write(self.style.SUCCESS(f'Email: admin@eagleeyeau.com'))
        self.stdout.write(self.style.SUCCESS(f'Password: admin123'))
