from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index,name="Home"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("handle_signup/", views.handle_signup, name="handle_signup"),
    path("handle_login/", views.handle_login, name="handle_login"),
    path("user_home/", views.user_home, name="user_home"),
    path("logout/",views.logout_view, name="logout"),
    path("equity_search/", views.equity_search, name="equity_search"),
    path("company_search/", views.company_search, name="company_search"),
    path("get_fundamentals/", views.get_fundamentals, name="get_fundamentals"),
    path('portfolio/', views.portfolio, name="portfolio"),
    path('add_portfolio/', views.add_portfolio, name="add_portfolio"),
    path('del_portfolio/', views.del_portfolio, name="del_portfolio"),
    path('news/',views.news, name="news"),
    path('support/', views.support, name="support"),
    path('get_support/', views.get_support, name="get_support"),
    path('change_password/',views.change_password, name="change_password"),
    path('handle_change_password/',views.handle_change_password, name="handle_change_password"),
path('reset_password/',auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
name="reset_password"),
path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"),
name="password_reset_done"),
path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(
template_name="password_reset_confirm.html"),
name="password_reset_confirm"),
path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(
template_name="password_reset_complete.html"), name="password_reset_complete"),



]