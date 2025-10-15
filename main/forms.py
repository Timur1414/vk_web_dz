from django import forms
from django.contrib.auth.models import User
from main.models import Answer, Question, Tag


class AskForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Tags')

    class Meta:
        model = Question
        fields = ['title', 'text', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.HiddenInput(),
        }
        labels = {
            'title': 'Title',
            'text': 'Text',
        }

    def save(self, commit=True):
        question = super().save(commit=commit)
        tags_text = self.cleaned_data['tags'].strip()
        while '  ' in tags_text:
            tags_text = tags_text.replace('  ', ' ')
        tags_text = tags_text.replace(', ', ',')
        tags_words = tags_text.split(',')
        for tag_text in tags_words:
            tag = Tag.get_or_create(tag_text)
            question.add_tag(tag)


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
