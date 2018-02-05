from django.shortcuts import render

def viewUsers(request):
    context = {

    }
    return render(request, 'learn/viewUsers.html', context)

def removeUsers(request):
    context = {

    }
    return render(request, 'learn/removeUsers.html', context)
