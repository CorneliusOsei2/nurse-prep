from django import forms
from .models import Card, Category


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['category', 'deck', 'question', 'answer', 'rationale']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
            'answer': forms.Textarea(attrs={'rows': 3}),
            'rationale': forms.Textarea(attrs={'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']


class ImportForm(forms.Form):
    file = forms.FileField(label='JSON file')
