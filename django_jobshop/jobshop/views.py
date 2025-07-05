from django.shortcuts import render


# Create your views here.
def hello_view(request):
    return render(request, 'hello_django.html', {
        'data': "Hello Django ",
    })

def dashboard_view(request):
    return render(request, './dist/dashboard/index.html', {
        'data': "Hello Django ",
    })