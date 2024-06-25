from django.shortcuts import redirect, render
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from whistleblower.models import Report
from .forms import CustomUserCreationForm

def signup(request):
    if request.user.is_authenticated:
        # If user is already authenticated, redirect them to a common user page or dashboard
        return redirect('accounts:profile')
    else:
        # User is not authenticated; present the signup form
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                # Log the user in (optional)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                # Redirect to a success page or login page after signup
                print('Sign up successful.')
                # Assuming 'home:index' is a placeholder for your actual home/dashboard page
                return redirect('/')  # Adjust as needed
        else:
            form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

@login_required(login_url='/accounts/signin/')
def profile(request):
    """
    Profile page for the user.

    If the user is a staff member, they will be redirected to the site admin page.
    """
    user = request.user
    reports = reports = Report.objects.filter(reported_by=request.user).order_by('-created_at')
    print(reports)
    return render(request, 'accounts/profile.html', {'user': user, 'reports': reports})

@login_required(login_url='/accounts/signin/')
def custom_logout(request):
    """
    Custom logout view function.
    """
    logout(request)  # This logs out the user
    messages.add_message(
        request,
        messages.SUCCESS,
        'You have been successfully logged out.')
    return redirect('/')  # Redirect to login page or home page

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/signin.html')

