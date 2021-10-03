import xadmin
from xadmin import views

from .models import EmailVerifyCode


class BaseSetting:
    # Change background theme style
    enable_themes = True
    use_bootswatch = True


class GlobalSettings:
    # Change the title and footer display of the background
    site_title = "Background management system"
    site_footer = "Foodalways"
    # The application model is displayed as a drop-down style in the navigation bar of the background page
    menu_style = "accordion"


class EmailVerifyCodeAdmin:
    # Used to display the information of the mail verification code form
    # according to the columns email, code, send_type, send_time
    list_display = ['email', 'code', 'send_type', "verify_times", 'send_time']
    # Enable the "check" operation of the data table by setting the search_fields field
    search_fields = ['email', 'code', 'send_type']
    # Implement filtering function
    list_filter = ['email', 'code', 'send_type', 'send_time']
    model_icon = "fa fa-envelope-o"


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(EmailVerifyCode, EmailVerifyCodeAdmin)
