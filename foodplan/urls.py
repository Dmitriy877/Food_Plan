from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from planner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('payments/', include('payments.urls')),
    path('', render, kwargs={'template_name': 'index.html'}, name='index'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('order/calculate/', views.CalculateSubscription.as_view(), name='order_calculate'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/upload-avatar', views.UploadAvatarView.as_view(), name='upload_avatar'),
    path('card/', views.card, name='card'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
