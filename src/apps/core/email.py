import os
import requests
import base64
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db.models import Q
from allauth.socialaccount.models import SocialToken
from .models import TemporaryIntakeCredential

def send_intake_email(request, credential_id, plain_password):
    credential = TemporaryIntakeCredential.objects.get(id=credential_id)
    token = SocialToken.objects.filter(account__user=request.user, account__provider='microsoft').first()

    if not token:
        raise Exception("No Microsoft token found. Please re-login.")

    # -Encoding the logo image
    logo_path = os.path.join(settings.BASE_DIR, 'src', 'static', 'insightersLogo.jpg')
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Safely strip any trailing slash from the base URL just in case
    safe_base_url = settings.BASE_URL.rstrip('/')

    # Determine dynamic form link
    if credential.form_type == TemporaryIntakeCredential.BUSINESS:
        form_link = f"{safe_base_url}/business/"
        form_type_text = "Business"
    else:
        form_link = f"{safe_base_url}/individual/"
        form_type_text = "Individual"

    context = {
        'name': 'Valued Client',
        'expiration_time': credential.expires_at.strftime("%m/%d/%Y at %I:%M %p"),
        'login_id': credential.login_id,
        'password': plain_password,
        'form_link': form_link,
        'form_type_display': form_type_text
    }
    html_content = render_to_string('email_temp.html', context)

    # 3. Call Microsoft Graph
    endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
    payload = {
        "message": {
            "subject": "Intake Form Access - Insighters Inc",
            "body": {"contentType": "HTML", "content": html_content},
            "toRecipients": [{"emailAddress": {"address": credential.client_email}}],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": "insightersLogo.jpg",
                    "contentType": "image/jpeg",
                    "contentBytes": encoded_logo,
                    "contentId": "insightersLogo",
                    "isInline": True
                }
            ]
        },
        "saveToSentItems": "true"
    }

    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"},
        json=payload
    )
    
    print(f"DEBUG: Graph API Status: {response.status_code}")
    return response.status_code == 202


# Used for sending a confirmation email to the admin user as well as the pdf generated
# from the intake forms
def send_submission_confirmation_email(submission, credential, pdf_path=None):
    # 1. Find the admin user who created the credential
    admin_identifier = credential.created_by_login_id
    # Try to find by email or username
    admin_user = User.objects.filter(Q(email=admin_identifier) | Q(username=admin_identifier)).first()
    
    if not admin_user:
        print(f"Error: Could not find admin user for identifier {admin_identifier}")
        return False

    token = SocialToken.objects.filter(account__user=admin_user, account__provider='microsoft').first()
    
    if not token:
        print(f"Error: No Microsoft token found for admin {admin_identifier}")
        return False

    # 2. Determine client name and type
    if hasattr(submission, 'business_name'):
        client_name = submission.business_name
        form_type = "Business"
    else:
        client_name = submission.client_name
        form_type = "Individual"

    context = {
        'client_name': client_name,
        'form_type': form_type,
        'submission_date': submission.created_at.strftime("%m/%d/%Y at %I:%M %p"),
    }
    html_content = render_to_string('email_confirmation.html', context)

    attachments = []
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        attachments.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": f"{client_name.replace(' ', '_')}_Intake.pdf",
            "contentType": "application/pdf",
            "contentBytes": encoded_pdf
        })

    # 3. Send via Graph API (Send TO the admin user)
    # The application uses the Admin's own Microsoft account credentials 
    # (stored from when they logged in) to send an email from themselves, to themselves.

    endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
    payload = {
        "message": {
            "subject": f"Intake Form Completed: {client_name}",
            "body": {"contentType": "HTML", "content": html_content},
            "toRecipients": [{"emailAddress": {"address": admin_user.email}}],
            "attachments": attachments
        },
        "saveToSentItems": "true"
    }

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 202:
            print(f"Success: Confirmation email sent to {admin_user.email}")
        else:
            print(f"Failed to send email. Graph API Status: {response.status_code} - {response.text}")
            
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False
