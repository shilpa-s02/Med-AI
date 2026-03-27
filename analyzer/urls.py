
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # The landing page
    # path('upload/', views.upload_image, name='predict'), # The upload section [cite: 35]
    path('index/',views.index,name='index'),
    path('doctor/',views.doctor_login,name='doctorlogin'),
    path('doctordashboard/',views.doctordashboard,name='doctordashboard'),
    path('doctorregister/',views.doctor_register,name='doctorregister'),
]