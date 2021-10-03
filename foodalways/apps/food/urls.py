




from django.urls import path

from . import views

app_name = "food"

urlpatterns = [
    path("food_article/<slug:article_id>/", views.FoodArticleView.as_view(), name="food_article"),
    path("food_ranking/", views.FoodRankingView.as_view(), name="food_ranking"),
    path("tag_food/<path:tag>", views.TagFoodView.as_view(), name="tag_food"),
    path("food_image_rank/", views.FoodImageRankView.as_view(), name="food_image_rank"),
    path("food_image/<slug:image_id>/", views.SingleFoodImageView.as_view(), name="food_image"),
    path("tag_image/<path:tag>", views.TagImageView.as_view(), name="tag_image"),
    path("search/", views.SearchView.as_view(), name="search"),

]
