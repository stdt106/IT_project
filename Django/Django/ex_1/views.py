from django.shortcuts import render


def index(request):
    return render(request, 'ex_1/index.html')


def about(request):
    return render(request, 'ex_1/about.html')