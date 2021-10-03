import xadmin
from xadmin import views

from .models import UserMessage, UserFav, UserLike, MessageBoard


class UserLikeAdmin:
    list_display = ['user', 'like_id', 'like_type', 'add_time']
    search_fields = ['user', 'like_id', 'like_type']
    list_filter = ['user', 'like_id', 'like_type', 'add_time']
    model_icon = "fa fa-heart-o"


class UserMessageAdmin:
    list_display = ['user', 'readable', 'message_title', 'message_content', 'add_time']
    search_fields = ['user', 'readable', 'message_title', 'message_content']
    list_filter = ['user', 'readable', 'message_title', 'message_content', 'add_time']
    model_icon = "fa fa-comment-o"


class UserFavAdmin:
    list_display = ['user', 'fav_id', 'fav_type', 'add_time']
    search_fields = ['user', 'fav_id', 'fav_type']
    list_filter = ['user', 'fav_id', 'fav_type', 'add_time']
    model_icon = "fa fa-star-o"


class MessageBoardAdmin:
    list_display = ['name', 'email', 'is_user', 'message', 'add_time']
    search_fields = ['name', 'email', 'is_user', 'message']
    list_filter = ['name', 'email', 'is_user', 'message', 'add_time']
    model_icon = "fa fa-comments-o"


xadmin.site.register(UserLike, UserLikeAdmin)
xadmin.site.register(UserFav, UserFavAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(MessageBoard, MessageBoardAdmin)
