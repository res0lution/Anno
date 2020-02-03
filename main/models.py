from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification

# Create your models here.
class AnnoUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Прошёл активацию")
    send_messages = models.BooleanField(default=True, verbose_name="Оповещения о новых комменариях")

    class Meta(AbstractUser.Meta):
        pass

user_registrated = Signal(providing_args=['instance']) 

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher) 

class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Haзвaниe')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Пop дoк')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
    verbose_name='Haдpyбpикa')

class SuperRubricМanager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)

class SuperRubric(Rubric):
    objects = SuperRubricМanager()
        
    def str (self) :
        return self.name
        
    class Meta:
        proxy = True
        ordering = ( 'order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'

class SubRubricManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)

class SubRubric(Rubric):
    objects = SubRubricManager()

    def str (self):
        return '%s - %s' % (self.super_rubric.name, self.name) 
    
    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики' 