from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user, uidb64, token):
    subject = 'Password Reset Request'
    reset_url = reverse('accounts:password_confirm_page', kwargs={'uidb64': uidb64, 'token': token})
    full_reset_url = f'{settings.BACKEND_URL}{reset_url}'
    
    html_message = render_to_string('password_reset_email.html', {
        'user': user,
        'reset_url': full_reset_url,
    })
    plain_message = strip_tags(html_message)
    from_email = 'from@example.com'
    to = user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
