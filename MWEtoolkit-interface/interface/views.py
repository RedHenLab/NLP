from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import WordForm
from django.forms.formsets import formset_factory

# Create your views here.


def xml(request):

    TemplateBuilder = formset_factory(WordForm, extra=2)

    if request.method == 'POST':
        formset = TemplateBuilder(request.POST, request.FILES)
        if formset.is_valid():
            return HttpResponseRedirect('/thanks/')

    else:
        formset = TemplateBuilder()

    return render(request, 'xml_builder.html', {'builder': formset})


def thanks(request):
    return render(request, 'thanks.html')