from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import AnnoUser
from .forms import ChangeUserDataForm, RegisterUserForm
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from .utilities import signer
from django.contrib.auth import logout
from django.contrib import messages

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
    success_url = reverse_lazy('main:register_done')

class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AnnoUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

class DeleteUserView(LoginRequiredMixin, DeleteView):
    template_name = "main/delete_user.html"
    model = AnnoUser
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id) 

def by_rubric(request, pk):
    pass 









