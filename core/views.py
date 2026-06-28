from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from store.models import Course, Podcast, Book
from blog.models import Article

def home(request):
    courses = Course.objects.filter(is_active=True)[:3]
    podcasts = Podcast.objects.filter(is_active=True)[:3]
    books = Book.objects.filter(is_active=True)[:3]
    context = {
        'courses': courses,
        'podcasts': podcasts,
        'books': books,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def team(request):
    return render(request, 'core/team.html')

def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # You can add email sending logic here
        return redirect('contact')
    return render(request, 'core/contact.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'core/register.html', {'error': 'رمز عبور و تکرار آن مطابقت ندارند'})
        
        from core.models import User
        if User.objects.filter(username=username).exists():
            return render(request, 'core/register.html', {'error': 'این نام کاربری قبلاً استفاده شده است'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    
    return render(request, 'core/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'core/login.html', {'error': 'نام کاربری یا رمز عبور اشتباه است'})
    
    return render(request, 'core/login.html')

@login_required
def profile(request):
    return render(request, 'core/profile.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
