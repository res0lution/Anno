from django.urls import path
from .views import index, other_page, AnnoLoginView, profile
from .views import AnnoLogoutView, ChangeUserDataView, AnnoPasswordChangeView
from .views import RegisterUserView, RegisterDoneView

app_name = 'main'
urlpatterns = [
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/' , RegisterUserView.as_view(), name='register'), 
    path('accounts/logout/', AnnoLogoutView.as_view() , name='logout'), 
    path('accounts/profile/change/', ChangeUserDataView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/password/change/', AnnoPasswordChangeView.as_view(), name='password_change'), 
    path('accounts/login/', AnnoLoginView.as_view(), name='login'), 
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index')
]