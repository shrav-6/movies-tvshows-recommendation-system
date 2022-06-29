from django import forms
from django.forms import formset_factory
class EnterMoviesForm(forms.Form):
   moviename = forms.CharField(label = "", max_length=200, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a movie name',
            
        }))
EnterMoviesFormset = formset_factory(EnterMoviesForm, extra=1)