from .models import SubRubric

def anno_context_processor(request):
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context 
