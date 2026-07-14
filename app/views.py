import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import UserRegistrationForm, ProfileEditForm, CustomPasswordChangeForm, SecretQuestionForm, ContactForm, ReplyForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
import numpy as np
from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.core.files.storage import default_storage
from tensorflow.keras.models import load_model
from keras.preprocessing import image
from .models import PredictionResult, Profile, Contact 


ML_MODELS_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
model_path = os.path.join(ML_MODELS_DIR, "best_model.keras")

model = None
if os.path.exists(model_path):
  try:
    model = load_model(model_path)
    print(f"✅ Model loaded successfully from: {model_path}")
  except Exception as e:
    print(f"❌ Error loading model from {model_path}: {e}")
else:
  print(f"❌ Error: Model file not found at {model_path}!")

# Define class labels
class_labels = {
  0: "History of MI",
  1: "Myocardial Infarction Patients",
  2: "Normal",
  3: "Abnormal"
}


def preprocess_image(img_path):
  img = image.load_img(img_path, target_size=(224, 224))
  img_array = image.img_to_array(img)
  img_array = np.expand_dims(img_array, axis=0)
  img_array /= 255.0  
  return img_array

# --- Core Views ---
def index(request):
  return render(request,'index.html')

def about(request):
  return render(request,'about.html')

def contact(request):
  if request.method == 'POST':
      form = ContactForm(request.POST)
      if form.is_valid():
          try:
              contact_instance = form.save(commit=False)
              contact_instance.date = now().date()
              contact_instance.save()
              return JsonResponse({'success': True, 'message': 'Your message has been sent successfully!'})
          except Exception as e:
              print(f"Error saving contact message: {e}")
              return JsonResponse({'success': False, 'message': 'There was an error sending your message. Please try again.'})
      else:
          print(f"Form validation errors: {form.errors}")
          return JsonResponse({'success': False, 'message': 'Invalid form data. Please check your input.', 'errors': form.errors})
  return render(request, 'contact.html')

def terms(request):
  return render(request, 'terms.html')

def service(request):
  return render(request, 'service.html')

def Forgotpass(request):
    secret_question = None
    email = ''
    show_answer_field = False

    if request.method == 'POST':
        email = request.POST.get('email')
        raw_answer = request.POST.get('secret_answer')
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            secret_question = profile.secret_question
            email = user.email

            if not raw_answer:
                show_answer_field = True
            else:
                if profile.check_secret_answer(raw_answer):
                    request.session['reset_user_id'] = user.id
                    request.session['secret_question_verified'] = True
                    messages.success(request, "Verified. You can now reset your password.")
                    return redirect('set_new_password') 
                else:
                    show_answer_field = True
                    messages.error(request, "Incorrect answer. Try again.")
        except (User.DoesNotExist, Profile.DoesNotExist):
            messages.error(request, "No account found for this email.")

    return render(request, 'forgotpass.html', {
        'email': email,
        'secret_question': secret_question,
        'show_answer_field': show_answer_field,
    })

def history(request):
  return render(request,'history.html')

def login(request):
  if request.GET.get('next') == "/profile/":
      messages.error(request, "Please login or register to access your profile.")
  elif request.GET.get('next') == "/ai/":
      messages.error(request, "Please login or register to access your AI-Modal.")

  if request.method == 'POST':
      email = request.POST.get('email')
      password = request.POST.get('password')

      try:
          user = User.objects.get(email=email)
      except User.DoesNotExist:
          messages.error(request, "No account found with this email.")
          return render(request, 'login.html')

      user_auth = authenticate(request, username=user.username, password=password)

      if user_auth is not None:
          auth_login(request, user_auth)
          return redirect('index')
      else:
          messages.error(request, "Incorrect password. Please try again.")
          return render(request, 'login.html')

  return render(request, 'login.html')

@login_required
def profile(request):
  profile_form = ProfileEditForm(instance=request.user.profile)
  password_form = CustomPasswordChangeForm(user=request.user)
  context = {
      'user': request.user,
      'profile_form': profile_form,
      'password_form': password_form,
      'active_tab': 'profile'
  }
  return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        # Debug: Print form data and errors
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        print("Form is valid:", profile_form.is_valid())
        print("Form errors:", profile_form.errors)
        
        if profile_form.is_valid():
            try:
                profile_form.save()
                messages.success(request, 'Your profile was successfully updated!')
                # Stay on the same page instead of redirecting
                return render(request, 'edit_profile.html', {
                    'profile_form': ProfileEditForm(instance=profile),
                    'success': True
                })
            except Exception as e:
                print(f"Error saving profile: {e}")
                messages.error(request, f'An error occurred while saving your profile: {str(e)}')
        else:
            # Add specific error messages for each field
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
            
            # If there are non-field errors
            if profile_form.non_field_errors():
                for error in profile_form.non_field_errors():
                    messages.error(request, error)
    else:
        profile_form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'profile_form': profile_form
    })

def register(request):
  if request.method == 'POST':
      form = UserRegistrationForm(request.POST, request.FILES)
      if form.is_valid():
          try:
              user = form.save()
              messages.success(request, 'Account created successfully! Please log in.')
              print("DEBUG: Form saved and success message set. Attempting redirect to login.") # Debug print
              return redirect('login')
          except Exception as e:
              print(f"DEBUG: An error occurred after form save: {e}") # Debug print
              messages.error(request, f'An error occurred while creating your account: {str(e)}')
      else:
          print(f"DEBUG: Form is not valid. Errors: {form.errors}") # Debug print
          messages.error(request, 'Please correct the errors below.')
  else:
      form = UserRegistrationForm()
  return render(request, 'register.html', {'form': form})

@login_required
def change_password(request):
  if request.method == 'POST':
      form = CustomPasswordChangeForm(user=request.user, data=request.POST)
      if form.is_valid():
          user = form.save()
          update_session_auth_hash(request, user)
          messages.success(request, 'Your password was successfully updated!')
          return redirect('profile')
      else:
          messages.error(request, 'Please correct the errors below.')
  else:
      form = CustomPasswordChangeForm(user=request.user)
  context = {
      'form': form,
  }
  return render(request, 'change_password.html', context)

def user_logout(request):
  auth_logout(request)
  messages.success(request, "You have been successfully logged out.")
  return render(request, 'logout.html')


def verify_secret_question_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Password reset flow interrupted. Please start again.")
        return redirect('verify_email')
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, "User or profile not found. Please start again.")
        return redirect('verify_email')
    if not profile.secret_question or not profile.secret_question.strip():
        messages.error(request, "No secret question set for this account. Please contact support.")
        return redirect('verify_email')
    if request.method == 'POST':
        form = SecretQuestionForm(request.POST)
        if form.is_valid():
            raw_answer = form.cleaned_data['secret_answer']
            if profile.check_secret_answer(raw_answer):
                request.session['secret_question_verified'] = True
                messages.success(request, "Secret question verified. You can now set your new password.")
                return redirect('set_new_password')
            else:
                messages.error(request, "Incorrect secret answer.")
        else:
            messages.error(request, "Please enter your secret answer.")
    else:
        form = SecretQuestionForm()
    return render(request, 'secret_question_verify.html', {
        'secret_question': profile.secret_question,
        'form': form
    })

def set_new_password_view(request):
    user_id = request.session.get('reset_user_id')
    verified = request.session.get('secret_question_verified')
    if not user_id or not verified:
        messages.error(request, "Unauthorized access.")
        return redirect('forgot')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('forgot')
    if request.method == 'POST':
        p1 = request.POST.get('password')
        p2 = request.POST.get('password2')
        if p1 != p2:
            messages.error(request, "Passwords don't match.")
        else:
            user.password = make_password(p1)
            user.save()
            del request.session['reset_user_id']
            del request.session['secret_question_verified']
            messages.success(request, "Password reset successful. Login now.")
            return redirect('login')
    return render(request, 'reset_password.html', {'user_email': user.email})

@login_required(login_url='/login/')
def ai(request):
  return render(request, 'ai.html')

@login_required # Ensure user is logged in to make predictions
def predict(request):
  if request.method == 'POST' and request.FILES.get('file'):
      if model is None:
          return JsonResponse({"error": "AI model not loaded. Please check server logs."}, status=500)

      file = request.FILES['file']
      # Use a unique filename to avoid conflicts, and ensure it's saved in MEDIA_ROOT
      file_extension = os.path.splitext(file.name)[1]
      unique_filename = f"{request.user.username}_{now().strftime('%Y%m%d%H%M%S')}{file_extension}"
      img_path_in_media = os.path.join('ecg_images', unique_filename)  # Subdirectory for ECG images

      # Save the file permanently to MEDIA_ROOT
      try:
          file_name_saved = default_storage.save(img_path_in_media, file)
          full_img_path = default_storage.path(file_name_saved)
      except Exception as e:
          print(f"Error saving uploaded file: {e}")
          return JsonResponse({"error": f"Failed to save image: {e}"}, status=500)

      try:
          # Preprocess and predict
          img_array = preprocess_image(full_img_path)
          prediction = model.predict(img_array)
          predicted_class = np.argmax(prediction, axis=1)[0]
          predicted_label = class_labels[predicted_class]

          # Save prediction result to database
          prediction_record = PredictionResult.objects.create(
              user=request.user,
              uploaded_image=file_name_saved,  # Store the path relative to MEDIA_ROOT
              predicted_label=predicted_label
          )

          # Return the result as JSON, including the prediction ID
          return JsonResponse({"predicted_class": predicted_label, "prediction_id": prediction_record.id})

      except Exception as e:
          print(f"Error during prediction or saving result: {e}")
          # Clean up the temporarily saved file if prediction fails
          if default_storage.exists(file_name_saved):
              default_storage.delete(file_name_saved)
          return JsonResponse({"error": f"Prediction failed: {e}"}, status=500)

  return JsonResponse({"error": "Invalid request or no file uploaded."}, status=400)

@login_required
def generate_report(request, prediction_id):
    try:
        prediction = get_object_or_404(PredictionResult, id=prediction_id, user=request.user)
    except Exception as e:
        messages.error(request, f"Report not found or you don't have permission: {e}")
        return redirect('ai')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(inch, 10.5 * inch, "Heart Disease Prediction Report")
    p.setFont("Helvetica", 12)
    p.drawString(inch, 10.2 * inch, f"Date: {prediction.prediction_date.strftime('%Y-%m-%d %H:%M:%S')}")
    p.line(inch, 10.1 * inch, 7.5 * inch, 10.1 * inch)

    # Patient Information
    p.setFont("Helvetica-Bold", 14)
    p.drawString(inch, 9.5 * inch, "Patient Information:")
    p.setFont("Helvetica", 12)
    p.drawString(inch, 9.2 * inch, f"Name: {request.user.username}")
    p.drawString(inch, 9.0 * inch, f"Email: {request.user.email}")
    
    # Safely access profile fields
    profile = None
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        pass # Profile might not exist for some users

    if profile:
        if profile.contact_number:
            p.drawString(inch, 8.8 * inch, f"Contact: {profile.contact_number}")
        if profile.birth_date:
            p.drawString(inch, 8.6 * inch, f"Date of Birth: {profile.birth_date.strftime('%Y-%m-%d')}")
        if profile.gender:
            p.drawString(inch, 8.4 * inch, f"Gender: {profile.get_gender_display()}")
    
    p.line(inch, 8.2 * inch, 7.5 * inch, 8.2 * inch)

    # Prediction Result
    p.setFont("Helvetica-Bold", 14)
    p.drawString(inch, 7.8 * inch, "Prediction Result:")
    p.setFont("Helvetica", 16)
    p.setFillColorRGB(0.1, 0.5, 0.2)
    p.drawString(inch, 7.4 * inch, f"Predicted Condition: {prediction.predicted_label}")
    p.setFillColorRGB(0, 0, 0)
    p.line(inch, 7.2 * inch, 7.5 * inch, 7.2 * inch)

    # Uploaded Image (if available and valid path)
    if prediction.uploaded_image:
        try:
            img_path = os.path.join(settings.MEDIA_ROOT, prediction.uploaded_image.name)
            if os.path.exists(img_path):
                p.setFont("Helvetica-Bold", 14)
                p.drawString(inch, 6.8 * inch, "Uploaded ECG Image:")
                img = RLImage(img_path)
                img_width = 4 * inch
                img_height = img.drawHeight * img_width / img.drawWidth
                # Ensure image fits on page, adjust y position if needed
                image_y_pos = 6.8 * inch - img_height - 0.2 * inch
                if image_y_pos < 1 * inch: # If it goes too low, adjust
                    image_y_pos = 1 * inch
                p.drawImage(img_path, inch, image_y_pos, width=img_width, height=img_height)
            else:
                p.setFont("Helvetica", 10)
                p.drawString(inch, 6.8 * inch, "Uploaded image not found on server.")
        except Exception as e:
            p.setFont("Helvetica", 10)
            p.drawString(inch, 6.8 * inch, f"Error loading image for PDF: {e}")

    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(inch, 0.5 * inch, "This report is for informational purposes only and should not be used for self-diagnosis.")
    p.drawString(inch, 0.3 * inch, "Generated by HDD. AI System")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'HDD_Report_{prediction.id}.pdf')

@login_required
def prediction_history(request):
    predictions = PredictionResult.objects.filter(user=request.user).order_by('-prediction_date')
    return render(request, 'prediction_history.html', {'predictions': predictions})
