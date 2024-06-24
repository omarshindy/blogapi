from django.urls import path
from django.contrib.auth import views as auth_views

from rest_framework_simplejwt.views import *

from . import api, views

app_name = 'accounts'


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', api.CustomLogoutView.as_view(), name='logout'),
    path('profile/' , api.ProfileAPIView.as_view(), name='profile'),
    path('signup/' , api.RegesterationView.as_view(), name='register'),
    path('password_reset/', api.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/', api.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_confirm/<uidb64>/<token>/', views.PasswordResetConfirmPageView.as_view(), name='password_confirm_page'),
]
