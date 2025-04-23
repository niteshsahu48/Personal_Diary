from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import RegisterUser, Expense, Notebook, Category
from django.contrib.auth.models import User






# User Login Form
    class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

# Expense Form
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['add_note', 'amount', 'category']
        widgets = {
            'add_note': forms.TextInput(attrs={'placeholder': 'Optional note'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Notebook Entry Form
class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Notebook title'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your notes here...'}),
        }

# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']
        widgets = {
            'category_name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
        }
