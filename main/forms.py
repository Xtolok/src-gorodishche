from django import forms
from django.core.exceptions import ValidationError

from .models import FeedbackSubmission


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackSubmission
        fields = ('phone', 'email', 'text')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'autocomplete': 'tel',
                'placeholder': '+7 (___) ___-__-__',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'autocomplete': 'email',
                'placeholder': 'example@mail.ru',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Опишите ваше обращение',
            }),
        }
        labels = {
            'phone': 'Телефон',
            'email': 'Электронная почта',
            'text': 'Текст обращения',
        }

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get('phone', '').strip()
        email = cleaned.get('email', '').strip()
        if not phone and not email:
            raise ValidationError('Укажите телефон или электронную почту для обратной связи.')
        cleaned['phone'] = phone
        cleaned['email'] = email
        return cleaned
