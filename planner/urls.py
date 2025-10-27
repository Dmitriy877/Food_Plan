from django.urls import path

from planner import views

urlpatterns = [
    path('order/', views.OrderView.as_view(), name='order'),
    path('order/calculate/', views.CalculateSubscription.as_view(), name='order_calculate'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/upload-avatar/', views.UploadAvatarView.as_view(), name='upload_avatar'),
    path('profile/menu/regenerate', views.RegenerateMenuView.as_view(), name='regenerate_menu'),
    path('dish/<int:pk>/', views.DishDetailView.as_view(), name='dish_detail'),
]
