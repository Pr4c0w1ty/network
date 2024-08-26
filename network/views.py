import datetime
import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import  HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Follow, Like
import json
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()
    # Pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_of_page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        all_likes = Like.objects.filter(user=request.user)
        who_you_liked = list(set([like.post.id for like in all_likes]))
    else:
        who_you_liked = []

    return render(request, "network/index.html", {
        "all_posts": all_posts,
        "post_of_page": post_of_page,
        "who_you_liked": who_you_liked,
    })

def remove_like(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        user = request.user  # Already authenticated due to the decorator
        like = Like.objects.get(user=user, post=post)
        like.delete()
        return JsonResponse({"message": "Like removed."})
    except ObjectDoesNotExist as e:
        return JsonResponse({"error": str(e)}, status=404)  # Object not found
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)  # Other exceptions

def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    new_like = Like(user=user, post=post)
    new_like.save()
    return JsonResponse({"message": "Like added."})

def new_post(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(user=user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/index.html")

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    try:
        check_follow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(check_follow) > 0:
            is_following = True
        else:
            is_following = False
    except:
        is_following = False
    # Pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_of_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "post_of_page": post_of_page,
        "username": user,
        "following": following,
        "followers": followers,
        "is_following": is_following,
        "user_profile": user
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        editpost = Post.objects.get(pk=post_id)
        editpost.content = data["content"]
        editpost.save()
        return JsonResponse({"message": "Post edited."}, status=201)
        

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
def follow(request):
    userfollow = request.POST['userfollow']
    user = User.objects.get(pk=request.user.id)
    userfollowdata = User.objects.get(username=userfollow)

    f = Follow(user=user, user_follower=userfollowdata)
    f.save()
    user_id = userfollowdata.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    user = User.objects.get(pk=request.user.id)
    userfollowdata = User.objects.get(username=userfollow)

    f = Follow.objects.get(user=user, user_follower=userfollowdata)
    f.delete()
    user_id = userfollowdata.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))

def following(request):

    current_user = User.objects.get(pk=request.user.id)
    followingusers = Follow.objects.filter(user=current_user)
    all_posts = Post.objects.filter(user__in=[user.user_follower for user in followingusers]).order_by("id").reverse()

    # Pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_of_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "post_of_page": post_of_page
    })