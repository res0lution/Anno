from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from django.db.models.signals import post_save 

from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification

# Create your models here.
class AnnoUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошёл активацию')
    send_messages = models.BooleanField(default=True, verbose_name='Оповещения о новых комменариях')

    def delete(self, *arqs, **kwarqs):

        for item in self.anno_set.all():
            item.delete()

        super().delete(*args, **kwargs) 


    class Meta(AbstractUser.Meta):
        pass

user_registrated = Signal(providing_args=['instance']) 

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher) 


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Haзвaниe')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Пopядoк')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
    verbose_name='Haдpyбpикa')


class SuperRubricМanager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricМanager()
        
    def __str__(self) :
        return self.name
        

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name) 
    

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики' 


class Anno(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='Pyбpикa')
    title = models.CharField(max_length=40, verbose_name='Toвap')
    content = models.TextField(verbose_name='Oпиcaниe')
    price = models.FloatField(default=0, verbose_name='Цeнa')
    contacts = models.TextField(verbose_name='Koнтaкты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey(AnnoUser, on_delete=models.CASCADE, verbose_name='Aвтop объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):

        for ai in self.additionalimage_set.all():
            ai.delete()

        super().delete(*args, **kwargs)
    

    class Meta:
        verbose_name = 'Обьявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at'] 


class AdditionalImage(models.Model):
    anno = models.ForeignKey(Anno, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')
    

    class Meta:
        verbose_name = 'Дополнительная иллюстрация'
        verbose_name_plural = 'Дополнительные иллюстрации'


class Comment(models.Model):
    anno = models.ForeignKey(Anno, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Aвтop')
    content = models.TextField(verbose_name='Coдepжaниe')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')
    

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-created_at']

def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].anno.author
    
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])

post_save.connect(post_save_dispatcher, sender=Comment)  
