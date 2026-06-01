import requests
import base64
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import DoctorRegisterModel,Patient,Scan,PatientScan
from .forms import DoctorRegisterForm,RadiologyUploadForm,PatientForm
# from .models import Patient
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group # Import the User model

# REPLACE THIS with the URL Ngrok gives you in your Kaggle Notebook
KAGGLE_URL = "https://nichelle-clerestoried-nonnasally.ngrok-free.dev/predict"

#FOR STATIC RADIOLOGIST LOGIN
def unified_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # --- STATIC RADIOLOGIST CHECK ---
            # Replace 'shilpa_radio' with your preferred static username
            if user.username == 'Radio_MedAI': 
                return redirect('radiologist_dashboard')
            
            # --- ADMIN CHECK ---
            elif user.is_superuser:
                return redirect('/admin/')
            
            # --- ALL OTHER REGISTERED DOCTORS ---
            else:
                return redirect('doctordashboard')
    else:
        form = AuthenticationForm()
        
    return render(request, 'analyzer/Login.html', {'form': form})

# Model code for the original image upload and AI analysis (without the new doctor assignment logic)
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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')

            # Check if user already exists to avoid IntegrityError
            if User.objects.filter(username=username).exists():
                messages.error(request, "That username is already taken. Please choose another.")
                return render(request, 'analyzer/DoctorRegister.html', {'form': form})

            # 1. Save the Profile to your DoctorRegisterModel
            doctor_profile = form.save()

            # 2. Create the actual Login account with encrypted password
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password) # Encrypts the password for login
            user.save()

            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
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

@login_required



def finalize_diagnosis(request, scan_id):
    # Use get_object_or_404 for better error handling
    scan = get_object_or_404(PatientScan, id=scan_id)
    
    if request.method == 'POST':
        # Save the doctor's clinical notes
        scan.doctor_notes = request.POST.get('notes')
        # Optional: scan.is_reviewed = True 
        scan.save()
        return redirect('doctordashboard')
        
    return render(request, 'analyzer/FinalizeReport.html', {'scan': scan})



#View TOTAL PATIENTs VIEW FOR DOCTOR
def doctor_patient(request):
    # Fetch only patients added by the logged-in doctor
    # If you want them to see ALL patients, keep Patient.objects.all()
    patients = Patient.objects.filter(added_by=request.user).order_by('-id')
    
    return render(request, 'analyzer/Doctor_patient.html', {'patients': patients})

# ADD PATIENT VIEW FOR DOCTOR
def add_patient(request):
    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone') # Capture phone if you added it to the form

        try:
            Patient.objects.create(
                name=name, 
                age=age, 
                gender=gender,
                phone=phone,
                added_by=request.user # This links the patient to the logged-in doctor
            )
            messages.success(request, f"Patient {name} registered successfully!")
        except Exception as e:
            messages.error(request, f"Error adding patient: {e}")

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

    
# View to display the scan report with AI analysis results

def scan_report(request, scan_id):
    # 1. FIX: Change 'Scan' to 'PatientScan' to match your models.py
    scan = get_object_or_404(PatientScan, id=scan_id)
    
    # 2. Convert image to base64
    image_base64 = ""
    if scan.image and hasattr(scan.image, 'path'):
        with open(scan.image.path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 3. FIX: Use 'prediction' instead of 'analysis' to match your model fields
    context = {
        'analysis': scan.prediction,  # Your model uses 'prediction'
        'image_base64': image_base64,
        'scan': scan 
    }
    
    return render(request, 'analyzer/result.html', context)


#AI INFERENCE

def ai_inference_list(request):
    # Fetch all scans and their associated patient data
    scans = Scan.objects.all().select_related('patient').order_by('-created_at')
    
    return render(request, 'analyzer/ai_inference.html', {'scans': scans})



# def radiologist_dashboard(request):
#     context = {
#         'patients': Patient.objects.all(),
#         'recent_uploads': PatientScan.objects.filter(uploaded_by=request.user).order_by('-created_at')[:10]
#     }
#     return render(request, 'analyzer/Radiologist/Radiologist_dashboard.html', context)

#Radiologist Register

def radiologist_register(request):
    return render(request, 'analyzer/RadiologistRegister.html')



#  --------------NEW FINALIZED VERSION WITH MEDGEMMA INTEGRATION (TEXT-BASED OUTPUT)----------------




import base64
import requests
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Patient, PatientScan
from django.shortcuts import render
from django.utils import timezone

# This is your new, fully integrated radiologist dashboard view with the fixed "Today's Scans" count and the doctor assignment logic in the process_analysis function.

def radiologist_dashboard(request):
    patients = Patient.objects.all()
    
    # 1. Grab only your doctor accounts (excluding staff admins)
    doctor_list = User.objects.filter(is_active=True).exclude(
        username__in=['Radio_MedAI', 'shilpasnair', 'shilpasankaran']
    )
    
    # 2. Real-time Live Feed (shows the last 10 scans overall)
    recent_uploads = PatientScan.objects.all().order_by('-created_at')[:10]
    
    # 3. FIXED: Calculate the exact mathematical count for TODAY only
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_scans_count = PatientScan.objects.filter(created_at__gte=today_start).count()

    context = {
        'patients': patients,
        'doctors': doctor_list,
        'recent_uploads': recent_uploads,
        'todays_count': todays_scans_count, # Use this new explicit variable!
    }
    return render(request, 'analyzer/Radiologist/Radiologist_dashboard.html', context)


# This is the new process_analysis function that captures the doctor selection from the radiologist dashboard form and assigns the AI-generated scan directly to that doctor. It also includes robust error handling for the AI response and database operations.
# def process_analysis(request):
#     if request.method != 'POST':
#         return redirect('radiologist_dashboard')
        
#     patient_id = request.POST.get('patient_id')
#     doctor_id = request.POST.get('doctor_id')  # 1. Capture the targeted doctor from the form
#     modality = request.POST.get('modality')
#     image = request.FILES.get('image')
    
#     if not image or not patient_id:
#         messages.error(request, "Please select an active patient and upload a valid scan image.")
#         return redirect('radiologist_dashboard')

#     patient_obj = get_object_or_404(Patient, id=patient_id)
    
#     # CONVERT IMAGE TO BASE64 STRING FOR KAGGLE
#     try:
#         img_bytes = image.read()
#         image.seek(0)  # Reset pointer head so Django can still save the physical file later
#         image_b64 = base64.b64encode(img_bytes).decode('utf-8')
#     except Exception as e:
#         messages.error(request, f"Failed to process image encoding: {e}")
#         return redirect('radiologist_dashboard')

#     # Establish fallbacks
#     prediction = "Pending Evaluation"
#     confidence = 0.0
    
#     AI_URL = "https://nichelle-clerestoried-nonnasally.ngrok-free.dev/predict"
    
#     # SEND JSON POST REQUEST (Matching Kaggle's expected structure)
#     try:
#         json_payload = {"image": image_b64}
#         response = requests.post(AI_URL, json=json_payload, timeout=45) 
        
#         if response.status_code == 200:
#             try:
#                 ai_data = response.json()
#                 analysis_text = ai_data.get('analysis', '')
#                 prediction = analysis_text if analysis_text else "Analysis complete (No text returned)"
#                 confidence = 100.0  
                
#             except (ValueError, TypeError):
#                 prediction = "Data Parsing Mismatch"
#                 messages.warning(request, "AI responded, but returned an unreadable payload format.")
#         else:
#             prediction = f"AI Error ({response.status_code})"
#             messages.warning(request, f"AI Gateway returned structural code {response.status_code}.")
            
#     except requests.exceptions.RequestException as e:
#         prediction = "AI Engine Offline"
#         messages.error(request, f"Could not bind connectivity to Kaggle server: {e}")

#     # 2. DYNAMIC ROUTING LOGIC BASED ON YOUR CHOICE
#     try:
#         # Priority A: Use the explicit doctor selected from your radiologist form dropdown
#         if doctor_id:
#             target_doctor = get_object_or_404(User, id=doctor_id)
#         # Priority B: Fall back to whoever created the patient profile originally
#         elif patient_obj.added_by:
#             target_doctor = patient_obj.added_by
#         # Priority C: Ultimate fallback to the current user session agent
#         else:
#             target_doctor = request.user
        
#         PatientScan.objects.create(
#             patient_name=patient_obj.name,
#             image=image,
#             modality=modality,
#             prediction=prediction,     
#             confidence=confidence,
#             uploaded_by=request.user,
#             assigned_doctor=target_doctor,  # Sends directly to the verified doctor's workspace
#             is_submitted=True
#         )
#         PatientScan.save()
#         messages.success(
#             request, 
#             f"Diagnostic file for {patient_obj.name} processed by MedGemma and sent directly to Dr. {target_doctor.last_name or target_doctor.username}."
#         )
        
#     except Exception as e:
#         messages.error(request, f"Critical Core System Database Write Failure: {e}")

#     return redirect('radiologist_dashboard')


def process_analysis(request):
    if request.method != 'POST':
        return redirect('radiologist_dashboard')
        
    patient_id = request.POST.get('patient_id')
    doctor_id = request.POST.get('doctor_id')  # 1. Capture the targeted doctor from the form
    modality = request.POST.get('modality')
    image = request.FILES.get('image')
    
    if not image or not patient_id:
        messages.error(request, "Please select an active patient and upload a valid scan image.")
        return redirect('radiologist_dashboard')

    patient_obj = get_object_or_404(Patient, id=patient_id)
    
    # CONVERT IMAGE TO BASE64 STRING FOR KAGGLE
    try:
        img_bytes = image.read()
        image.seek(0)  # Reset pointer head so Django can still save the physical file later
        image_b64 = base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        messages.error(request, f"Failed to process image encoding: {e}")
        return redirect('radiologist_dashboard')

    # Establish fallbacks
    prediction = "Pending Evaluation"
    confidence = 0.0
    
    AI_URL = "https://nichelle-clerestoried-nonnasally.ngrok-free.dev/predict"
    
    # SEND JSON POST REQUEST (Matching Kaggle's expected structure)
    try:
        json_payload = {"image": image_b64}
        response = requests.post(AI_URL, json=json_payload, timeout=45) 
        
        if response.status_code == 200:
            try:
                ai_data = response.json()
                analysis_text = ai_data.get('analysis', '')
                prediction = analysis_text if analysis_text else "Analysis complete (No text returned)"
                confidence = 100.0  
                
            except (ValueError, TypeError):
                prediction = "Data Parsing Mismatch"
                messages.warning(request, "AI responded, but returned an unreadable payload format.")
        else:
            prediction = f"AI Error ({response.status_code})"
            messages.warning(request, f"AI Gateway returned structural code {response.status_code}.")
            
    except requests.exceptions.RequestException as e:
        prediction = "AI Engine Offline"
        messages.error(request, f"Could not bind connectivity to Kaggle server: {e}")

    # 2. DYNAMIC ROUTING LOGIC BASED ON YOUR CHOICE
    try:
        # Priority A: Use the explicit doctor selected from your radiologist form dropdown
        if doctor_id:
            target_doctor = get_object_or_404(User, id=doctor_id)
        # Priority B: Fall back to whoever created the patient profile originally
        elif patient_obj.added_by:
            target_doctor = patient_obj.added_by
        # Priority C: Ultimate fallback to the current user session agent
        else:
            target_doctor = request.user
        
        # This saves automatically to the DB! No additional save call needed.
        PatientScan.objects.create(
            patient_name=patient_obj.name,
            image=image,
            modality=modality,
            prediction=prediction,     
            confidence=confidence,
            uploaded_by=request.user,
            assigned_doctor=target_doctor,  # Sends directly to the verified doctor's workspace
            is_submitted=True
        )
        
        messages.success(
            request, 
            f"Diagnostic file for {patient_obj.name} processed by MedGemma and sent directly to Dr. {target_doctor.last_name or target_doctor.username}."
        )
        
    except Exception as e:
        messages.error(request, f"Critical Core System Database Write Failure: {e}")

    return redirect('radiologist_dashboard')

# Doctor dashboard for see the result send by Radiologist and add doctor notes and finalize the report. This view will also show the count of pending scans that are assigned to this doctor and marked as submitted but not yet finalized (i.e., doctor_notes is still null).
def doctordashboard(request):
    # Fetch scans assigned to this doctor that are marked submitted
    recent_scans = PatientScan.objects.filter(
        assigned_doctor=request.user, 
        is_submitted=True
    ).order_by('-created_at')

    context = {
        'total_patients': Patient.objects.filter(added_by=request.user).count(),
        'total_scans': PatientScan.objects.filter(assigned_doctor=request.user).count(),
        'recent_scans': recent_scans,
        'doctor_name': request.user.username,
        # FIX: Count scans that are submitted. (If you add a doctor notes field later for completed items, 
        # you can filter out annotated scans by changing this to: filter(doctor_notes__isnull=True))
        'pending_count': recent_scans.count()  
    }
    
    return render(request, 'analyzer/DoctorDashboard.html', context)