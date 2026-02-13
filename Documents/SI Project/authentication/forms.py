from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from common.models import Client

User = get_user_model()

class ClientSignupForm(forms.ModelForm):
    """
    Form for client registration
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = Client
        fields = [
            'email', 'phone', 'address', 'city', 'postal_code', 'country'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            label="Username"
        )
        self.fields['email'] = forms.EmailField(
            widget=forms.EmailInput(attrs={'class': 'form-control'}),
            label="Email"
        )
        self.fields['first_name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John'}),
            label="First Name",
            max_length=100,
            required=True
        )
        self.fields['last_name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doe'}),
            label="Last Name",
            max_length=100,
            required=True
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return cleaned_data

    def save(self, commit=True):
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip() or "Client"

        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=last_name,
            role='client'
        )

        client = super().save(commit=False)
        client.name = full_name
        client.save()

        user.client_profile = client
        user.save()

        return client


from common.models import Driver

class DriverSignupForm(forms.ModelForm):
    """
    Form for driver registration
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = Driver
        fields = [
            'first_name', 'last_name', 'license_number', 'license_expiry', 'phone', 'email', 'address', 'hire_date'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add user fields
        self.fields['username'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            label="Username"
        )
        # Email and names are already in Meta fields, so we just need to update widgets
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})
        self.fields['first_name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['last_name'].widget = forms.TextInput(attrs={'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        license_number = cleaned_data.get('license_number')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        if Driver.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("License number already registered")

        return cleaned_data

    def save(self, commit=True):
        # Create the user first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='driver'
        )

        # Create the driver profile
        driver = super().save(commit=False)
        driver.save()  # Save first to get the ID

        # Link the user to the driver profile
        user.driver_profile = driver
        user.save()

        return driver