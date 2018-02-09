from django.shortcuts import render
from learn import confirmUsers

def viewUsers(request):
    context = {

    }
    return render(request, 'learn/viewUsers.html', context)

def removeUsers(request):
    context = {

    }
    return render(request, 'learn/removeUsers.html', context)

def addUsers(request):

    selectedUsers = request.session['selected_users']

    userList = confirmUsers.search(selectedUsers)
    

    context = {

        'addedUser': userList,
    }
    return render(request, 'learn/confirmAddedUsers.html', context)
