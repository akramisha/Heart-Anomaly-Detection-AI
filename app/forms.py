# app/forms.py (Create this file if it doesn't exist)
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile, Contact

class UserRegistrationForm(UserCreationForm):
    # Add fields from Profile model directly to the registration form
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(max_length=20, required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=False)
    location = forms.CharField(max_length=255, required=False)
    education = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)
    
    # New fields for secret question and answer
    secret_question = forms.CharField(max_length=255, required=True, help_text="e.g., What is your mother's maiden name?")
    secret_answer = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput, help_text="This will be used to verify your identity if you forget your password.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 'contact_number', 'birth_date', 'gender', 'location',
            'education', 'bio', 'profile_picture', 'secret_question', 'secret_answer'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.email = self.cleaned_data.get('email')
            profile.contact_number = self.cleaned_data.get('contact_number')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.gender = self.cleaned_data.get('gender')
            profile.location = self.cleaned_data.get('location')
            profile.education = self.cleaned_data.get('education')
            profile.bio = self.cleaned_data.get('bio')

            
            profile.secret_question = self.cleaned_data.get('secret_question')

            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data.get('profile_picture')

            raw_secret_answer = self.cleaned_data.get('secret_answer')
            if raw_secret_answer:
                profile.set_secret_answer(raw_secret_answer)

            profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'contact_number', 
            'gender',
            'birth_date',
            'location',
            'education',
            'bio'
        ]
        widgets = {
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your contact number'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your location'
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your education'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself',
                'rows': 4
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional (not required)
        for field in self.fields.values():
            field.required = False

class CustomPasswordChangeForm(PasswordChangeForm):
    # You can add custom validation or styling here if needed
    pass

class SecretQuestionForm(forms.Form):
    secret_answer = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput,
        label="Your Secret Answer",
        help_text="Please enter the answer to your secret question."
    )


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['admin_reply']
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']