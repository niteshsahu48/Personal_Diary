from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Category, Notebook, Expense, RegisterUser
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models



User = get_user_model()

def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        hashed_password = make_password(password)
        user = RegisterUser(username=username, password=hashed_password, email=email)
        user.save()
        return redirect('login_view') 
    return render(request, 'diary_app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('login_password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid email or password")
            return render(request, 'diary_app/login.html')
        
        login(request, user)
        return redirect('index')
    
    return render(request, 'diary_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login_view')

@login_required
def index(request): 
    categories = Category.objects.filter(user=request.user)
    notebooks = Notebook.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    
    context = {
        'categories': categories,
        'notebooks': notebooks,
        'expenses': expenses,
    }
    return render(request, 'diary_app/index.html', context)

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        Category.objects.create(user=request.user, category_name=category_name)
        return redirect('index')
    return render(request, 'diary_app/add_category.html')

@login_required
def edit_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category.category_name = category_name
        category.save()
        return redirect('index')
    return render(request, 'diary_app/edit_category.html', {'category': category})

@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    category.delete()
    return redirect('index')

@login_required
def add_notebook(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Notebook.objects.create(user=request.user, title=title, content=content)
        return redirect('index')
    return render(request, 'diary_app/add_notebook.html')

@login_required
def edit_notebook(request, notebook_id):
    notebook = Notebook.objects.get(id=notebook_id, user=request.user)
    if request.method == 'POST':
        notebook.title = request.POST.get('title')
        notebook.content = request.POST.get('content')
        notebook.save()
        return redirect('index')
    return render(request, 'diary_app/edit_notebook.html', {'notebook': notebook})

@login_required
def delete_notebook(request, notebook_id):
    notebook = Notebook.objects.get(id=notebook_id, user=request.user)
    notebook.delete()
    return redirect('index')

@login_required
def add_expense(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        add_note = request.POST.get('add_note')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        
        Expense.objects.create(user=request.user, amount=amount, add_note=add_note, category=category)
        return redirect('index')
    
    return render(request, 'diary_app/add_expense.html', {'categories': categories})

@login_required
def edit_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id, user=request.user)
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        expense.amount = request.POST.get('amount')
        expense.add_note = request.POST.get('add_note')
        category_id = request.POST.get('category')
        expense.category = Category.objects.get(id=category_id) if category_id else None
        expense.save()
        return redirect('index')
    
    return render(request, 'diary_app/edit_expense.html', {'expense': expense, 'categories': categories})

@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        expense.delete()
        return redirect('my_expenses')

    return render(request, 'diary_app/confirm_delete.html', {'expense': expense})

@login_required
def expenses_by_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    expenses = Expense.objects.filter(user=request.user, category=category)
    return render(request, 'diary_app/expenses_by_category.html', {
        'expenses': expenses,
        'category': category,
    })

@login_required
def notebook_detail(request, notebook_id):
    notebook = Notebook.objects.get(id=notebook_id, user=request.user)
    return render(request, 'diary_app/notebook_detail.html', {'notebook': notebook})

@login_required
def expense_detail(request, expense_id):
    expense = Expense.objects.get(id=expense_id, user=request.user)
    return render(request, 'diary_app/expense_detail.html', {'expense': expense})

@login_required
def my_expenses_view(request):
    categories = Category.objects.filter(user=request.user)
    selected_category = request.GET.get('category')

    if selected_category:
        expenses = Expense.objects.filter(user=request.user, category__id=selected_category).order_by('-created_at')
    else:
        expenses = Expense.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'diary_app/my_expenses.html', {
        'expenses': expenses,
        'categories': categories,
        'selected_category': selected_category
    })
