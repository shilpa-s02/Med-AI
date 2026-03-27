import requests
import base64
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib import messages


# REPLACE THIS with the URL Ngrok gives you in your Kaggle Notebook
KAGGLE_URL = "https://nichelle-clerestoried-nonnasally.ngrok-free.dev/predict"


 


#UPLOAD IMAGE & ANALYZE
def index(request):
    if request.method == "POST" and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # 1. Convert image to Base64
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 2. Send request to Kaggle Flask API
        payload = {
           "prompt": "Identify the medical findings in this image.",

            "image": image_base64
        }
        
        try:
            # MedGemma is large; we give it 90 seconds to respond
            response = requests.post(KAGGLE_URL, json=payload, timeout=90)
            response.raise_for_status()
            result = response.json()
            
            return render(request, 'analyzer/result.html', {
                'analysis': result.get('analysis'),
                'image_base64': image_base64
            })
        except Exception as e:
            return render(request, 'analyzer/index.html', {'error': f"Connection Error: {str(e)}"})

    return render(request, 'analyzer/index.html')




#FRONT END CODE

##HOME PAGE

from django.shortcuts import render

def home(request):
    # This renders your new stylish home page
    return render(request, 'analyzer/home.html')

# def upload_image(request):
#     # Keep your existing upload/analyze logic here
#     # This is Step 2 & 4 in your workflow [cite: 35, 44]
#     return render(request, 'analyzer/index.html')


# DOCTOR SECTION


def doctor(request):
    return render(request,'analyzer/DoctorDashboard.html')


#doctor login

def doctor_login(request):
    
    return render(request, 'analyzer/Doctorlogin.html')

#Doctor Register


def doctor_register(request):
    
        
    return render(request, 'analyzer/DoctorRegister.html', )

def doctordashboard(request):
    return render(request,'analyzer/DoctorDashboard.html')