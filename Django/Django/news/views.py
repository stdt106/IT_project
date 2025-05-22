from django.shortcuts import render, redirect, get_object_or_404
from .models import Articles, Comments
from .forms import ArticlesForm, CommentForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def custom_logout(request):
    logout(request)
    return redirect('/')


def news_home(request):
    query = request.GET.get('q')
    if query:
        news = Articles.objects.filter(
            Q(title__icontains=query) |
            Q(anons__icontains=query) |
            Q(full_text__icontains=query)
        ).order_by('-date')
    else:
        news = Articles.objects.order_by('-date')

    return render(request, 'news/news_home.html', {'news': news, 'query': query})


def create(request):
    error = ''
    if request.method == 'POST':
        form = ArticlesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма неверно заполнена'

    form = ArticlesForm()

    data = {
        'form': form,
        'error': error
    }

    return render(request, 'news/create.html', data)


def news_detail(request, pk):
    article = get_object_or_404(Articles, pk=pk)
    comments = Comments.objects.filter(article=article).order_by('-created_at')

    form = CommentForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.article = article
                comment.save()
                return redirect('news_detail', pk=article.pk)

    return render(request, 'news/detail.html', {
        'article': article,
        'comments': comments,
        'form': form
    })
