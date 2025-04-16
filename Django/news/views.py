from django.shortcuts import render, redirect
from .models import Articles, Comments
from .forms import ArticlesForm


def news_home(request):
    news = Articles.objects.order_by('-date')
    return render(request, 'news/news_home.html', {'news': news})


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


def article_detail(request, article_id):
    article = Articles.objects.get(id=article_id)
    comments = article.comments.all()

    return render(request, 'news/article_detail.html', {
        'article': article,
        'comments': comments
    })