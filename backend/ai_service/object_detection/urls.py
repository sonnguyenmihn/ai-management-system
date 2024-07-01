from django.urls import path
from . import views


urlpatterns = [
    path('admin_ai_service/', views.admin_ai_service, name = 'admin_ai_service'),
    path('admin_ai_service_delete/', views.admin_ai_service_delete, name='admin_ai_service_delete'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('admin_users_detail/<str:username>/',views.admin_users_detail, name="admin_users_detail"),
    path('admin_user_detail_approve/',views.admin_user_detail_approve, name="admin_user_detail_approve"),
    path('admin_user_detail_delete/',views.admin_user_detail_delete, name="admin_user_detail_delete"),
    path('admin_profit/', views.admin_profit, name='admin_profit'),
    path('user_check/<str:type_>/', views.user_check, name='user_check'),
    # path('user_ai_service/', views.user_ai_service, name='user_ai_service'),
    path('user_delete_service/', views.user_delete_service, name ="user_delete_service"),
    path('user_subscribe/', views.user_subscribe,name="user_subscribe"),
    path('test/',views.test,name="test"),
    # path('user_history/<int:user_id>/', views.user_history, name="user_history"),
    # path('user_services/<int:user_id>', views.user_services, name="user_services"),
    path('user_ai_service_airplane/', views.user_ai_service_airplane, name='user_ai_service_airplane'),
    path('user_ai_service_ship/', views.user_ai_service_ship, name='user_ai_service_ship'),


]