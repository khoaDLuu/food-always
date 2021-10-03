import random

from django.core.mail import send_mail
from django_food.settings import EMAIL_FROM

from user.models import EmailVerifyCode


def send_email_verify_record(email, send_type='register', username=''):

    email_verify_record = EmailVerifyCode()
    code = random_code()
    email_verify_record.code = code
    email_verify_record.email = email
    email_verify_record.send_type = send_type
    email_verify_record.verify_times = 3
    email_verify_record.save()

    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = 'Foodalways - Registration and Activation'
        email_body = (
            'Thank you for signing up for Foodalways!\n\n'
            'Please click on the link to activate your account:\n'
            '{0}/user/activation/{1}'.format('http://127.0.0.1:8000', code)
        )
    elif send_type == 'forget':
        email_title = 'Foodalways - Password Reset'
        email_body = (
            'Please click the link to reset your password:\n'
            '{0}/user/reset_password_code/{1}'.format('http://127.0.0.1:8000', code)
        )
    elif send_type == 'reset_email':
        email_title = 'Foodalways - Email Reset'
        email_body = (
            'Please fill in the verification code '
            'to change the email: {0}'.format(code)
        )

    # Use try/catch block to avoid network fluctuations or errors
    # caused by mail backend configuration errors
    try:
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    except Exception as e:
        return False
    else:
        return send_status


def random_code(length=8):

    code_str = 'ABCDEFGHIJKLMNOPQRETUVWXYZabcedfghijklmnopqrstuvwxyz0123456789'
    code = "".join(random.sample(code_str, length))
    return code
