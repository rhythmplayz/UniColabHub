from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import CollabUser
from .forms import UserUpdateForm, CollabUserUpdateForm
from django.contrib.auth.models import User


# delete user
@login_required
def delete_user(request):
    if request.method == "POST":
        password = request.POST.get("password")
        user = request.user

        if user.check_password(password):
            username = user.username

            logout(request)
            user.delete()

            messages.success(request, f"User '{username}' account deleted successfully.")
            return redirect('home')
        else:
            messages.error(request, "Incorrect password. Please try again.")

    return render(request, "user/delete_confirmation.html")
