# from django import migrations, models
from django import forms
from django.contrib.auth.models import User

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



# class RadiologistRegisterForm(forms.ModelForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
#     # Field from the Profile model
#     employee_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EMP-123'}))

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match!")
#         return cleaned_data