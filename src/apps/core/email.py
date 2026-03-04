from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import TemporaryIntakeCredential 

def display_login_email(user_id):
    credential = TemporaryIntakeCredential.objects.get(id=user_id)

    formatted_time = credential.expires_at.strftime("%m/%d/%Y at %I:%M %p")

