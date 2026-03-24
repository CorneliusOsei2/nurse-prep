from django import forms
from .models import Card, Category, Deck


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['category', 'deck', 'question', 'answer', 'rationale']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'deck': forms.Select(attrs={'class': 'form-select'}),
            'question': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Enter the question...'}),
            'answer': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Enter the answer...'}),
            'rationale': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Why is this the correct answer? (optional)'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Pharmacology II'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 💉', 'style': 'width:80px'}),
        }


class ImportForm(forms.Form):
    file = forms.FileField(
        label='JSON File',
        help_text='Upload a .json file exported from NursePrep',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.json'})
    )
