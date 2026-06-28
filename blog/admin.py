from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
