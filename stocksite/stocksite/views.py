from django.shortcuts import render

# Create your views here.

def index(request):
    html = "<html><body>it is bool</body></html>"
    return HttpResponse(html)