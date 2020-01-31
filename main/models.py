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