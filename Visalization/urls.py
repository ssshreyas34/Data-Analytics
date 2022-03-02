from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as v1
urlpatterns = [
    path('',views.home,name="home"),
    path('login/',views.login_form,name='login_form'),
    path('dataset/',views.load,name='load'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout_view,name='logout'),
    path('password_reset/', v1.PasswordResetView.as_view(template_name="Visalization/password_reset.html"),name="reset_password"),
    path('password_reset_done',v1.PasswordResetDoneView.as_view(template_name='Visalization/password_reset_done.html'),name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/',v1.PasswordResetConfirmView.as_view(template_name="Visalization/password_reset_confirm.html"),name="password_reset_confirm"),
    path('password_reset_complete/', v1.PasswordResetCompleteView.as_view(template_name="Visalization/password_reset_complete.html"),name="password_reset_complete"),

    # path('dashboard-line/',views.line_chart,name='line'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)