from django.conf import settings
from django.urls import reverse
from django.views import View
from django.shortcuts import render

class PasswordResetConfirmPageView(View):
    def get(self, request, uidb64, token):
        confirm_url = reverse('accounts:password_reset_confirm')
        confirm_full_url = f'{settings.BACKEND_URL}/{confirm_url}'
        context = {
            'uidb64': uidb64,
            'token': token,
            'confirm_full_url': confirm_full_url
        }
        return render(request, 'password_reset_confirm.html', context)
