from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password 

class PredictionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    uploaded_image = models.ImageField(upload_to='ecg_images/') # Images will be saved here
    predicted_label = models.CharField(max_length=255) #  stores AI prediction ans
    prediction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prediction for {self.user.username} on {self.prediction_date.strftime('%Y-%m-%d %H:%M')}: {self.predicted_label}"

    class Meta:
        ordering = ['-prediction_date'] # shows in descending order, so new predictions appear first


class Contact(models.Model):
     name = models.CharField(max_length=50)
     email = models.CharField(max_length=120)
     subject = models.CharField(max_length=100)
     message = models.TextField()
     date = models.DateField()
     admin_reply = models.TextField(blank=True, null=True)
     replied_at = models.DateTimeField(blank=True, null=True)

     def __str__(self):
          return self.name
     
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    secret_question = models.CharField(max_length=200, blank=True, null=True)
    secret_answer_hash = models.CharField(max_length=128, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def set_secret_answer(self, raw_answer):
        self.secret_answer_hash = make_password(raw_answer)
    
    def check_secret_answer(self, raw_answer):
        return check_password(raw_answer, self.secret_answer_hash)
# Signals to create/save profile when a User is created/saved
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists before saving it
    if hasattr(instance, 'profile'):
        instance.profile.save()
