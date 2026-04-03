
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # The landing page
    # path('upload/', views.upload_image, name='predict'), # The upload section [cite: 35]
    # path('index/',views.index,name='index'),
    path('doctor/',views.doctor_login,name='doctorlogin'),
    path('doctordashboard/',views.doctordashboard,name='doctordashboard'),
    path('doctorregister/',views.doctor_register,name='doctorregister'),
    path('doctornew/',views.doctor,name='doctor'),
    path('doctor_patient/',views.doctor_patient,name='doctor_patient'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('radiology_upload/',views.Radiology_doctor,name='radiology_upload'),
    path('report/<int:scan_id>/', views.scan_report, name='scan_report'),
    path('ai-inference/', views.ai_inference_list, name='ai_inference'),
]