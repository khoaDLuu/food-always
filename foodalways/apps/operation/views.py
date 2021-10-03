import json
import time

from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from pure_pagination import Paginator, PageNotAnInteger

from assist_function.email.email import send_email_verify_record
from . import forms
from user.models import EmailVerifyCode, UserProfiles
from food.models import FoodImage, FoodArticle, FoodSteps, Tags
from .models import UserFav, UserLike, MessageBoard
from assist_function.authenticate.login_required import LoginRequiredMixin


@login_required
def user_center(request):
    return render(request, 'operation/user_center.html')


class ChangeHeaderPortraitView(LoginRequiredMixin, View):

    def post(self, request):
        head_portrait_form = forms.ChangeUserHeaderPortraitForm(
            request.POST, request.FILES, instance=request.user
        )
        if head_portrait_form.is_valid():
            request.user.save()
            image = request.user.head_portrait.url
            return JsonResponse({'status': 'success', 'image': image})
        else:
            return JsonResponse({'status': 'fail'})


class ChangeUserInfoView(LoginRequiredMixin, View):

    def post(self, request):
        user_info_form = forms.ChangeUserInfoForm(
            request.POST, instance=request.user
        )
        if user_info_form.is_valid():
            request.user.save()
            return JsonResponse({"status": "success"})
        else:
            error_dict = user_info_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            return JsonResponse({"status": "fail", "message": error_dict})


@login_required
def generate_captcha():
    captcha_dict = dict()
    captcha_dict['captcha_key'] = CaptchaStore.generate_key()
    captcha_dict['captcha_image'] = captcha_image_url(captcha_dict['captcha_key'])
    return captcha_dict


@login_required
def refresh_captcha(request):
    if request.is_ajax():
        to_json_response = dict()
        to_json_response['status'] = 'success'
        to_json_response.update(generate_captcha())
        return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class ChangePasswordView(LoginRequiredMixin, View):

    def post(self, request):
        change_password_form = forms.ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')
            if password == password2:
                user = request.user
                user.password = make_password(password)
                user.save()
                return JsonResponse({"status": 'success', 'url': reverse('user:login')})
            else:
                to_json_response = dict()
                to_json_response['status'] = 'fail'
                to_json_response['error'] = {'password2': 'Two passwords are inconsistent'}
                to_json_response.update(generate_captcha())
                return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        else:
            to_json_response = dict()
            to_json_response['status'] = 'fail'
            to_json_response.update(generate_captcha())

            error_dict = change_password_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            to_json_response['error'] = error_dict

            return HttpResponse(json.dumps(to_json_response), content_type='application/json')


@login_required
def get_change_email_code(request):

    if request.is_ajax():
        email_form = forms.ChangeEmailForm(request.POST)
        if email_form.is_valid():
            email = request.POST.get('email')
            user = UserProfiles.objects.filter(email=email)
            if not user:
                send_status = send_email_verify_record(email, send_type="reset_email")
                if send_status:
                    return JsonResponse({"status": 'success'})
                else:
                    return JsonResponse({"status": 'fail', 'message': 'send'})
            else:
                return JsonResponse({"status": 'fail', 'message': 'exist'})
        else:
            return JsonResponse({"status": 'fail', 'message': 'invalid'})


class ChangeEmailView(LoginRequiredMixin, View):

    def post(self, request):
        email = request.POST.get('email')
        email_code = request.POST.get('email_code')
        email_verify_query = EmailVerifyCode.objects.filter(email=email, code=email_code)
        if email_verify_query:
            email_verify = email_verify_query[0]
            if email_verify.verify_times > 0 and \
                    email_verify.send_time.timestamp() - time.time() < 600:
                user = request.user
                user.email = email
                user.save()
                email_verify.delete()
                return JsonResponse({'status': 'success', 'email': email})
            else:
                return JsonResponse({
                    'status': 'fail',
                    'message': 'The verification code has expired, please obtain it again'
                })
        else:
            return JsonResponse({
                'status': 'fail',
                'message': 'Invalid verification code or verification code has expired, please check again'
            })


class UserLikeView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        user_like_article = user.userlike_set.filter(like_type='food_article')
        user_like_image = user.userlike_set.filter(like_type='food_image')

        old_article_page = request.session.get('user_like_article_page', 1)
        old_image_page = request.session.get('user_like_image_page', 1)

        focus = 'food_article'
        if user_like_article:
            # Get article information from matched data
            food_articles = FoodArticle.objects.filter(
                article_id__in=[like.like_id for like in user_like_article]
            )

            # Get the paging value returned by the page, the default is 1 (first page)
            try:
                article_page = request.GET.get('article_page', 1)
                request.session['user_like_article_page'] = article_page
            except PageNotAnInteger:
                article_page = 1

            # Paging all objects taken out of the database,
            # the middle parameter is the number of objects displayed on each page, set to 6
            # The pagination plug-in is rewritten here, the default next page query is page,
            # there are two paginations in this view, so it needs to be distinguished
            # A default parameter type is added to Paginator,
            # which can be modified by passing parameters when needed
            # Modify the function _other_page_querystring in the Page class
            # to use the type parameter value instead of the hard-coded 'page' string
            paginator = Paginator(food_articles, 6, request=request, page_type='article_page')
            # Get the data of the corresponding page
            user_like_article_page = paginator.page(article_page)

            if old_article_page != article_page:
                focus = 'food_article'
        else:
            user_like_article_page = []
            focus = 'food_image'
            article_page = 1

        if user_like_image:
            food_images = FoodImage.objects.filter(
                name__in=[like.like_id for like in user_like_image]
            )

            try:
                image_page = request.GET.get('image_page', 1)
                request.session['user_like_image_page'] = image_page
            except PageNotAnInteger:
                image_page = 1
            paginator = Paginator(food_images, 6, request=request, page_type='image_page')
            user_like_image_page = paginator.page(image_page)
            if old_image_page != image_page:
                focus = 'food_image'
        else:
            user_like_image_page = []
            focus = 'food_article'
            image_page = 1

        # After refreshing the page
        if image_page == article_page == 1:
            focus = 'food_article'

        # After canceling the like in the user center, keep the canceled focus state
        # For example: if the article is canceled,
        # the focus will be on the article you like after refreshing the page
        del_type = request.session.get('delete_like_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_like_type']

        return render(request, 'operation/user_like.html', {
            'user_like_article_page': user_like_article_page,
            'user_like_image_page': user_like_image_page,
            'focus': focus,
        })


class UserFavView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        user_fav_article = user.userfav_set.filter(fav_type='food_article')
        user_fav_image = user.userfav_set.filter(fav_type='food_image')

        old_article_page = request.session.get('user_fav_article_page', 1)
        old_image_page = request.session.get('user_fav_image_page', 1)

        focus = 'food_article'
        if user_fav_article:
            food_articles = FoodArticle.objects.filter(
                article_id__in=[fav.fav_id for fav in user_fav_article]
            )

            try:
                article_page = request.GET.get('article_page', 1)
                request.session['user_fav_article_page'] = article_page
            except PageNotAnInteger:
                article_page = 1
            paginator = Paginator(food_articles, 6, request=request, page_type='article_page')
            user_fav_article_page = paginator.page(article_page)

            if old_article_page != article_page:
                focus = 'food_article'
        else:
            user_fav_article_page = []
            focus = 'food_image'
            article_page = 1

        if user_fav_image:
            food_images = FoodImage.objects.filter(
                name__in=[fav.fav_id for fav in user_fav_image]
            )

            try:
                image_page = request.GET.get('image_page', 1)
                request.session['user_fav_image_page'] = image_page
            except PageNotAnInteger:
                image_page = 1
            paginator = Paginator(food_images, 6, request=request, page_type='image_page')
            user_fav_image_page = paginator.page(image_page)
            if old_image_page != image_page:
                focus = 'food_image'
        else:
            user_fav_image_page = []
            focus = 'food_article'
            image_page = 1

        if image_page == article_page == 1:
            focus = 'food_article'

        del_type = request.session.get('delete_fav_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_fav_type']

        return render(request, 'operation/user_fav.html', {
            'user_fav_article_page': user_fav_article_page,
            'user_fav_image_page': user_fav_image_page,
            'focus': focus,
        })


class UserMessageView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        unread_message = user.usermessage_set.filter(readable="unread")
        read_message = user.usermessage_set.filter(readable="read")
        old_unread_page = request.session.get('user_unread_page', 1)
        old_read_page = request.session.get('user_read_page', 1)

        focus = 'unread'
        if unread_message:

            try:
                unread_page = request.GET.get('unread_page', 1)
                request.session['user_unread_page'] = unread_page
            except PageNotAnInteger:
                unread_page = 1
            paginator = Paginator(unread_message, 6, request=request, page_type='unread_page')
            user_unread_page = paginator.page(unread_page)

            if old_unread_page != unread_page:
                focus = 'unread'
        else:
            user_unread_page = []
            focus = 'unread'
            unread_page = 1

        if read_message:

            try:
                read_page = request.GET.get('read_page', 1)
                request.session['user_read_page'] = read_page
            except PageNotAnInteger:
                read_page = 1
            paginator = Paginator(read_message, 6, request=request, page_type='read_page')
            user_read_page = paginator.page(read_page)
            if old_read_page != read_page:
                focus = 'read'
        else:
            user_read_page = []
            focus = 'read'
            read_page = 1

        if read_page == unread_page == 1:
            focus = 'unread'

        del_type = request.session.get('delete_read_type', '')
        if del_type:
            focus = del_type
            del request.session['delete_read_type']

        return render(request, 'operation/user_message.html', {
            'user_unread_page': user_unread_page,
            'user_read_page': user_read_page,
            'focus': focus,
        })


class AddLikeView(View):
    """User like add/cancel view class - ajax"""

    def post(self, request):
        if request.user.is_authenticated:
            like_status = request.POST.get("status", '')
            like_id = request.POST.get("id", '')
            like_type = request.POST.get('type')
            user = request.user
            if like_status == 'no':
                like = UserLike()
                like.user = user
                like.like_id = like_id
                like.like_type = like_type
                try:
                    if 'food_article' == like_type:
                        food = FoodArticle.objects.get(article_id=like_id)
                        food.like += 1
                        food.save()
                    elif 'food_image' == like_type:
                        image = FoodImage.objects.get(name=like_id)
                        image.like += 1
                        image.save()
                    like.save()
                    return JsonResponse({'status': 'success', 'like_status': 'yes'})
                except:
                    # If there is a situation where the id cannot be matched,
                    # a failure prompt will be shown
                    return JsonResponse({
                        'status': 'fail',
                        'message': 'The operation failed, please try again later!'
                    })
            elif like_status == 'yes':
                like = user.userlike_set.filter(like_id=like_id)
                if like:
                    like = like[0]
                    like.delete()
                    if 'food_article' == like_type:
                        food = FoodArticle.objects.get(article_id=like_id)
                        food.like -= 1
                        food.save()
                    elif 'food_image' == like_type:
                        image = FoodImage.objects.get(name=like_id)
                        image.like -= 1
                        image.save()
                    return JsonResponse({'status': 'success', 'like_status': 'no'})
                else:
                    return JsonResponse({'status': 'fail', 'message': 'The operation failed, please try again later!'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'User is not logged in, please go to Login'})


class AddFavView(View):

    def post(self, request):
        if request.user.is_authenticated:
            fav_status = request.POST.get("status", '')
            fav_id = request.POST.get("id", '')
            fav_type = request.POST.get('type')
            user = request.user
            if fav_status == 'no':
                fav = UserFav()
                fav.user = user
                fav.fav_id = fav_id
                fav.fav_type = fav_type
                try:
                    if 'food_article' == fav_type:
                        food = FoodArticle.objects.get(article_id=fav_id)
                        food.like += 1
                        food.save()
                    elif 'food_image' == fav_type:
                        image = FoodImage.objects.get(name=fav_id)
                        image.like += 1
                        image.save()
                    fav.save()
                    return JsonResponse({'status': 'success', 'fav_status': 'yes'})
                except:
                    return JsonResponse({
                        'status': 'fail',
                        'message': 'The operation failed, please try again later!'
                    })
            elif fav_status == 'yes':
                fav = user.userfav_set.filter(fav_id=fav_id)
                if fav:
                    fav = fav[0]
                    fav.delete()
                    if 'food_article' == fav_type:
                        food = FoodArticle.objects.get(article_id=fav_id)
                        food.like -= 1
                        food.save()
                    elif 'food_image' == fav_type:
                        image = FoodImage.objects.get(name=fav_id)
                        image.like -= 1
                        image.save()
                    return JsonResponse({'status': 'success', 'fav_status': 'no'})
                else:
                    return JsonResponse({
                        'status': 'fail',
                        'message': 'The operation failed, please try again later!'
                    })
        else:
            return JsonResponse({
                'status': 'fail',
                'message': 'User is not logged in, please go to Login'
            })


class DelLikeView(LoginRequiredMixin, View):

    def get(self, request, like_id):
        user = request.user
        unlike = user.userlike_set.get(like_id=like_id)
        request.session['delete_like_type'] = unlike.like_type
        unlike.delete()
        if 'food_article' == unlike.fav_type:
            food = FoodArticle.objects.get(article_id=like_id)
            food.fav -= 1
            food.save()
        elif 'food_image' == unlike.fav_type:
            image = FoodImage.objects.get(name=like_id)
            image.fav -= 1
            image.save()
        return redirect(reverse('operator:user_like'))


class DelFavView(LoginRequiredMixin, View):

    def get(self, request, fav_id):
        user = request.user
        unfav = user.userfav_set.get(fav_id=fav_id)
        request.session['delete_fav_type'] = unfav.fav_type
        unfav.delete()
        if 'food_article' == unfav.fav_type:
            food = FoodArticle.objects.get(article_id=fav_id)
            food.fav -= 1
            food.save()
        elif 'food_image' == unfav.fav_type:
            image = FoodImage.objects.get(name=fav_id)
            image.fav -= 1
            image.save()
        return redirect(reverse('operator:user_fav'))


class DelMessageView(LoginRequiredMixin, View):

    def get(self, request, message_id):
        user = request.user
        del_message = user.usermessage_set.get(id=message_id)
        request.session['delete_read_type'] = del_message.readable
        del_message.delete()
        return redirect(reverse('operator:user_message'))


class ReadMessageView(LoginRequiredMixin, View):

    def post(self, request, message_id):
        user = request.user
        id = request.POST.get('id', '')
        read_message = user.usermessage_set.get(id=message_id)
        read_message.readable = 'read'
        read_message.save()
        return JsonResponse({"status": "success"})


class MessageBoardView(View):

    def get(self, request):
        message_board = MessageBoard.objects.order_by('-add_time')

        for message in message_board:
            name, addr = message.email.split('@')
            if len(name) > 5:
                name = name[0:3] + '*'*len(name[3:])
            else:
                addr = '*'*len(addr)
            message.email = name + '@' + addr

        old_message_page = request.session.get('message_board_page', 1)
        try:
            message_page = request.GET.get('message_page', 1)
            request.session['message_board_page'] = message_page
        except PageNotAnInteger:
            message_page = 1
        paginator = Paginator(message_board, 10, request=request, page_type='message_page')
        message_board_page = paginator.page(message_page)
        if old_message_page != message_page:
            message_focus = 'read'
        else:
            message_focus = 'add'
        return render(request, 'message.html', {
            'message': message_board_page,
            "focus": "message",
            "message_focus": message_focus
        })


class AddMessageView(View):

    def post(self, request):
        message_board_form = forms.MessageBoardForm(request.POST)
        if message_board_form.is_valid():
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            message_board = MessageBoard()
            if request.user.is_authenticated:
                is_user = 'yes'
            else:
                is_user = 'no'
            message_board.name = name
            message_board.email = email
            message_board.message = message
            message_board.is_user = is_user
            message_board.save()
            return JsonResponse({"status": "success"})
        else:
            error_dict = message_board_form.errors
            error_str = json.dumps(error_dict)
            error_dict = json.loads(error_str)
            return JsonResponse({"status": "fail", 'message': error_dict})


class GetUserMessageView(View):

    def get(self, request):
        user = request.user
        message_count = user.usermessage_set.filter(readable='unread').count()
        return JsonResponse({"status": "success", "counter": message_count})


class UploadFoodArticle(View):

    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.is_author == 'yes' and user.is_staff == True:
                url = reverse("xadmin:food_foodarticle_add")
                return JsonResponse({'status': 'success', "url": url})
            else:
                user.is_author = 'yes'
                user.is_staff = True
                user.save()
                authority = Group.objects.filter(name='Food Author').first()  # XXX
                user.groups.add(authority)
                url = reverse("xadmin:food_foodarticle_add")
                return JsonResponse({'status':'success', "url": url})
        else:
            return JsonResponse({
                'status':'fail',
                "message": "User not logged in, can't perform this action"
            })


def handler_400_error(request, exception, template_name='400_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('400_error_page.html')
    response.status_code = 400
    return response


def handler_403_error(request, exception, template_name='403_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('403_error_page.html')
    response.status_code = 403
    return response


def handler_404_error(request, exception, template_name='404_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('404_error_page.html')
    response.status_code = 404
    return response


# Global 500 error page, but the parameter is different with the other three,
# that is it does not need to be the exception
def handler_500_error(request, template_name='500_error_page.html'):
    from django.shortcuts import render_to_response
    response = render_to_response('500_error_page.html')
    response.status_code = 500
    return response
