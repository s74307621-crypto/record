from django.contrib import admin
from .models import Category, Course, Podcast, Book

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
