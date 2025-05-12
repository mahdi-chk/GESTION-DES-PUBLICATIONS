from django.contrib import admin
from .models import Chercheur, Thematique, Publication, Commentaire

admin.site.register(Chercheur)
admin.site.register(Thematique)
admin.site.register(Publication)
admin.site.register(Commentaire)
