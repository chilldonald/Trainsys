from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf  import settings


urlpatterns = [
    path('', views.homepage, name="home"),
    path('analytics/', views.analytics, name="analytics"),
    path('scoreboard/', views.scoreboard, name="scoreboard"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logout_view, name="logout"),
    path('new_workout/', views.new_workout, name="new_workout"),
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('workout_detail/<int:workout_id>/', views.workout_detail, name="workout_detail"),
    path('delete_workout/<int:workout_id>/', views.delete_workout, name="delete_workout"),
]   

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)