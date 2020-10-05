from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favorites/', views.favorites, name='favorites'),
    path('accounts/signup/', views.signup, name='signup'),
    path('search/', views.search, name='search'),
    path('pets/<int:api_pet_id>/', views.pets_show, name='pets_show'),
    path('pets/create/', views.pets_create, name='pets_create'),
    path('pets/delete/', views.pets_delete, name='pets_delete'),
    path('pets/update/', views.pets_update, name='pets_update'),
]
