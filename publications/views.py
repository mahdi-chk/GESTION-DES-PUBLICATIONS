from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Chercheur, Publication, Thematique, Commentaire, UserProfile
from .forms import PublicationForm, CommentaireForm, ThematiqueForm, ProfileForm, UserRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User 
from django.db import IntegrityError


def home(request):
    publications = Publication.objects.select_related('thematique', 'auteur').all()
    thematiques = Thematique.objects.all()
    user_profile = None
    
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if not hasattr(request.user, 'chercheur'):
            Chercheur.objects.create(user=request.user, nom=request.user.username, prenom='Unknown')

        if request.method == 'POST':
            publication_id = request.POST.get('publication_id')
            publication = get_object_or_404(Publication, id=publication_id)

            if publication in user_profile.favorite_publications.all():
                user_profile.favorite_publications.remove(publication)
            else:
                user_profile.favorite_publications.add(publication)

            return redirect('home')

    return render(request, 'publications/home.html', {
        'publications': publications, 
        'thematiques': thematiques, 
        'user_profile': user_profile,
        'is_authenticated': request.user.is_authenticated
    })


@login_required
def create_publication(request):
    if not hasattr(request.user, 'chercheur'):
        Chercheur.objects.create(user=request.user, nom=request.user.username, prenom='Unknown')

    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.auteur = request.user.chercheur
            publication.save()
            messages.success(request, 'Publication créée avec succès.')
            return redirect('home')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PublicationForm()

    return render(request, 'publications/create_publication.html', {'form': form})

@login_required
def detail_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    publication.views += 1  
    publication.save()  

    commentaires = Commentaire.objects.filter(publication=publication)

    if request.method == "POST":
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.date_comment = timezone.now()
            if hasattr(request.user, 'chercheur'):
                commentaire.auteur = request.user.chercheur
                commentaire.publication = publication
                commentaire.save()
                messages.success(request, 'Commentaire ajouté avec succès.')
                return redirect('detail_publication', pk=pk)
            else:
                messages.error(request, 'Veuillez compléter votre profil de chercheur.')
                return redirect('edit_profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CommentaireForm()

    return render(request, 'publications/detail_publication.html', {
        'publication': publication,
        'commentaires': commentaires,
        'form': form,  
        'is_superuser': request.user.is_superuser
    })


@login_required
def delete_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    if request.user == publication.auteur.user or request.user.is_superuser:
        publication.delete()
        messages.success(request, 'Publication supprimée avec succès.')
    else:
        messages.error(request, 'Vous n\'êtes pas autorisé à supprimer cette publication.')
    return redirect('home')

@login_required
def update_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    if request.user != publication.auteur.user and not request.user.is_superuser:
        messages.error(request, 'Vous n\'êtes pas autorisé à modifier cette publication.')
        return redirect('home')

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication modifiée avec succès.')
            return redirect('detail_publication', pk=publication.pk)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PublicationForm(instance=publication)

    return render(request, 'publications/update_publication.html', {'form': form})


def search_publications(request):
    query = request.GET.get('q')
    thematiques = Thematique.objects.all()
    results = Publication.objects.filter(
        Q(titre__icontains=query) | 
        Q(description__icontains=query) | 
        Q(auteur__user__username__icontains=query) | 
        Q(thematique__nom__icontains=query)
    ).distinct()
    return render(request, 'publications/search_results.html', {'results': results, 'thematiques': thematiques})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=user.username, password=raw_password)
                if user is not None:
                    Chercheur.objects.create(user=user, nom=user.username, prenom='Unknown')
                    login(request, user)
                    messages.success(request, 'Votre compte a été créé avec succès !')
                    return redirect('home') 
                else:
                    messages.error(request, 'Une erreur est survenue lors de la connexion.')
            except IntegrityError:
                messages.error(request, 'Le nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def manage_chercheurs(request):
    chercheurs = Chercheur.objects.all()
    return render(request, 'admin/manage_chercheurs.html', {'chercheurs': chercheurs})

@user_passes_test(lambda u: u.is_superuser)
def delete_chercheur(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, 'Chercheur supprimé avec succès.')
    return redirect('manage_chercheurs')

@user_passes_test(lambda u: u.is_superuser)
def toggle_active_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, 'Statut du chercheur modifié avec succès.')
    return redirect('manage_chercheurs')

@user_passes_test(lambda u: u.is_superuser)
def manage_thematiques(request):
    thematiques = Thematique.objects.all()
    return render(request, 'admin/manage_thematiques.html', {'thematiques': thematiques})

@user_passes_test(lambda u: u.is_superuser)
def create_thematique(request):
    if request.method == 'POST':
        form = ThematiqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thématique créée avec succès.')
            return redirect('manage_thematiques')
    else:
        form = ThematiqueForm()
    return render(request, 'admin/create_thematique.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def edit_thematique(request, pk):
    thematique = get_object_or_404(Thematique, pk=pk)
    if request.method == 'POST':
        form = ThematiqueForm(request.POST, instance=thematique)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thématique modifiée avec succès.')
            return redirect('manage_thematiques')
    else:
        form = ThematiqueForm(instance=thematique)
    return render(request, 'admin/edit_thematique.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def delete_thematique(request, pk):
    thematique = get_object_or_404(Thematique, pk=pk)
    if request.method == 'POST':
        thematique.delete()
        messages.success(request, 'Thématique supprimée avec succès.')
        return redirect('manage_thematiques')
    return render(request, 'admin/delete_thematique.html', {'thematique': thematique})

@login_required
def edit_profile(request):
    if not hasattr(request.user, 'chercheur'):
        Chercheur.objects.create(user=request.user, nom=request.user.username, prenom='Unknown')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.chercheur, user=request.user)
        if form.is_valid():
            chercheur = form.save(commit=False)
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            chercheur.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user.chercheur, user=request.user)

    return render(request, 'registration/edit_profile.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_commentaire(request, pk):
    commentaire = get_object_or_404(Commentaire, pk=pk)
    publication_id = commentaire.publication.pk
    commentaire.delete()
    messages.success(request, 'Commentaire supprimé avec succès.')
    return redirect('detail_publication', pk=publication_id)

@login_required
def publication_statistics(request):
    if not request.user.is_superuser:
        return redirect('home')

    publications = Publication.objects.all()
    stats = [{'publication': pub, 'views': pub.views, 'comments': pub.commentaires.count()} for pub in publications]

    sort_by = request.GET.get('sort_by', 'views')
    order = request.GET.get('order', 'desc')

    if sort_by == 'views':
        stats.sort(key=lambda x: x['views'], reverse=(order == 'desc'))
    elif sort_by == 'comments':
        stats.sort(key=lambda x: x['comments'], reverse=(order == 'desc'))

    return render(request, 'admin/publication_statistics.html', {'stats': stats, 'sort_by': sort_by, 'order': order})

@login_required
def favorite_publications(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    favorites = user_profile.favorite_publications.all()
    return render(request, 'publications/favorite_publications.html', {'favorites': favorites})
