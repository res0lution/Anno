from django.urls import path

from .views import index, other_page, AnnoLoginView, profile, by_rubric, detail
from .views import AnnoLogoutView, ChangeUserDataView, AnnoPasswordChangeView, profile_anno_add
from .views import RegisterUserView, RegisterDoneView, user_activate, DeleteUserView
from .views import profile_anno_change, profile_anno_delete, profile_anno_detail

app_name = 'main'
urlpatterns = [
    path('accounts/reqister/activate/<str:sign>/', user_activate, name='register_activate'), 
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/' , RegisterUserView.as_view(), name='register'), 
    path('accounts/logout/', AnnoLogoutView.as_view() , name='logout'),
    path('accounts/profile/change/<int:pk>/', profile_anno_change, name='profile_anno_change'),
    path('accounts/profile/delete/<int:pk>/' , profile_anno_delete, name='profile_anno_delete'),
    path('accounts/profile/<int:pk>/', profile_anno_detail, name='profile_anno_detail'),
    path('accounts/profile/change/', ChangeUserDataView.as_view(), name='profile_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'), 
    path('accounts/profile/add/', profile_anno_add, name='profile_anno_add'), 
    path('accounts/profile/', profile, name='profile'),
    path('accounts/password/change/', AnnoPasswordChangeView.as_view(), name='password_change'), 
    path('accounts/login/', AnnoLoginView.as_view(), name='login'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index')
]