from django import forms

class Search(forms.Form):
    q = forms.CharField(label='search', max_length=100)