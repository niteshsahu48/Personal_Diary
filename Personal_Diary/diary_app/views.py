from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Notebook, Expense, RegisterUser
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
import random
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt




User = get_user_model()

@csrf_exempt
def about_page(request):
    return render(request, 'diary_app/about.html')  


@csrf_exempt
def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm_password = request.POST.get('confirm_password')

        # Username check
        if RegisterUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('registration')

        # Email check
        if RegisterUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('registration')

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('registration')

        # Create user and login
        hashed_password = make_password(password)
        user = RegisterUser(username=username, password=hashed_password, email=email)
        user.save()

        login(request, user)  
        messages.success(request, "Registration successful. You are now logged in.")
        return redirect('index') 

    return render(request, 'diary_app/register.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('login_password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid email or password")
            return render(request, 'diary_app/login.html')

        if not request.session.session_key:
            request.session.create()
        
        login(request, user)
        return redirect('index')
    
    return render(request, 'diary_app/login.html')


@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('login_view')

@csrf_exempt
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


@csrf_exempt
@login_required
def profile(request):
    user = request.user  
    return render(request, 'diary_app/profile.html')



@csrf_exempt
@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == 'POST':
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')

        user.username = username
        user.last_name = last_name
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'diary_app/edit_profile.html', {'user': user})



@csrf_exempt
def send_otp_email(user,otp):
    send_mail(
        subject='Your OTP for Password Reset',
        message=f'Dear {user.username},\n\n'
            f'🛡️ Your OTP for password reset is: {otp}\n\n'
            'Please note:⏳ This OTP is valid for only 5 minutes.\n'
            'If you did not request a password reset, please ignore this email.\n\n'
            'Thank you,\n'
            'My Personal Diary Team',
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )


def generate_otp():
    return str(random.randint(100000, 999999))

@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = RegisterUser.objects.get(email=email)
            otp = generate_otp()  
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(user, otp)  
            request.session['reset_email'] = email
            messages.success(request, "OTP sent to your email!")
            return redirect('verify_otp')

        except RegisterUser.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    
    return render(request, 'diary_app/forgot_password.html')

@csrf_exempt
@login_required
def forgot_password_auto(request):
    user = request.user
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()
    send_otp_email(user, otp)
    request.session['reset_email'] = user.email
    messages.success(request, "OTP sent to your email!")
    return redirect('verify_otp')


@csrf_exempt
def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = RegisterUser.objects.get(email=email)
            if user.otp != otp:
                messages.error(request, "Invalid OTP.")
            elif (timezone.now() - user.otp_created_at).total_seconds() > 300:
                user.otp = None
                user.otp_created_at = None
                user.save()
                messages.error(request, "OTP expired. Please try again.")
                return redirect('forgot_password')
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif len(new_password) < 8 or not any(c.isdigit() for c in new_password) or not any(c.isupper() for c in new_password):
                messages.error(request, "Password must be at least 8 characters, contain a number and an uppercase letter.")

            elif check_password(new_password, user.password):
                messages.error(request, "New password cannot be the same as the old password.")

            else:
                user.set_password(new_password)
                user.otp = None
                user.otp_created_at = None
                user.save()
                messages.success(request, "Password reset successfully!")
                return redirect('login_view')
        except RegisterUser.DoesNotExist:
            messages.error(request, "Something went wrong.")
    return render(request, 'diary_app/verify_otp.html')

@csrf_exempt
@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            exists = Category.objects.filter(
                category_name__iexact=category_name.strip(), 
                user=request.user
            ).exists()

            if exists:
                messages.warning(request, f"Category '{category_name}' already exists.")
            else:
                Category.objects.create(
                    category_name=category_name.strip(), 
                    user=request.user
                )
                messages.success(request, f"Category '{category_name}' added successfully.")
                return redirect('add_category')

    categories = Category.objects.filter(user=request.user).order_by('category_name')
    return render(request, 'diary_app/add_category.html', {'categories': categories})



@csrf_exempt
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            category.category_name = category_name
            category.save()
            return redirect('add_category')

    return render(request, 'diary_app/edit_category.html', {'category': category})


@csrf_exempt
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == 'POST':
        category.delete()
        return redirect('add_category')

    return render(request, 'diary_app/delete_category.html', {'category': category})

@csrf_exempt
@login_required
def add_notebook(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Notebook.objects.create(user=request.user, title=title, content=content)
        return redirect('index')
    return render(request, 'diary_app/add_notebook.html')

@csrf_exempt
@login_required
def edit_notebook(request, notebook_id):
    notebook = Notebook.objects.get(id=notebook_id, user=request.user)
    if request.method == 'POST':
        notebook.title = request.POST.get('title')
        notebook.content = request.POST.get('content')
        notebook.save()
        return redirect('index')
    return render(request, 'diary_app/edit_notebook.html', {'notebook': notebook})


@csrf_exempt
@login_required
def delete_notebook(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id, user=request.user)
    notebook.delete()
    return redirect('my_notebooks')



@csrf_exempt
@login_required
def add_expense(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        add_note = request.POST.get('add_note')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        
        Expense.objects.create(user=request.user, amount=amount, add_note=add_note, category=category)
        messages.success(request, "Expense added successfully!")
        return redirect('add_expense')
    
    return render(request, 'diary_app/add_expense.html', {'categories': categories})


@csrf_exempt
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


@csrf_exempt
@login_required
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        expense.delete()
        return redirect('my_expenses')

    return render(request, 'diary_app/confirm_delete.html', {'expense': expense})



@csrf_exempt
@login_required
def expenses_by_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
    expenses = Expense.objects.filter(user=request.user, category=category)
    return render(request, 'diary_app/expenses_by_category.html', {
        'expenses': expenses,
        'category': category,
    })


@csrf_exempt
@login_required
def my_notebooks(request):
    notebooks = Notebook.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'diary_app/my_notebooks.html', {'notebooks': notebooks})



@csrf_exempt
@login_required
def my_expenses_view(request):
    categories = Category.objects.filter(user=request.user)
    selected_category = request.GET.get('category')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    expenses = Expense.objects.filter(user=request.user)

    if selected_category:
        expenses = expenses.filter(category__id=selected_category)

    if from_date:
        expenses = expenses.filter(created_at__date__gte=from_date)
    if to_date:
        expenses = expenses.filter(created_at__date__lte=to_date)

    expenses = expenses.order_by('-created_at')
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'diary_app/my_expenses.html', {
        'expenses': expenses,
        'categories': categories,
        'selected_category': selected_category,
        'total_amount': total_amount,
        'from_date': from_date,
        'to_date': to_date
    })


@csrf_exempt
@login_required
def read_notebook(request, id):
    notebook = get_object_or_404(Notebook, id=id, user=request.user)
    return render(request, 'diary_app/read_notebook.html', {'notebook': notebook})




@csrf_exempt
def some_view(request):
    prev_url = request.META.get('HTTP_REFERER', '/')
    return render(request, 'diary_app/index.html', {'prev_url': prev_url})






     


