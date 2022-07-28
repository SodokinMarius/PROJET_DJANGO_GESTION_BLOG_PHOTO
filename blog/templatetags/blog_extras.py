from django import template
from django.utils import timezone 

register=template.Library()  #<------- C'est pour ganatir l'accessibilité des filtres dans le gabarit
MINUTE=60
HOUR=60*MINUTE
DAY=24*HOUR

#Renvoie d'une representation du type de model
@register.filter  #<--- Pour enregistrer les filtres
def model_type(value):
    return type(value).__name__

#Fonction qui retourne 'vous' ou auteur d'une publication
@register.simple_tag(takes_context=True)# <--Decorateur permettant d'enregistrer une fonction en tant que balise  personnalisée
def get_poster_display(context,user):
    if user==context['user']:
        return 'vous'
    return user.username

@register.filter
def get_posted_at_display(time):
    seconds_ago=(timezone.now()-time).total_seconds()
    if 0<seconds_ago<=HOUR:
        return f'Posté il y a {int(seconds_ago)//MINUTE} minutes'
    elif 1<seconds_ago<=DAY:
        return f'Posté il y a {int(seconds_ago)//HOUR} minutes'
    else:
        return f'Posté il y a {time.strftime("%d %b %y à Hh:%M" )}'







    
