from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from django.core.files.base import ContentFile
from .forms import CustomLoginForm, CustomRegistrationForm, PreferencesForm
from .models import UserPreferences

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        # Check if user has preferences
        try:
            UserPreferences.objects.get(user=self.request.user)
            # User has preferences, go to dashboard
            return reverse_lazy('dashboard')
        except UserPreferences.DoesNotExist:
            # User doesn't have preferences, redirect to preferences setup
            return reverse_lazy('preferences_setup')
    
    def form_valid(self, form):
        messages.success(self.request, 'Connexion réussie!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Email ou mot de passe incorrect.')
        return super().form_invalid(form)

class CustomRegistrationView(CreateView):
    form_class = CustomRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            # Let the form handle the saving process
            user = form.save()
            messages.success(self.request, 'Inscription réussie! Vous pouvez maintenant vous connecter.')
            return redirect(self.success_url)
        except Exception as e:
            # Add error handling
            messages.error(self.request, f'Erreur lors de l\'inscription: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Add better error handling for form validation
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

@login_required
def preferences_setup(request):
    """Vue pour la configuration initiale des préférences utilisateur"""
    try:
        # Check if user already has preferences
        preferences = UserPreferences.objects.get(user=request.user)
        # If preferences exist, redirect to dashboard
        return redirect('dashboard')
    except UserPreferences.DoesNotExist:
        # User doesn't have preferences, show setup form
        pass
    
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.user = request.user
            preferences.save()
            messages.success(request, 'Vos préférences ont été enregistrées avec succès!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = PreferencesForm()
    
    return render(request, 'accounts/preferences_setup.html', {'form': form})

@login_required
def preferences_edit(request):
    """Vue pour modifier les préférences utilisateur"""
    try:
        preferences = UserPreferences.objects.get(user=request.user)
    except UserPreferences.DoesNotExist:
        # If no preferences exist, redirect to setup
        return redirect('preferences_setup')
    
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vos préférences ont été mises à jour avec succès!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = PreferencesForm(instance=preferences)
    
    return render(request, 'accounts/preferences_edit.html', {'form': form, 'preferences': preferences})

@csrf_exempt
def process_id_card(request):
    """
    Vue pour traiter l'image de la carte d'identité
    Cette vue simule l'extraction des données - vous devrez intégrer une vraie API OCR
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            extracted_data = {
                'nom': 'BENCHEIKH',
                'prenom': 'Ahmed',
                'numero_national': '1234567890123456',
                'success': True
            }
            
            return JsonResponse(extracted_data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def custom_logout(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie!')
    return redirect('login')

@login_required
def dashboard(request):
    try:
        preferences = UserPreferences.objects.get(user=request.user)
    except UserPreferences.DoesNotExist:
        # If no preferences, redirect to setup
        return redirect('preferences_setup')
    
    context = {
        'user': request.user,
        'preferences': preferences,
    }
    return render(request, 'accounts/dashboard.html', context)