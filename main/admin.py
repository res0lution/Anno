from django.contrib import admin
from .models import AnnoUser, SuperRubric, SubRubric
from .utilities import send_activation_notification
from .forms import SubRubricForm
import datetime

# Register your models here.
class SubRubricInline(admin.TabularInline):
    model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm

admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin) 
admin.site.register(AnnoUser)
