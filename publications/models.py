from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

class Thematique(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la thématique")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Thématique"
        verbose_name_plural = "Thématiques"
        ordering = ['nom']

class Chercheur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chercheur')
    nom = models.CharField(max_length=100, default='Unknown', verbose_name="Nom")
    prenom = models.CharField(max_length=100, default='Unknown', verbose_name="Prénom")

    def __str__(self):
        return f'{self.prenom} {self.nom}'

    class Meta:
        verbose_name = "Chercheur"
        verbose_name_plural = "Chercheurs"
        ordering = ['nom', 'prenom']

class Publication(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(default=' ', verbose_name="Description")
    contenu_pdf = models.FileField(upload_to='publications/', blank=True, null=True, verbose_name="Contenu PDF")
    thematique = models.ForeignKey(Thematique, on_delete=models.CASCADE, related_name='publications', verbose_name="Thématique")
    auteur = models.ForeignKey(Chercheur, on_delete=models.CASCADE, related_name='publications', verbose_name="Auteur")
    date_publication = models.DateTimeField(default=timezone.now, verbose_name="Date de publication")
    views = models.IntegerField(default=0, verbose_name="Nombre de vues")

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ['titre']

class Commentaire(models.Model):
    contenu = models.TextField(verbose_name="Contenu")
    publication = models.ForeignKey(Publication, related_name='commentaires', on_delete=models.CASCADE, verbose_name="Publication")
    auteur = models.ForeignKey(Chercheur, on_delete=models.CASCADE, related_name='commentaires', verbose_name="Auteur")
    date_comment = models.DateTimeField(default=timezone.now, verbose_name="Date de commentaire")

    def __str__(self):
        return f'Commentaire de {self.auteur} sur {self.publication}'

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-date_comment']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_publications = models.ManyToManyField('Publication', related_name='favorited_by')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()