from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    password = forms.CharField(required=True)
    recode = forms.IntegerField(required=True)


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(min_length=8, max_length=16, required=True)
    recode = forms.IntegerField(required=True)


class ForgetPasswordForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=16, required=True)
    email = forms.EmailField(max_length=254, required=True)
    recode = forms.IntegerField(required=True)


class ResetPasswordForm(forms.Form):
    password = forms.CharField(min_length=8, max_length=16, required=True)
    password2 = forms.CharField(min_length=8, max_length=16, required=True)
