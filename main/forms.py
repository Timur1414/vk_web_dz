from django import forms
from django.contrib.auth.models import User

from main.models import Answer


class AskForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title')
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Text')
    author = forms.IntegerField(widget=forms.HiddenInput())
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Tags')


class SettingsForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    nickname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}), label='NickName')
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), label='Avatar', required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.save()
            profile = user.profile
            profile.nickname = self.cleaned_data['nickname']
            if self.cleaned_data['avatar']:
                profile.avatar = self.cleaned_data['avatar']
            profile.save()
        return user


class CreateAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'author', 'question']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control my-2', 'placeholder': 'Enter your answer here...'}),
            'author': forms.HiddenInput(),
            'question': forms.HiddenInput(),
        }
