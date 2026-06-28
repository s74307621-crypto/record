from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from store import views as store_views
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core pages
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('team/', core_views.team, name='team'),
    path('contact/', core_views.contact, name='contact'),
    
    # Authentication
    path('login/', core_views.login_view, name='login'),
    path('logout/', core_views.logout_view, name='logout'),
    path('register/', core_views.register, name='register'),
    path('profile/', core_views.profile, name='profile'),
    
    # Store - Courses
    path('courses/', store_views.courses, name='courses'),
    path('course/<slug:slug>/', store_views.course_detail, name='course_detail'),
    
    # Store - Podcasts
    path('podcasts/', store_views.podcasts, name='podcasts'),
    path('podcast/<slug:slug>/', store_views.podcast_detail, name='podcast_detail'),
    
    # Store - Books
    path('books/', store_views.books, name='books'),
    path('book/<slug:slug>/', store_views.book_detail, name='book_detail'),
    
    # Blog - Articles
    path('articles/', blog_views.articles, name='articles'),
    path('article/<slug:slug>/', blog_views.article_detail, name='article_detail'),
    
    # Error pages
    path('400/', core_views.error_400, name='error_400'),
    path('500/', core_views.error_500, name='error_500'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'core.views.error_400'
handler500 = 'core.views.error_500'
