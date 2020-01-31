from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import AnnoUser
from .forms import ChangeUserDataForm, RegisterUserForm
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def other_page(request, page):

    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404

    return HttpResponse(template.render(request=request))

class AnnoLoginView(LoginView):
    template_name = "main/login.html"

@login_required
def profile(request):
    return render(request, 'main/profile.html')

class AnnoLogoutView(LogoutView):
    template_name = "main/logout.html"

class ChangeUserDataView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AnnoUser
    template_name = 'main/change_user_data.html'
    form_class = ChangeUserDataForm
    success_url = reverse_lazy('main:profile')
    success_message = 'личные данные пользователя изменены'
    
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        
        return get_object_or_404(queryset, pk=self.user_id) 

class AnnoPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView) :
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя был изменен' 

class RegisterUserView(CreateView):
    model = AnnoUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main/register_done.html')

class RegisterDoneView(TemplateView):
    template_name = 'main/ egister_done.html' 



