from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.user_logout, name='logout'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("forget_password/", views.ForgetPasswordView.as_view(), name="forget_password"),
    path("reset_password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("reset_password_code/<slug:reset_password_code>/", views.ResetPasswordCodeView.as_view(), name="reset_password_code"),
    path("activation/<slug:active_code>/", views.ActivationView.as_view(), name="activation"),
    path("flush_recode_image/", views.FlushRecodeImage.as_view(), name="flush_recode_image"),
    path("reactive/", views.Reactive.as_view(), name="reactive")
]
