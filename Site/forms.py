from django import forms
from django.core.exceptions import ValidationError
from .models import User, DesignApplication, Category
import re
from django.core.validators import FileExtensionValidator

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(required=True, max_length=100, label='Имя пользователя', widget=forms.TextInput())
    email = forms.CharField(required=True, max_length=100, label='Email', widget=forms.TextInput())
    first_name = forms.CharField(required=True, max_length=100, label='Имя', widget=forms.TextInput())
    last_name = forms.CharField(required=True, max_length=100, label='Фамилия', widget=forms.TextInput())
    patronymic = forms.CharField(required=True, max_length=100, label='Отчество',  widget=forms.TextInput())
    password = forms.CharField(required=True, max_length=100, label='Пароль', widget=forms.PasswordInput)
    password_repeat = forms.CharField(required=True, max_length=100, label='Повторите пароль', widget=forms.PasswordInput)
    consent = forms.BooleanField(required=True, label='Согласие на обработку персональных данных', widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'patronymic', 'password']

    def check_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Данное имя пользователя уже занято')
        if not re.match(r'^[A-z-]+$', username):
            raise ValidationError('Имя пользователя может содержать только латиницу и дефисы')
        return username

    def check_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[А-я\s-]+$', first_name):
            raise ValidationError('Имя может содержать только кириллицу, пробелы и дефисы')
        return first_name

    def check_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[А-я\s-]+$', last_name):
            raise ValidationError('Фамилия может содержать только кириллицу, пробелы и дефисы')
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError('Пароли не совпадают')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=100)
    password = forms.CharField(required=True, max_length=100, widget=forms.PasswordInput)

class CreateApplicationForm(forms.ModelForm):
    title = forms.CharField(required=True, max_length=100, label='Название', widget=forms.TextInput())
    description = forms.CharField(required=True, max_length=100, label='Описание', widget=forms.Textarea())
    photo = forms.FileField(required=True, label='Фото помещения', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])])

    class Meta:
        model = DesignApplication
        fields = ['title', 'description', 'category', 'photo']
        widgets = {'category':  forms.CheckboxSelectMultiple()}

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo.size > 1024*1024*2:
            raise ValidationError('Файл слишком большой. Размер не должен превышать 2 МБ.')
        return photo

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        app = super().save(commit=False)
        if self.user:
            app.creator = self.user

        if commit:
            app.save()
            self.save_m2m()
        return app