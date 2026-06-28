from django.shortcuts import render, get_object_or_404
from .models import Article

def articles(request):
    articles = Article.objects.filter(is_active=True)
    return render(request, 'blog/articles.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_active=True)
    return render(request, 'blog/article_detail.html', {'article': article})
