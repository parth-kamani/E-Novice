from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.template.defaulttags import url
from django.urls import path, re_path, reverse_lazy

from F20Lab04T2 import settings
from myapp import views
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static

from myapp.views import index, detail

app_name = 'myapp'

urlpatterns = [
    # path(r'', views.index, name='index'),
    path(r'', index.as_view(), name='index'),
    path(r'about/', views.about, name='about'),
    # re_path(r'(?P<topic_id>[0-9]+)/$', views.detail, name='detail'),
    path(r'<int:topic_id>/', detail.as_view(), name='detail'),
    path(r'findcourses/', views.findcourses, name='findcourses'),
    path(r'place_order/', views.place_order, name='place_order'),
    path(r'review/', views.review, name='review'),
    path(r'login/', views.user_login, name='user_login'),
    path(r'register/', views.register, name='user_reg'),
    path(r'logout/', views.user_logout, name='user_logout'),
    path(r'myaccount/', views.myaccount, name='myaccount'),
    path(r'myorders/', views.myorders, name='myorders'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="myapp/reset_password.html",
                                                                 email_template_name='myapp/password_reset_email.html',
                                                                 success_url=reverse_lazy('myapp:password_reset_done')),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="myapp/password_reset_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="myapp/password_reset_form.html",
                                                     success_url=reverse_lazy('myapp:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="myapp/password_reset_done.html"),
         name='password_reset_complete')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
