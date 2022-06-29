from django import forms
class EnterMovies(forms.Form):
   moviename = forms.CharField(label = "", max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Enter a movie'}))