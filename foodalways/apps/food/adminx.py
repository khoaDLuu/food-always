import os
from PIL import Image
import shutil

import xadmin
from xadmin import views
from django_food.settings import BASE_DIR

from .models import FoodImage, FoodArticle, FoodSteps, Tags, ImageTags, FoodIngredients


class FoodStepsInline:
    model = FoodSteps
    extra = 1


class FoodIngredientsLine:
    model = FoodIngredients
    extra = 1


class TagsAdmin:
    list_display = ['name', 'add_time']
    search_fields = ['name']
    list_filter = ['name', 'add_time']
    model_icon = "fa fa-tags"
    list_editable = ['name']

    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(foodarticle__author=self.request.user.username)
            return qs


class FoodIngredientsAdmin:
    list_display = ['article_id', 'classification', 'name', 'dosage', 'add_time']
    search_fields = ['article_id', 'classification', 'name', 'dosage']
    list_filter = ['article_id', 'classification', 'name', 'dosage', 'add_time']
    list_editable = ['classification', 'name', 'dosage']
    exclude = ['add_time']
    model_icon = "fa fa-ellipsis-h"
    ordering = ['article_id', 'classification']

    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(article_id__author=self.request.user.username)
            return qs


class FoodArticleAdmin:
    list_display = ['article_id', 'name', 'ingredient_list',
                    'image', 'author', 'like',
                    'fav', 'click_number', 'tags', 'add_time']
    search_fields = ['article_id', 'name', 'ingredient_list',
                     'image', 'author', 'like',
                     'fav', 'click_number', 'tags']
    list_filter = ['article_id', 'name', 'ingredient_list',
                   'image', 'author', 'like',
                   'fav', 'click_number', 'tags', 'add_time']

    model_icon = "fa fa-lemon-o"

    # Dynamic data, readable but not writable
    # readonly_fields = ['like', 'fav', 'click_number']
    # The display of the background control field will be no longer displayed
    # in the background if added to the list below
    # The fields in readonly_fields and exclude cannot appear in both lists at the same time
    exclude = ['ingredient_list', 'author', 'like', 'fav', 'click_number']

    # Data loading method of background foreign keys,
    # use ajax to load (for search function)
    relfield_style = 'fk-ajax'
    fk_fields = ['name']
    # The background display style of the field,
    # the left side is all the labels,
    # and the right side is the selected label
    style_fields = {'tags': 'm2m_transfer'}

    # Used for one module to manage another module,
    # it can add prep steps directly when adding food,
    # but only one level of nesting can be achieved
    inlines = [FoodIngredientsLine, FoodStepsInline]
    list_editable = ['name']

    # Filter out the food articles uploaded by the logged-in user
    # (if it is a super user, all articles will be displayed)
    def queryset(self):
        qs = super().queryset()
        if self.user.is_superuser:
            return qs
        else:
            qs = qs.filter(author=self.user.username)
            return qs

    def save_models(self):
        obj = self.new_obj

        # Modify image data, this is a file object whose class is python file
        image = self.request.FILES.get('image').read()
        path = os.path.join(BASE_DIR, 'media', 'food_article', f'{obj.article_id}')
        if not os.path.isdir(path):
            os.makedirs(path)

        # Save the original picture
        with open(os.path.join(path, 'full.jpg'), 'wb') as f:
            f.write(image)

        # Reduce image size
        with Image.open(os.path.join(path, 'full.jpg')) as img:
            img = img.convert("RGB")
            x, y = img.size
            new_x = 320
            new_y = int(y * new_x / x)
            small_image = img.resize((new_x, new_y), Image. ANTIALIAS)
            small_image.save(os.path.join(path, 'small.jpg'))

        # Get the author, ingredient and image data of the article
        obj.author = self.user.username
        obj.image = os.path.join('food_article', f'{obj.article_id}', 'small.jpg')
        in_list = []
        food_in_length = int(self.request.POST.get('foodingredients_set-TOTAL_FORMS', 0))
        for i in range(0, food_in_length):
            in_list.append(self.request.POST.get(f"foodingredients_set-{i}-name"))
        if in_list:
            obj.ingredient_list = "Ingredients: " + ', '.join(in_list)
        obj.save()

    def delete_models(self, obj):
        remove_list = (
            os.path.join(BASE_DIR, 'media', 'food_article', f'{item.article_id}')
            for item in obj
        )
        for item in remove_list:
            shutil.rmtree(item)
        obj.delete()


    # # Select the data displayed by the article model according to the type of logged-in user
    # def get_model_form(self, **kwargs):
    #     user = self.request.user
    #     if user.is_superuser:
    #         self.readonly_fields = ['like', 'fav', 'click_number']
    #         self.exclude = []
    #     else:
    #         self.readonly_fields = []
    #         self.exclude = ['ingredient_list', 'author', 'like', 'fav', 'click_number']
    #     return super().author_display()


# # This backend model is suitable for author related data display
# # The author can only see his own article data
# class UserFoodArticleAdmin:
#     list_display = ['article_id', 'name', 'ingredient_list',
#                     'image', 'author', 'like',
#                     'fav', 'click_number', 'tags', 'add_time']
#     search_fields = ['article_id', 'name', 'ingredient_list',
#                      'image', 'author', 'like',
#                      'fav', 'click_number', 'tags']
#     list_filter = ['article_id', 'name', 'ingredient_list',
#                    'image', 'author', 'like',
#                    'fav', 'click_number', 'tags', 'add_time']
#     model_icon = "fa fa-lemon-o"
#     readonly_fields = ['like', 'fav', 'click_number']
#     # exclude = []
#     relfield_style = 'fk-ajax'
#     style_fields = {'tags': 'm2m_transfer'}
#     inlines = [FoodStepsInline]


class FoodStepsAdmin:
    list_display = ['article_id', 'step_number', 'description',
                    'image', 'add_time']
    search_fields = ['article_id', 'step_number', 'description',
                     'image']
    list_filter = ['article_id', 'step_number', 'description',
                   'image', 'add_time']
    model_icon = "fa fa-spinner"

    ordering = ['-article_id', 'step_number']
    list_editable = ['description']
    exclude = ['add_time']

    def queryset(self):
        qs = super().queryset()
        if self.request.user.is_superuser:
            return qs
        else:
            qs = qs.filter(article_id__author=self.request.user.username)
            return qs


class ImageTagsAdmin:
    list_display = ['name', 'add_time']
    search_fields = ['name']
    list_filter = ['name', 'add_time']
    model_icon = "fa fa-tags"
    list_editable = ['name']


class FoodImageAdmin:
    list_display = ['name', 'image', 'like', 'fav',
                    'click_number', 'tags', 'add_time']
    search_fields = ['name', 'image', 'like', 'fav',
                     'click_number', 'tags', 'add_time']
    list_filter = ['name', 'image', 'like', 'fav',
                   'click_number', 'tags', 'add_time']
    model_icon = "fa fa-picture-o"

    readonly_fields = ['like', 'fav', 'click_number']

    style_fields = {'tags': 'm2m_transfer'}
    list_editable = ['tags']


xadmin.site.register(FoodArticle, FoodArticleAdmin)
xadmin.site.register(FoodIngredients, FoodIngredientsAdmin)
xadmin.site.register(FoodSteps, FoodStepsAdmin)
xadmin.site.register(Tags, TagsAdmin)
xadmin.site.register(FoodImage, FoodImageAdmin)
xadmin.site.register(ImageTags, ImageTagsAdmin)
