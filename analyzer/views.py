import requests
import base64
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import DoctorRegisterModel,Patient,Scan
from .forms import DoctorRegisterForm,RadiologyUploadForm,PatientForm
from .models import Patient
from django.contrib.auth.decorators import login_required


# REPLACE THIS with the URL Ngrok gives you in your Kaggle Notebook
KAGGLE_URL = "https://nichelle-clerestoried-nonnasally.ngrok-free.dev/predict"

# #UPLOAD IMAGE & ANALYZE
# def index(request):
#     if request.method == "POST" and request.FILES.get('image'):
#         image_file = request.FILES['image']
        
#         # 1. Convert image to Base64
#         image_data = image_file.read()
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
        
#         # 2. Send request to Kaggle Flask API
#         payload = {
#            "prompt": "Identify the medical findings in this image.",

#             "image": image_base64
#         }
        
#         try:
#             # MedGemma is large; we give it 90 seconds to respond
#             response = requests.post(KAGGLE_URL, json=payload, timeout=90)
#             response.raise_for_status()
#             result = response.json()
            
#             return render(request, 'analyzer/result.html', {
#                 'analysis': result.get('analysis'),
#                 'image_base64': image_base64
#             })
#         except Exception as e:
#             return render(request, 'analyzer/index.html', {'error': f"Connection Error: {str(e)}"})

#     return render(request, 'analyzer/index.html')

#FRONT END CODE

##HOME PAGE

def home(request):
    # This renders your new stylish home page
    return render(request, 'analyzer/home.html')

# DOCTOR SECTION
def doctor(request):
    return render(request,'analyzer/DoctorDashboard.html')

#  1. Doctor Registration View
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('doctorlogin')
        else:
            # If form is invalid, we pass errors to the template via messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DoctorRegisterForm()
    return render(request, 'analyzer/DoctorRegister.html', {'form': form})

# 2. Doctor Login View
def doctor_login(request):
    if request.method == 'POST':
        email_id = request.POST.get('email')
        pass_word = request.POST.get('password')

        try:
            user = DoctorRegisterModel.objects.get(email=email_id)
            if user.password == pass_word:
                request.session['doctor_id'] = user.id
                messages.success(request, f"Welcome back, Dr")
                return redirect('doctordashboard')
            else:
                messages.error(request, "Invalid password.")
        except DoctorRegisterModel.DoesNotExist:
            messages.error(request, "This email is not registered.")
            
    return render(request, 'analyzer/Doctorlogin.html')

# Doctor Dashboard
@login_required
def doctordashboard(request):
    total_patients = Patient.objects.count()
    total_scans = Scan.objects.count()
    recent_scans = Scan.objects.select_related('patient').order_by('-created_at')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_scans': total_scans,
        'recent_scans': recent_scans,
        'doctor_name': request.user.username 
    }
    
    # ADD 'context' HERE ↓
    return render(request, 'analyzer/DoctorDashboard.html', context)


# patient management for Doctor
def doctor_patient(request):
    # Fetch all patients so the table isn't empty!
    patients = Patient.objects.all().order_by('-id')
    return render(request,'analyzer/Doctor_patient.html',{'patients': patients})

# def add_patient(request):
def add_patient(request):
    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')

        try:
            Patient.objects.create(name=name, age=age, gender=gender)
            messages.success(request, f"Patient {name} registered successfully!")
        except Exception as e:
            messages.error(request, f"Error adding patient: {e}")

        # This triggers doctor_patient() again, which now fetches the new list
        return redirect('doctor_patient')
    
    return redirect('doctor_patient')
    

# Radiology Upload For Doctor

def Radiology_doctor(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        selected_modality = request.POST.get('scan_type') 
        uploaded_file = request.FILES.get('medical_image')

        if patient_id and uploaded_file:
            try:
                patient = Patient.objects.get(id=patient_id)
                
                # 1. Prepare Image for AI (Convert to Base64)
                image_data = uploaded_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                uploaded_file.seek(0) # Reset file pointer so Django can save it later

                # 2. Send request to Kaggle Flask API
                payload = {
                    "prompt": f"Identify the medical findings in this {selected_modality} image.",
                    "image": image_base64
                }
                
                try:
                    # MedGemma analysis
                    response = requests.post(KAGGLE_URL, json=payload, timeout=90)
                    response.raise_for_status()
                    result = response.json()
                    ai_analysis = result.get('analysis', "No analysis returned from AI.")
                except Exception as e:
                    ai_analysis = f"AI Connection Error: {str(e)}"

                # 3. Save to Database with REAL AI results
                new_scan = Scan.objects.create(
                    patient=patient,
                    modality=selected_modality,
                    image=uploaded_file,
                    analysis=ai_analysis # This replaces "Analysis in progress..."
                )
                
                # Redirect directly to the report page
                return redirect('scan_report', scan_id=new_scan.id)
                
            except Patient.DoesNotExist:
                return render(request, 'analyzer/radiology_upload.html', {'error': 'Patient not found'})

    patients = Patient.objects.all().order_by('name')
    return render(request, 'analyzer/radiology_upload.html', {'patients': patients})

    
#Scan report
def scan_report(request, scan_id):
    
    # 1. Get the specific scan
    scan = get_object_or_404(Scan, id=scan_id)
    
    # 2. Convert image to base64
    # Safety check: ensures the file exists on the disk before opening
    image_base64 = ""
    if scan.image and hasattr(scan.image, 'path'):
        with open(scan.image.path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 3. Pass to template
    context = {
        'analysis': scan.analysis,
        'image_base64': image_base64,
        'scan': scan 
    }
    
    return render(request, 'analyzer/result.html', context)


#AI INFERENCE

def ai_inference_list(request):
    # Fetch all scans and their associated patient data
    scans = Scan.objects.all().select_related('patient').order_by('-created_at')
    
    return render(request, 'analyzer/ai_inference.html', {'scans': scans})




   