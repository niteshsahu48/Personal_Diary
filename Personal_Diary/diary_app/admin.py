from django.contrib import admin
from .models import RegisterUser, Category, Notebook, Expense


@admin.register(RegisterUser)
class RegisterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'user')
    search_fields = ('category_name', 'user__email')
    list_filter = ('user',)


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__email')
    list_filter = ('user', 'created_at')
    ordering = ('-created_at',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'user', 'created_at', 'add_note')
    search_fields = ('add_note', 'user__email', 'category__category_name')
    list_filter = ('category', 'user', 'created_at')
    ordering = ('-created_at',)
