# from django.db import models

# # We only need ONE model for the Doctor. 
# # Registration SAVES to this; Login CHECKS against this.




# class DoctorRegisterModel(models.Model):
#     username = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     license_number = models.CharField(max_length=100, unique=True)
#     password = models.CharField(max_length=100)
#     # Adding a role helps separate General Doctors from Radiologists
#     role = models.CharField(max_length=50, choices=[('Doctor', 'Doctor'), ('Radiologist', 'Radiologist')], default='Doctor')

#     def __str__(self):
#         return f"Dr. {self.username} ({self.license_number})"

from django.db import models
from django.utils import timezone

class DoctorRegisterModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    license_number = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255) # Use longer length for hashed passwords

    def __str__(self):
        return f"Dr. {self.username} ({self.license_number})"
    


class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # Basic Info
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Optional contact info
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    @property
    def last_visit(self):
        """Used for the 'Last Visit' column in your dashboard table"""
        last_scan = self.scans.order_by('-created_at').first()
        return last_scan.created_at if last_scan else self.created_at


class Scan(models.Model):
    MODALITY_CHOICES = [
        ('X-Ray', 'X-Ray'),
        ('MRI', 'MRI'),
        ('CT', 'CT Scan'),
    ]

    # Relationship: One Patient can have many Scans
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='scans'
    )
    
    # File Storage
    image = models.ImageField(upload_to='radiology_scans/%Y/%m/%d/')
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default='X-Ray')
    
    # The AI output from MedGemma
    analysis = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.modality} - {self.patient.name} ({self.created_at.date()})"