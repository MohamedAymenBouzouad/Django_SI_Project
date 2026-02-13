from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django import forms
from django.core.exceptions import ValidationError
from .models import User
from common.models import Client, Driver, Manager, Agent

class UserAdminForm(forms.ModelForm):
    """Simple form for user creation - username, password, role, and profile"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave blank to keep current password"
    )
    
    # Profile selection fields
    client_profile = forms.ModelChoiceField(
        queryset=Client.objects.filter(is_active=True),
        required=False,
        label="Select Client"
    )
    driver_profile = forms.ModelChoiceField(
        queryset=Driver.objects.filter(is_active=True),
        required=False,
        label="Select Driver"
    )
    manager_profile = forms.ModelChoiceField(
        queryset=Manager.objects.all(),
        required=False,
        label="Select Manager"
    )
    agent_profile = forms.ModelChoiceField(
        queryset=Agent.objects.all(),
        required=False,
        label="Select Agent"
    )
    
    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'client_profile', 'driver_profile', 'manager_profile', 'agent_profile']
    
    def clean(self):
        """Validate that a profile is selected matching the role"""
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'client' and not cleaned_data.get('client_profile'):
            raise ValidationError("Please select a Client profile")
        elif role == 'driver' and not cleaned_data.get('driver_profile'):
            raise ValidationError("Please select a Driver profile")
        elif role == 'manager' and not cleaned_data.get('manager_profile'):
            raise ValidationError("Please select a Manager profile")
        elif role == 'agent' and not cleaned_data.get('agent_profile'):
            raise ValidationError("Please select an Agent profile")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user and assign the selected profile"""
        user = super().save(commit=False)
        
        # Hash the password if provided and not empty
        password = self.cleaned_data.get('password', '').strip()
        if password:  # Only set if password is provided (not blank)
            user.set_password(password)
            user.simple_password = password
        
        # Assign profile based on role
        if user.role == 'client':
            user.client_profile = self.cleaned_data.get('client_profile')
            user.driver_profile = None
            user.manager_profile = None
            user.agent_profile = None
        elif user.role == 'driver':
            user.driver_profile = self.cleaned_data.get('driver_profile')
            user.client_profile = None
            user.manager_profile = None
            user.agent_profile = None
        elif user.role == 'manager':
            user.manager_profile = self.cleaned_data.get('manager_profile')
            user.client_profile = None
            user.driver_profile = None
            user.agent_profile = None
        elif user.role == 'agent':
            user.agent_profile = self.cleaned_data.get('agent_profile')
            user.client_profile = None
            user.driver_profile = None
            user.manager_profile = None
        
        if commit:
            user.save()
        return user

@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    form = UserAdminForm
    add_form = UserAdminForm  # Use our custom form for add view too
    list_display = ['username', 'role', 'get_profile', 'is_staff']
    list_filter = ['role', 'is_staff']
    
    fieldsets = (
        ('Credentials', {
            'fields': ('username', 'password', 'role')
        }),
        ('Profile Selection', {
            'fields': ('client_profile', 'driver_profile', 'manager_profile', 'agent_profile'),
            'description': 'Select the profile matching the role above'
        }),
    )
    
    def get_profile(self, obj):
        """Display which profile is assigned"""
        if obj.client_profile:
            return f"Client: {obj.client_profile.name}"
        elif obj.driver_profile:
            return f"Driver: {obj.driver_profile.first_name} {obj.driver_profile.last_name}"
        elif obj.manager_profile:
            return f"Manager: {obj.manager_profile.first_name} {obj.manager_profile.last_name}"
        elif obj.agent_profile:
            return f"Agent: {obj.agent_profile.first_name} {obj.agent_profile.last_name}"
        return "No Profile"
    get_profile.short_description = "Profile"