from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.

def validate_logon(request):

    if request.method == "POST":

        user = authenticate(username=request.POST.get("username"),
                            password=request.POST.get("password"))
        if user is not None:

            login(request,user)
            return HttpResponse("ok")

        else:
            return HttpResponse()
    return render(request,'login.html')

@login_required
def index(request):
    return render(request, 'index.html')