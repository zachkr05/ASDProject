from django.urls import path
from . import views
from .views import signup, signin_view
app_name = "accounts"
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('profile/', views.profile, name='profile'),
]
