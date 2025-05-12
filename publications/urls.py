from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # Publications
    path('create/', views.create_publication, name='create_publication'),
    path('publication/<int:pk>/', views.detail_publication, name='detail_publication'),
    path('publication/<int:pk>/edit/', views.update_publication, name='update_publication'),
    path('publication/<int:pk>/delete/', views.delete_publication, name='delete_publication'),
    path('search/', views.search_publications, name='search_publications'),

    # Chercheurs Management
    path('manage_chercheurs/', views.manage_chercheurs, name='manage_chercheurs'),
    path('delete_chercheur/<int:user_id>/', views.delete_chercheur, name='delete_chercheur'),
    path('toggle_active_status/<int:user_id>/', views.toggle_active_status, name='toggle_active_status'),

    # Thématiques Management
    path('thematiques/', views.manage_thematiques, name='manage_thematiques'),
    path('thematiques/new/', views.create_thematique, name='create_thematique'),
    path('thematiques/<int:pk>/edit/', views.edit_thematique, name='edit_thematique'),
    path('thematiques/<int:pk>/delete/', views.delete_thematique, name='delete_thematique'),

    path('commentaire/<int:pk>/delete/', views.delete_commentaire, name='delete_commentaire'),
    path('publication_statistics/', views.publication_statistics, name='publication_statistics'), 
    path('favorite_publications/', views.favorite_publications, name='favorite_publications'),
]
