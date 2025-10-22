from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import CollabUser
from .forms import UserUpdateForm, CollabUserUpdateForm


# user registration view
def register_user(request):
    if request.method == 'POST':
        # Get data from the form
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # check pass & confirm pass
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user:register_user')

        # check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('user:register_user')

        # create user
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = False  # Cannot access admin
        user.is_superuser = False  # Definitely not admin
        user.save()

        # register done msg
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('user:login_user')

        # render reg form for GET method
    return render(request, 'user/register_form.html')


# login view
def login_user(request):
    if request.method == "POST":
        # get data from form
        username = request.POST.get("username")
        password = request.POST.get("password")
        # if no user, return none
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            # no login msg
            messages.error(request, "Invalid credentials")
            return render(request, "user/login_form.html")
    else:
        return render(request, "user/login_form.html")

# logout view
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


# profile view
@login_required
def user_profile(request):
    user = request.user
    profile = CollabUser.objects.get(user=user)
    if request.user.is_authenticated:
        events = Event.objects.all()
        projects = Project.objects.all()
        theses = Thesis.objects.all()

        for e in events:
            e.content_type = "Event"
            e.date_field = e.created_at
        for p in projects:
            p.content_type = "Project"
            p.date_field = p.created_at
        for t in theses:
            t.content_type = "Thesis"
            t.date_field = t.created_at

        feed_items = list(chain(events, projects, theses))

        feed_items = list([fi for fi in feed_items if fi.organizer.user == user])

        # 🎲 Add slight random variation to sort key
        def sort_key(item):
            # Random factor between -300 and +300 seconds (±5 minutes)
            random_offset = random.uniform(-300, 300)
            # Apply offset to timestamp
            return item.date_field.timestamp() + random_offset

        # Sort by adjusted key descending (newer + randomness)
        feed_items.sort(key=sort_key, reverse=True)
    return render(request, 'user/user_profile.html', {'profile': profile, 'feed_items': feed_items})

# update profile
@login_required
def update_user(request):
    user = request.user
    profile = CollabUser.objects.get(user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('collaborator_phone')
        department = request.POST.get('collaborator_department')
        university = request.POST.get('collaborator_university')
        university_id = request.POST.get('collaborator_university_id')
        date_of_birth = request.POST.get('collaborator_dob')
        type = request.POST.get('collaborator_type')
        about = request.POST.get('collaborator_about')
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        profile.collaborator_phone = phone_number
        profile.collaborator_department = department
        profile.collaborator_university = university
        profile.collaborator_university_id = university_id
        profile.collaborator_date_of_birth = date_of_birth
        profile.collaborator_type = type
        profile.collaborator_about = about
        user.save()
        profile.save()
        return redirect('user:user_profile')

    return render(request, 'user/update_profile.html', {
        'user': user,
        'profile': profile
    })


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
