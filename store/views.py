from django.shortcuts import render, get_object_or_404
from .models import Course, Podcast, Book

def courses(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'store/courses.html', {'courses': courses})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    return render(request, 'store/course_detail.html', {'course': course})

def podcasts(request):
    podcasts = Podcast.objects.filter(is_active=True)
    return render(request, 'store/podcasts.html', {'podcasts': podcasts})

def podcast_detail(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug, is_active=True)
    return render(request, 'store/podcast_detail.html', {'podcast': podcast})

def books(request):
    books = Book.objects.filter(is_active=True)
    return render(request, 'store/books.html', {'books': books})

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    return render(request, 'store/book_detail.html', {'book': book})
