import os
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import TemporaryIntakeCredential 

def display_login_email(user_id):
    credential = TemporaryIntakeCredential.objects.get(id=user_id)

    formatted_time = credential.expires_at.strftime("%m/%d/%Y at %I:%M %p")

# Used for testing the view of the email templete
def generate_preview_file():
    """
    Generates a static HTML file in src/static/email_preview.html 
    populated with dummy data so you can view the design in a browser.
    """
    context = {
        'name': 'Valued Client',
        'expiration_time': timezone.now().strftime("%m/%d/%Y at %I:%M %p"),
        'login_id': 'INT-PREVIEW-123',
        'password': 'sample-password-123'
    }
    
    html_content = render_to_string('email_temp.html', context)
    
    output_path = os.path.join(settings.BASE_DIR, 'src', 'static', 'email_preview.html')
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return f"Preview generated at: {output_path}"
