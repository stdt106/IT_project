from django.shortcuts import render


def index(request):
    data = {
        'title': 'Main page',
        'values': ['smth', 123, 'hello', 124345, 12345, 1234, 123456, 234567, 6789, 5678, 678, 5678, 34567, 890, 89, 89, 9, 6789]
    }
    return render(request, 'ex_1/index.html', data)


def about(request):
    return render(request, 'ex_1/about.html')