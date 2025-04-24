# mynewapp/urls.py


from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


#urlpatterns = [
    #path('', views.index, name='index'),
    #path('login/', views.login_view, name='login'),
    #path('logout/', views.logout_view, name='logout'),
    #path('add_category/', views.add_category, name='add_category'),
    #path('add_notebook/', views.add_notebook, name='add_notebook'),
    #path('add_expense/', views.add_expense, name='add_expense'),
    #path('register/', views.register, name='register'),
    #path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    #path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
#]


urlpatterns = [
    #path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('', views.about_page, name='about_page'),

    # Authentication
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registration, name='registration'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(template_name='diary_app/change_password.html'), name='change_password'),



    

    # Category
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),

    # Notebook
    path('notebook/add/', views.add_notebook, name='add_notebook'),
    path('notebook/edit/<int:notebook_id>/', views.edit_notebook, name='edit_notebook'),
    path('notebook/delete/<int:notebook_id>/', views.delete_notebook, name='delete_notebook'),
    #path('notebook/<int:notebook_id>/', views.notebook_detail, name='notebook_detail'),
    path('my-notebooks/',views.my_notebooks,name='my_notebooks'),

    # Expense
    path('expense/add/', views.add_expense, name='add_expense'),
    path('my-expenses/', views.my_expenses_view, name='my_expenses'),
    path('expense/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:expense_id>/', views.delete_expense_view, name='delete_expense'),
    path('expense/category/<int:category_id>/', views.expenses_by_category, name='expenses_by_category'),

    

]



