from django.contrib import admin
from app.models import Contact, Profile, PredictionResult



admin.site.register(Contact)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
        list_display = ('user', 'location', 'birth_date')
        search_fields = ('user__username', 'location')
        list_filter = ('location',)