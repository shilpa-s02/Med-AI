# from django.db import models

# # We only need ONE model for the Doctor. 
# # Registration SAVES to this; Login CHECKS against this.



from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

#DOCTOR REGISTER
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

    name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # --- ADD THIS LINE ---
    # null=True allows existing patients to remain in the database without crashing
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    @property
    def last_visit(self):
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
    


class PatientScan(models.Model):
    patient_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='scans/')
    modality = models.CharField(max_length=20) # X-Ray, MRI, etc.
    
    # AI Results
    prediction = models.CharField(max_length=255, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    heatmap_image = models.ImageField(upload_to='heatmaps/', blank=True, null=True)
    
    # Workflow tracking
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='radiology_uploads')
    assigned_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='doctor_reviews')
    is_submitted = models.BooleanField(default=False) # True when Radiologist clicks "Submit"
    doctor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.prediction}"