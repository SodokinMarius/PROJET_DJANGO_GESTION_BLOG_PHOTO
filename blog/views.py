from django.contrib.auth.decorators import login_required, permission_required
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
import authentication
from . import forms, models
from django.db.models import Q 
from django.core.paginator import Paginator  #<---------Pour paginer une page
from itertools import chain


@login_required
@permission_required('blog.add_photo')
def photo_upload(request):
    form = forms.PhotoForm()
    if request.method == 'POST':
        form = forms.PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            # set the uploader to the user before saving the model
            photo.uploader = request.user
            # now we can save
            photo.save()
            return redirect('home')
    return render(request, 'blog/photo_upload.html', context={'form': form})


@login_required
def home(request):
    #blogs=models.Blog.objects.filter(contributors__in=request.user.follows.all()) #--> Recuprer uniquement les billets de sblogs des créateurs auxquels l'utilisateur courante s'est connecté
    blogs=models.Blog.objects.filter(
        Q(contributors__in=request.user.follows.all()) |Q(starred=True) #<-- Blogsdont l'un des constributeurs est suivi  ou dont starred=True
        #Pour faire la negation, on utilise ~
    )
    users=authentication.models.User.objects.all()
    photos = models.Photo.objects.all().filter(
        uploader__in=request.user.follows.all()).exclude(blog__in=blogs)
                   #exclure des photos qui sont déjà liées aux instances de blog
    #blogs = models.Blog.objects.all()
    #photos=models.Photo.objects.all().filter(blog__contributors__first_name='SODOKIN') #Inclure les photos qui apparaossent dans un billet écrit par SODOKIN
    
    blog_and_photo=sorted(
        chain(blogs,photos),
        key=lambda instance: instance.date_created, #C'est pour trier l'ensemble blogs et photos
        reverse=True
    )
    paginator=Paginator(blog_and_photo,6) #<-- PAginer l'objet blof_an_photo et le diviser en des pages de 6
    page_number=request.GET.get('page') #<--- Pour recuperer le numro de la pafe courante
    page_obj=paginator.get_page(page_number)  #Recuperer de la page donée
    context={
        #'blog_and_photo':blog_and_photo,
        'page_obj':page_obj,
         'users':users
    }  
    return render(request, 'blog/home.html', context=context)


#Construction de la vue qui servira les les flux de photos

def photo_feed(request):
    photos=models.Photo.objects().filter(
    uploader__in=request.user.follows.all()).order_by('-date_created')
    paginator=Paginator(photos,6)

    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    context={
        #'photos':photos
        'page_obj':page_obj,
        }
    return render(request,'blog/photo_feed.html',context=context)

#vue de telechargement de photo et blog 
@login_required
@permission_required(['blog.add_photo', 'blog.add_blog'])
def blog_and_photo_upload(request):
    blog_form = forms.BlogForm()
    photo_form = forms.PhotoForm()

    if request.method == 'POST':
        blog_form = forms.BlogForm(request.POST)
        photo_form = forms.PhotoForm(request.POST, request.FILES)
        if all([blog_form.is_valid(), photo_form.is_valid()]):
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            blog = blog_form.save(commit=False)
            blog.author = request.user
            blog.photo = photo
            blog.save()
            blog.contributors.add(request.user,through_defaults={'contribution':'Auteur principal '})   # <------------ Sauvegarde Automatique des données dans la table intermediaire
            return redirect('home')

    context = {
        'blog_form': blog_form,
        'photo_form': photo_form,
    }          

    return render(request, 'blog/create_blog_post.html', context=context)


@login_required
def view_blog(request, blog_id):
    blog = get_object_or_404(models.Blog, id=blog_id)
    return render(request, 'blog/view_blog.html', {'blog': blog})


#view for editing blog 
@login_required
@permission_required('blog.change_blog')
def edit_blog(request, blog_id):
    blog = get_object_or_404(models.Blog, id=blog_id)
    edit_form = forms.BlogForm(instance=blog)
    delete_form = forms.DeleteBlogForm()
    if request.method == 'POST':

        if 'edit_blog' in request.POST:
            edit_form = forms.BlogForm(request.POST, instance=blog)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('home')
        if 'delete_blog' in request.POST:
            delete_form = forms.DeleteBlogForm(request.POST)
            if delete_form.is_valid():
                blog.delete()
                return redirect('home')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
    }
    return render(request, 'blog/edit_blog.html', context=context)


#view for creating photo
@login_required
@permission_required('blog.add_photo')
def create_multiple_photos(request):
    PhotoFormSet = formset_factory(forms.PhotoForm, extra=5)
    formset = PhotoFormSet()
    if request.method == 'POST':
        formset = PhotoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:    # Si le formulaire n'est pas vide 
                    photo = form.save(commit=False)
                    photo.uploader = request.user
                    photo.save()
            return redirect('home')
    return render(request, 'blog/create_multiple_photos.html', {'formset': formset})

#Ecrituree de la vue pour suivre des photos
def follows_users(request):
    form =forms.FollowsUserForm(instance=request.user)
    if request.method=='POST':
        form=forms.FollowsUserForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request,'blog/follow_users_form.html',context={'form':form})


