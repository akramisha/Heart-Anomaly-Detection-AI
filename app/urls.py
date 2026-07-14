from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact, name='contact'),
    path('history/',views.history,name='history'),
    path('terms/',views.terms,name='terms',),
    path('register/',views.register,name='register'),
    path('service/',views.service,name='service'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('login/',views.login,name='login',),
    path('Forgotpass/',views.Forgotpass,name='Forgotpass'),
    path('ai/',views.ai,name='ai'),
    path('logout/',views.user_logout,name='logout',),

    path('verify_secret_question/', views.verify_secret_question_view, name='verify_secret_question'),
    path('set_new_password/', views.set_new_password_view, name='set_new_password'),

    # --- New AI System URLs ---
    path('predict/', views.predict, name='predict'),
    path('generate_report/<int:prediction_id>/', views.generate_report, name='generate_report'),
    path('prediction_history/', views.prediction_history, name='prediction_history'),
]
