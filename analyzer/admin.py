from django.contrib import admin
from .models import Patient, Scan ,DoctorRegisterModel # Import your models here



# Register your models
admin.site.register(Patient)
admin.site.register(Scan)

# If you want to register your doctor model:
admin.site.register(DoctorRegisterModel)


