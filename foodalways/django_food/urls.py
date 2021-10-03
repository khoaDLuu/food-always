"""django_food URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path, include
import xadmin
from xadmin.plugins import xversion

from django.views.static import serve

from django_food import settings

from user.views import HomePageView, about
from operation import views as operation_views


xadmin.autodiscover()
xversion.register_models()


urlpatterns = [

    # path('admin/', admin.site.urls),
    path("dashboard/", xadmin.site.urls),

    path("", HomePageView.as_view(), name="home_page"),

    path("food/", include("food.urls")),

    # User related, caveat: don't use params with apps, or an error will show
    path("user/", include("user.urls")),

    path("user_center/", include("operation.urls")),

    path('media/<path:path>/', serve, {'document_root': settings.MEDIA_ROOT}),

    path('captcha/', include('captcha.urls')),

    path('message/', operation_views.MessageBoardView.as_view(), name="message"),

    path('about/', about, name='about'),

    # Static file path, used for debugging error pages
    # path('static/<path:path>/', serve, {'document_root': settings.STATIC_ROOT}),
]


handler400 = "operation.views.handler_400_error"
handler403 = "operation.views.handler_403_error"
handler404 = "operation.views.handler_404_error"
handler500 = "operation.views.handler_500_error"
