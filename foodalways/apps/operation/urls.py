from django.urls import path

from . import views

app_name = 'operator'

urlpatterns = [
    path('', views.user_center, name="user_center"),
    path('change_head_portrait/', views.ChangeHeaderPortraitView.as_view(), name="change_head_portrait"),
    path('change_user_info/', views.ChangeUserInfoView.as_view(), name="change_user_info"),
    path('refresh_captcha/', views.refresh_captcha, name="refresh_captcha"),
    path('change_password/', views.ChangePasswordView.as_view(), name="change_password"),
    path('get_email_code/', views.get_change_email_code, name="get_email_code"),
    path('change_email/', views.ChangeEmailView.as_view(), name="change_email"),

    path('user_like/', views.UserLikeView.as_view(), name="user_like"),
    path('user_fav/', views.UserFavView.as_view(), name="user_fav"),
    path('user_message/', views.UserMessageView.as_view(), name="user_message"),

    path('add_like/', views.AddLikeView.as_view(), name="add_like"),
    path('add_fav/', views.AddFavView.as_view(), name="add_fav"),

    path('del_like/<slug:like_id>', views.DelLikeView.as_view(), name="del_like"),
    path('del_fav/<slug:fav_id>', views.DelFavView.as_view(), name="del_fav"),

    path('del_message/<slug:message_id>', views.DelMessageView.as_view(), name="del_message"),
    path('read_message/<slug:message_id>', views.ReadMessageView.as_view(), name="read_message"),

    path('add_message_board', views.AddMessageView.as_view(), name="add_message_board"),

    path('upload_food_article/', views.UploadFoodArticle.as_view(), name="upload_food_article"),

    path('get_user_message/', views.GetUserMessageView.as_view(), name="get_user_message"),
]
