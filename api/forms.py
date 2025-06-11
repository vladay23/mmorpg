# mmorpg_forum/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Guide, News, Event

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pw_confirm = cleaned_data.get('password_confirm')

        if pw and pw_confirm and pw != pw_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают')
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class GuideForm(forms.ModelForm):
    author_id = forms.IntegerField(
        required=True,
        label='ID автора',
        widget=forms.NumberInput(attrs={'placeholder': 'Введите ID автора'})
    )
    image = forms.ImageField(
        required=False,
        label='Изображение'
    )

    class Meta:
        model = Guide
        fields = ['author_id', 'title', 'description', 'content', 'image']
        widgets = {
            'author_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        guide = super().save(commit=False)
        # Установка автора по ID
        author_id = self.cleaned_data['author_id']
        from django.contrib.auth.models import User
        try:
            guide.author = User.objects.get(pk=author_id)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким ID не найден.")
        if commit:
            guide.save()
        return guide
    

class NewsForm(forms.ModelForm):
    author_id = forms.IntegerField(
        required=True,
        label='ID автора',
        widget=forms.NumberInput(attrs={'placeholder': 'Введите ID автора'})
    )
    image = forms.ImageField(
        required=False,
        label='Изображение'
    )

    class Meta:
        model = News
        fields = ['author_id', 'title', 'content', 'published_at', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        news = super().save(commit=False)
        author_id = self.cleaned_data['author_id']
        try:
            news.author = User.objects.get(pk=author_id)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким ID не найден.")
        if commit:
            news.save()
        return news

class EventForm(forms.ModelForm):
    organizer_id = forms.IntegerField(
        required=True,
        label='ID организатора',
        widget=forms.NumberInput(attrs={'placeholder': 'Введите ID организатора'})
    )

    class Meta:
        model = Event
        fields = ['organizer_id', 'title', 'description', 'date', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        event = super().save(commit=False)
        organizer_id = self.cleaned_data['organizer_id']
        try:
            event.organizer = User.objects.get(pk=organizer_id)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким ID не найден.")
        if commit:
            event.save()
        return event