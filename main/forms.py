from django import forms


class AskForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title')
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Text')
    author = forms.IntegerField(widget=forms.HiddenInput())
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Tags')
