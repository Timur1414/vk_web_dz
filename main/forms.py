from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django_ckeditor_5.widgets import CKEditor5Widget
from main.models import Answer, Question, Tag, Profile
from vk_dz import settings


class RegistrationForm(UserCreationForm):
    """
    Form for user registration.
    Extends Django's UserCreationForm to include a nickname field.
    """
    nickname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='NickName*', max_length=50)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email*', max_length=50)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), label='Avatar', required=False)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Avatar size must be less than 5MB')
        return avatar

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if len(nickname) > 50:
            raise forms.ValidationError('Nickname must be between 50 characters')
        if Profile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('Nickname already exists')
        return nickname

    def clean_email(self):
        email = self.cleaned_data['email']
        if len(email) > 50:
            raise forms.ValidationError('Email must be between 50 characters')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email


class AskForm(forms.ModelForm):
    """
    Form for asking a new question.
    Includes fields for question title, text, and tags.
    Tags should be entered as comma-separated values.
    """
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2, tag3...'}), label='Tags*', max_length=100)

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Title*',
            'text': 'Text*',
        }

    def clean_tags(self):
        tags_text = self.cleaned_data['tags'].strip()
        while '  ' in tags_text:
            tags_text = tags_text.replace('  ', ' ')
        tags_text = tags_text.replace(', ', ',')
        tags_words = tags_text.split(',')
        tags_words = [tag_word for tag_word in tags_words if tag_word]
        for tag_text in tags_words:
            if len(tag_text) > 50:
                raise forms.ValidationError('Tag too long')
        return ','.join(tags_words)

    def save(self, commit=True):
        with transaction.atomic():
            question = super().save(commit=commit)
            tags_words = self.cleaned_data['tags'].split(',')
            existing_tags_names = Tag.objects.filter(text__in=tags_words).values_list('text', flat=True)
            new_tags = [Tag(text=tag_text) for tag_text in tags_words if tag_text not in existing_tags_names]
            Tag.bulk_create_with_color(new_tags)
            tags = Tag.objects.filter(text__in=tags_words)
            question.add_tags(tags)


class SettingsForm(forms.ModelForm):
    """
    Form for updating user profile settings.
    Allows users to update their username, email, nickname, and avatar.
    The avatar field is optional.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login*')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email*')
    nickname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}), label='NickName*')
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), label='Avatar', required=False)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Avatar size must be less than 5MB')
        return avatar

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
    """
    Form for creating a new answer to a question.
    Includes a text area for the answer content.
    """
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': CKEditor5Widget(attrs={'placeholder': 'enter answer here...'}),
        }
