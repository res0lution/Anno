from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import AnnoUser, SubRubric, Anno, Comment
from .forms import ChangeUserDataForm, RegisterUserForm, SearchForm, AnnoForm, AIFormSet, UserCommentForm, GuestCommentForm
from .utilities import signer

# Create your views here.
def index(request):
    anno = Anno.objects.filter(is_active=True)[:10]
    context = {'anno': anno}
    return render(request, 'main/index.html', context)

def other_page(request, page):

    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404

    return HttpResponse(template.render(request=request))


class AnnoLoginView(LoginView):
    template_name = 'main/login.html'

@login_required
def profile(request):
    anno = Anno.objects.filter(author=request.user.pk)
    context = {'anno': anno } 
    return render(request, 'main/profile.html', context)


class AnnoLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


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


class AnnoPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
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
    template_name = 'main/delete_user.html'
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
    rubric = get_object_or_404(SubRubric, pk=pk)
    anno = Anno.objects.filter(is_active=True, rubric=pk)

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        anno = anno.filter(q)
    else:
        keyword = ''

    form = SearchForm(initial = {'keyword' : keyword})
    paginator = Paginator(anno, 2)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'anno': page.object_list,
    'form': form}
    return render(request, 'main/by_rubric.html', context)  

def detail(request, rubric_pk, pk):
    anno = get_object_or_404(Anno, pk=pk)
    ais = anno.additionalimage_set.all()
    comments = Comment.objects.filter(anno=pk, is_active=True)
    initial = {'anno': anno.pk }

    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm

    form = form_class(initial=initial)

    if request.method == 'POST':
        c_form = form_class(request.POST)

        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = с_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')

    context = {'anno': anno, 'ais': ais, 'comments': comments, 'form': form} 
    return render(request, 'main/detail.html', context)

@login_required
def profile_anno_add(request):

    if request.method == 'POST':
        form = AnnoForm(request.POST, request.FILES)

        if form.is_valid():
            anno = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=anno)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = AnnoForm(initial={'author': request.user.pk})
        formset = AIFormSet()

    context = { 'form':form, 'formset':formset}
    return render(request, 'main/profile_anno_add.html', context)

@login_required
def profile_anno_change(request, pk):
    anno = get_object_or_404(Anno, pk=pk)

    if request.method == 'POST':
        form = AnnoForm(request.POST, request.FILES, instance=anno)

        if form.is_valid():
            anno = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=anno)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = AnnoForm(instance=anno)
        formset = AIFormSet(instance=anno)
        context = { 'form' : form, 'formset' : formset}
        return render(request, 'main/profile_anno_change.html', context)

@login_required
def profile_anno_delete(request, pk):
    anno = get_object_or_404(Anno, pk=pk)
    
    if request.method == 'POST':
        anno.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'anno' : anno }
        return render(request, 'main/profile_anno_delete.html', context)

@login_required
def profile_anno_detail(request, pk):
    anno = get_object_or_404(Anno, pk=pk)
    ais = anno.additionalimage_set.all()
    context = {'anno': anno, 'ais': ais }
    return render(request, 'main/profile_anno_detail.html', context)




 










