import os
import requests
import base64
from django.conf import settings
from django.template.loader import render_to_string
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

    # Determine dynamic form link
    if credential.form_type == TemporaryIntakeCredential.BUSINESS:
        form_link = "http://localhost:8000/business/"
        form_type_text = "Business"
    else:
        form_link = "http://localhost:8000/individual/"
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
