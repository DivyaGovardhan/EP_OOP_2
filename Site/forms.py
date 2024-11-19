from datetime import timedelta, time, date

from django import forms
from django.core.exceptions import ValidationError
# from django.utils.datetime_safe import date

from .models import User, DesignApplication
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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Данное имя пользователя уже занято')
        if not re.match(r'^[A-z-]+$', username):
            raise ValidationError('Имя пользователя может содержать только латиницу и дефисы')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[A-z][\w.-]+@[\w.-]+\.[A-z]{2,6}$', email):
            raise ValidationError('Адрес электронной почты не валиден')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[А-яёЁ\s-]+$', first_name):
            raise ValidationError('Имя может содержать только кириллицу, пробелы и дефисы')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[А-яёЁ\s-]+$', last_name):
            raise ValidationError('Фамилия может содержать только кириллицу, пробелы и дефисы')
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        print(f'Password: {password}')
        print(f'Password repeat: {password_repeat}')
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
    completion_date = forms.DateField(required=True, label='Дата заявки', widget=forms.DateInput(attrs={'type': 'date'}))
    completion_time = forms.TimeField(required=True, label='Время заявки', widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DesignApplication
        fields = ['title', 'description', 'category', 'photo']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo.size > 1024*1024*2:
            raise ValidationError('Файл слишком большой. Размер не должен превышать 2 МБ')
        return photo

    def clean_completion_date(self):
        completion_date = self.cleaned_data.get('completion_date')
        today = date.today()
        tomorrow = today + timedelta(days=1)

        if completion_date < today or completion_date == tomorrow:
            raise ValidationError('Можно выбрать только даты после завтрашнего дня')

        return completion_date

    def clean_completion_time(self):
        completion_time = self.cleaned_data.get('completion_time')

        if completion_time < time(9, 0) or completion_time > time(19, 0):
            raise ValidationError('Время должно быть между 9:00 и 19:00')

        return completion_time

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        app = super().save(commit=False)
        if self.user:
            app.creator = self.user

        if commit:
            app.save()
            self.save_m2m()
        return app

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class RedactAppForm(forms.ModelForm):
    design_comment = forms.CharField(required=False, max_length=200, label='', widget=forms.Textarea(attrs={'placeholder': 'Комментарий'}))
    design_photo = forms.FileField(required=False, label='Изображение дизайна', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])])

    class Meta:
        model = DesignApplication
        fields = ['category', 'status', 'design_comment', 'design_photo']

    def clean_design_comment(self):
        new_status = self.cleaned_data.get('status')
        design_comment = self.cleaned_data.get('design_comment')
        if new_status == 'w' and not design_comment:
            raise ValidationError('Комментарий должен быть заполнен')
        return design_comment

    def clean_design_photo(self):
        new_status = self.cleaned_data.get('status')
        design_photo = self.cleaned_data.get('design_photo')
        if new_status == 'd' and not design_photo:
            raise ValidationError('Изображение должно быть заполнено')
        return design_photo

    def __init__(self, *args, **kwargs):
        super(RedactAppForm, self).__init__(*args, **kwargs)
        if self.initial.get('status') in ['w', 'd']:
            self.fields['status'].disabled = True
        if self.initial.get('status') == 'w':
            self.fields['design_comment'].required = True
            self.fields['design_photo'].required = False
        elif self.initial.get('status') == 'd':
            self.fields['design_comment'].required = False
            self.fields['design_photo'].required = True
        else:
            self.fields['design_comment'].required = False
            self.fields['design_photo'].required = False

class AppFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все'),
        ('n', 'Новая'),
        ('w', 'Принято в работу'),
        ('d', 'Выполнено'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Статус')