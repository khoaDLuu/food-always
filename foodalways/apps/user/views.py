#!/usr/bin/env python3

import random
import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
# Import the django user authentication module
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
# To import the django database query object
from django.db.models import Q
from django.views.generic.base import View
# Import django message module, which can be used in the background
# to send some messages to the frontend
from django.contrib import messages

from .models import UserProfiles, EmailVerifyCode, RecodeImage
from .forms import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from assist_function.email.email import send_email_verify_record
from food.models import FoodArticle, FoodImage
from operation.models import UserMessage


# Generate two random numbers, and obtain the captcha image
def create_numbers(request):
    a, b = random.randint(1, 9), random.randint(1, 9)
    recode_image = RecodeImage.objects.get(recode_number_a=a, recode_number_b=b)
    request.session["number_a"] = a
    request.session["number_b"] = b
    return recode_image


class CustomBackend(ModelBackend):
    """
    Customize the login authentication method, login with username/email
    Implementation logic:
        - Enter the data entered by the user into the background for query
        - If the query is successful, the authentication is successful
        - If an exception or failure occurs, the authentication fails
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfiles.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    """User login view class"""

    def get(self, request):

        request.session['login_reference_page'] = request.META.get("HTTP_REFERER", '/')
        recode_image = create_numbers(request)
        return render(request, "user/login.html", {"recode_image": recode_image})

    def post(self, request):

        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            recode = int(request.POST.get("recode", 0))

            if recode != request.session["number_a"] + request.session["number_b"]:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                # There is a big problem here, the problem of jsonification of specific model instances
                # The solution is to customize a function in the model - put the model field and value into a dictionary
                # In this process, another problem occurs, that is,
                # the value of the ImageField field needs to be stringified by calling the str() function
                # See the definition in the RecodeImage model class for details
                return JsonResponse(message, safe=False)

            verify_user_name = UserProfiles.objects.filter(Q(username=username) | Q(email=username))
            if not verify_user_name:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            user = authenticate(username=username, password=password)  # If the authentication fails, user = None
            if not user:  # User name and password do not match
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "password", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            if not user.is_active:
                send_email_verify_record(user.email)
                return JsonResponse({
                    "status": "fail",
                    "fail_type": "not_active",
                    "message": (
                        "The user is not activated, the activation has been re-sent to the registered email, "
                        "please go to your mailbox to activate..."
                    )
                })
            else:
                login(request, user)
                refer_page = request.session.get("login_reference_page", '/')
                if refer_page in (reverse("user:login"), reverse("user:reset_password")):
                    return JsonResponse({"status": "success", "url": reverse("home_page")})
                else:
                    return JsonResponse({"status": "success", "url": request.session["login_reference_page"]})

        # Form validation fails
        recode_image = create_numbers(request).to_json()
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))


class RegisterView(View):
    """User registration view class"""

    def get(self, request):

        recode_image = create_numbers(request)
        return render(request, "user/register.html", {"recode_image": recode_image})

    def post(self, request):

        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            recode = int(request.POST.get("recode"))

            if recode != request.session["number_a"] + request.session["number_b"]:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            verify_username = UserProfiles.objects.filter(username=username)
            if verify_username:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            verify_email = UserProfiles.objects.filter(email=email)
            if verify_email:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            send_status = send_email_verify_record(email)
            if send_status:
                new_user = UserProfiles()
                new_user.username = username
                new_user.email = email
                new_user.is_active = False
                new_user.password = make_password(password)
                new_user.save()

                user_message = UserMessage()
                user_message.user = new_user
                user_message.message_title = 'Welcome to <foodalways.com>\n'
                user_message.message_content = f"""
                    Hi, {username} ! I'm glad you can register for <foodalways.com>.\n\n
                    This is a website about food. The website provides many food making tutorials and food pictures.
                    I hope you can find your favorite food and pictures!\n\n
                    \t\t\t\t\t\t\t\tA food lover: Keith\n
                    \t\t\t\t\t\t\t\t{timezone.now().strftime('%Y-%m-%d %H:%M')}\n
                """
                user_message.save()

                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "fail", "fail_type": "send_email"})

        recode_image = create_numbers(request).to_json()
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ActivationView(View):
    """User activation view class"""

    def get(self, request, active_code):
        email_verify_record = EmailVerifyCode.objects.filter(code=active_code)
        if email_verify_record:
            recode = email_verify_record[0]

            if (timezone.now() - recode.send_time).total_seconds() < 600:  # authentication code's valid time = 600s
                user = UserProfiles.objects.get(email=recode.email)
                user.is_active = True
                user.save()
                recode.delete()  # After activation, delete the verification code
                messages.add_message(
                    request,
                    messages.INFO,
                    "User has been activated, please log in again"
                )
                return redirect("user:login")
            else:
                send_email_verify_record(recode.email)
                recode.delete()  # The verification code is timed out, delete it, and resend the verification code
                messages.add_message(
                    request,
                    messages.INFO,
                    "The connection is invalid, the verification email has been re-sent, "
                    "please go to the mailbox to reactivate"
                )
                return redirect("user:login")

        # Verification failed, return to the homepage
        messages.add_message(
            request,
            messages.INFO,
            "Invalid activation verification, the page has been reset, "
            "please enter the email information to obtain the activation link again"
        )
        return redirect("user:login")


class Reactive(View):
    """New user activation failed, re-acquire the view class of the activation link"""

    def get(self, request):
        recode_image = create_numbers(request)
        return render(request, "user/reactive.html", {"recode_image": recode_image})

    def post(self, request):
        reactive_form = ForgetPasswordForm(request.POST)
        if reactive_form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            recode = int(request.POST.get("recode"))

            if recode != request.session["number_a"] + request.session["number_b"]:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            verify_user = UserProfiles.objects.filter(username=username)
            if not verify_user:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)
            else:
                user = verify_user[0]
                if user.username != username or user.email != email:
                    recode_image = create_numbers(request).to_json()
                    message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                    return JsonResponse(message, safe=False)
                else:
                    send_email_verify_record(email, "register")
                    return JsonResponse({"status": "success"})

        recode_image = create_numbers(request)
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ForgetPasswordView(View):
    """Forgot Password View Class"""

    def get(self, request):
        recode_image = create_numbers(request)
        return render(request, "user/forget_password.html", {"recode_image": recode_image})

    def post(self, request):
        forget_password_form = ForgetPasswordForm(request.POST)
        if forget_password_form.is_valid():
            username = request.POST.get("username")
            email = request.POST.get("email")
            recode = int(request.POST.get("recode"))

            if recode != request.session["number_a"] + request.session["number_b"]:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "recode", "recode_image": recode_image}
                return JsonResponse(message, safe=False)

            verify_user = UserProfiles.objects.filter(username=username)
            if not verify_user:
                recode_image = create_numbers(request).to_json()
                message = {"status": "fail", "fail_type": "username", "recode_image": recode_image}
                return JsonResponse(message, safe=False)
            else:
                user = verify_user[0]
                if user.username != username or user.email != email:
                    recode_image = create_numbers(request).to_json()
                    message = {"status": "fail", "fail_type": "email", "recode_image": recode_image}
                    return JsonResponse(message, safe=False)
                else:
                    send_email_verify_record(email, "forget")
                    return JsonResponse({"status": "success"})

        recode_image = create_numbers(request)
        message = {"status": "fail", "fail_type": "form", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


class ResetPasswordCodeView(View):
    """The view of the email link sent to the user resetting the password"""

    def get(self, request, reset_password_code):
        verify_code = EmailVerifyCode.objects.filter(code=reset_password_code)
        if verify_code:
            reset_code = verify_code[0]
            email = reset_code.email
            request.session["email"] = email
            request.session["reset_password_code"] = reset_password_code
            return redirect("user:reset_password")
        messages.add_message(
            request,
            messages.INFO,
            "The connection is invalid, the page has been reset, please re-acquire"
        )
        return redirect("user:forget_password")


class ResetPasswordView(View):
    """Reset Password View Class"""

    def get(self, request):
        return render(request, 'user/reset_password.html')

    def post(self, request):
        reset_password_form = ResetPasswordForm(request.POST)
        if reset_password_form.is_valid():
            password = request.POST.get("password")
            password2 = request.POST.get("password2")

            # Obtain email and reset_password_code information from the session,
            # if it cannot be obtained, that means it is invalid
            try:
                email = request.session["email"]
                code = request.session["reset_password_code"]
            except:
                return JsonResponse({"status": "fail", "fail_type": "email"})

            # Verify that the two passwords are the same
            if password != password2:
                return JsonResponse({"status": "fail", "fail_type": "not_equal"})

            # Password consistency verification succeeded
            user = UserProfiles.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            # Password hashing completed, delete the verification code from the database
            verify_cord = EmailVerifyCode.objects.get(code=code)
            verify_cord.delete()
            del request.session["email"]
            del request.session["reset_password_code"]
            # return redirect("user:login") # Redirect to the login page
            # There is a problem here, the ajax request will not perform the redirect operation
            # Need to perform operations in ajax
            return JsonResponse({"status": "success"})

        # Failed
        return JsonResponse({"status": "fail", "fail_type": "form"})


class HomePageView(View):
    """Home View"""

    def get(self, request):

        # Randomly get 6 pictures from the database
        random_image = FoodImage.objects.order_by("?")[:6]

        # Randomly extract 6 records from the database
        random_food = FoodArticle.objects.order_by("?")[:6]

        # Get top 3 most popular foods
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        return render(request, "home_page.html", {
            "random_food": random_food,
            "popular_food": popular_food,
            "random_image": random_image,
            "focus": "home",  # selected state flag
        })


class FlushRecodeImage(View):
    """Refresh image verification code"""

    def post(self, request):
        recode_image = create_numbers(request).to_json()
        message = {"status": "success", "recode_image": recode_image}
        return JsonResponse(message, safe=False)


def about(request):
    return render(request, 'about.html', {'focus': 'about'})
