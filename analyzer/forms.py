

from django import forms
from .models import DoctorRegisterModel
from .models import Patient, Scan

class DoctorRegisterForm(forms.ModelForm):
    # This must match the 'name' attribute in your HTML: name="confirmpassword"
    confirmpassword = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = DoctorRegisterModel
        fields = ['username', 'email', 'license_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirmpassword")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data
    

from .models import Patient, Scan

class PatientForm(forms.ModelForm):
    """Form to register a new patient via the Modal on the Dashboard"""
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Full Name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Age'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Email Address'
            }),
        }

class RadiologyUploadForm(forms.ModelForm):
    """Form to handle Radiology Upload and AI Inference"""
    class Meta:
        model = Scan
        fields = ['patient', 'modality', 'image']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select shadow-sm'
            }),
            # RadioSelect is used to match your X-Ray/MRI/CT toggle buttons
            'modality': forms.RadioSelect(attrs={
                'class': 'btn-check'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control', 
                'id': 'fileInput',
                'hidden': 'True' # Hidden because we use the custom Dropzone UI
            }),
        }