from django import forms
from .models import Publication, Commentaire, Thematique, Chercheur
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titre', 'description', 'contenu_pdf', 'thematique']  
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
            'contenu_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'thematique': forms.Select(attrs={'class': 'form-control'}),  
        }
        labels = {
            'titre': 'Titre',
            'description': 'Description',
            'contenu_pdf': 'Fichier PDF',
            'thematique': 'Thématique',  
        }
        help_texts = {
            'contenu_pdf': 'Télécharger le PDF de la publication ici.',
        }


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'class': 'form-control'}),
        }
        labels = {
            'contenu': 'Comment Content',
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nom d\'utilisateur',
            'email': 'Adresse e-mail',
            'password1': 'Mot de passe',
            'password2': 'Confirmer le mot de passe',
        }

class ThematiqueForm(forms.ModelForm):
    class Meta:
        model = Thematique
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': 'Theme Name',
        }

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Chercheur
        fields = ['nom', 'prenom']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = user.username
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
