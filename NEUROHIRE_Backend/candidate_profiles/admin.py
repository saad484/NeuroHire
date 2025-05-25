from django.contrib import admin
from .models import CandidateProfile, SocialProfile

class SocialProfileInline(admin.TabularInline):
    model = SocialProfile
    extra = 1

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'current_position', 'location')
    search_fields = ('user__username', 'user__email', 'current_position')
    inlines = [SocialProfileInline]

@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate', 'platform', 'profile_url', 'last_updated')
    list_filter = ('platform',)
    search_fields = ('candidate__user__username', 'platform', 'profile_url')
    readonly_fields = ('profile_data', 'last_updated')
