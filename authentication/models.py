from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    CREATOR = 'CREATOR'
    SUBSCRIBER = 'SUBSCRIBER'

    ROLE_CHOICES = (
        (CREATOR, 'Créateur'),
        (SUBSCRIBER, 'Abonné'),
    )
    profile_photo = models.ImageField(verbose_name='photo de profil')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='rôle')

    #Etablissons la relation ManyToMany
    follows=models.ManyToManyField(
        'self',
        limit_choices_to={'role':CREATOR},  #<------- Qui peut être suivi
        symmetrical=False ,#<--------- La relation est reflexive et non symétrique
        verbose_name='Suit',
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Attribution des Droits aux utilisateurs
        if self.role == self.CREATOR:
            group = Group.objects.get(name='creators')
            group.user_set.add(self)
        elif self.role == self.SUBSCRIBER:
            group = Group.objects.get(name='subscribers')
            group.user_set.add(self)
