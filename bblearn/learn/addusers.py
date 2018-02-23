from django.shortcuts import render, redirect
from BlackboardLearn import interface
from . import util
import json

def addUsers(request, error_message=None):
    ''' If we are displaying an error message, then display blank page w/ no users '''
    if error_message is not None:
        context = {
            'name':request.session['instructor_name'],
            'error_message':error_message,
            'userList': '',
        }
        return render(request, 'learn/addUsers.html', context)

    ''' if there is no search bar data then this is coming straight from course selection - display no users '''
    if 'searchBar' not in request.POST:
        context = {
            'name':request.session['instructor_name'],
            'error_message': '',
            'userList': '',
        }
        return render(request, 'learn/addUsers.html', context)

    searchKey = str(request.POST.get('searchBy'))
    searchString = str(request.POST.get('searchBar')).lower()

    # Load users into sessions
    status = util.loadUsersIntoSession(request)
    if status == None:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif status == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif status == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif status == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    elif status != 200:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Error! Status code: ' + str(status), 'name': request.session['instructor_name'] })
    # search for users based on criteria, then sort the results, then build an HTML list of them.
    users = search(request, searchKey, searchString)
    users = sortUsers(searchKey, users, False)
    userList = buildHtmlUserList(request, users)

    index = 0
    if 'index' in request.session:
        index = request.session['index']
        del request.session['index']

    if userList == '':
        context = {
            'name':request.session['instructor_name'],
            'error_message':"No users found!",
            'userList': '',
            'optionIndex': index,
        }
        return render(request, 'learn/addUsers.html', context)
    context ={
        'name': request.session['instructor_name'],
        'error_message': '',
        'userList': userList,
        'optionIndex': index,
    }
    return render(request, 'learn/addUsers.html', context)

''' Given a list of users, this method returns the same dict, but sorted according to searchKey '''
def sortUsers(searchKey, users, reverse):
    user_results = []
    if searchKey == 'userName':
        from operator import itemgetter
        user_results = sorted(users, key=itemgetter('userName'), reverse=reverse)
    elif searchKey == 'firstName':
        user_results = sorted(users, key=lambda e: e.get('name', {}).get('given'), reverse=reverse)
    elif searchKey == 'lastName':
        user_results = sorted(users, key=lambda e: e.get('name', {}).get('family'), reverse=reverse)
    elif searchKey == 'contact':
        user_results = sorted(users, key=lambda e: e.get('contact', {}).get('email'), reverse=reverse)
    elif searchKey == 'studentId':
        from operator import itemgetter
        user_results = sorted(users, key=itemgetter('studentId'), reverse=reverse)
    else:
        from operator import itemgetter
        user_results = sorted(users, key=itemgetter('userName'), reverse=reverse)
    return user_results

''' given a list of users, this method builds an html list of them. '''
def buildHtmlUserList(request, users):
    userList = ''
    for user in users:
        userList += buildUserListEntry(user)
    return userList


''' create a list of users from search info. '''
def search(request, searchKey, searchString):
    user_results = []
    users = None
    index = 0

    users = request.session['all_users']
    # build list of users to display
    for user in users:
        if 'availability' in user and user['availability']['available'] == 'Yes':
            if searchKey == 'userName':
                index = 1
                if 'userName' not in user and searchString == '':
                    user['userName'] = ''
                    user_results.append(user)
                elif 'userName' in user and searchString in user['userName'].lower():
                    user_results.append(user)
                continue
            elif searchKey == 'firstName':
                index = 2
                if 'name' not in user and searchString == '':
                    user['name'] = {'family':'','given':''}
                    user_results.append(user)
                elif 'name' in user and searchString in user['name']['given'].lower():
                    user_results.append(user)
                continue
            elif searchKey == 'lastName':
                index = 3
                if 'name' not in user and searchString == '':
                    user['name'] = {'family':'','given':''}
                    user_results.append(user)
                elif 'name' in user and searchString in user['name']['family'].lower():
                    user_results.append(user)
                continue
            elif searchKey == 'contact':
                index = 4
                if 'contact' not in user and (not searchString or not searchString.strip()):
                    user['contact'] = {'email':''}
                    user_results.append(user)
                elif 'contact' in user and searchString in user['contact']['email'].lower():
                    user_results.append(user)
                continue
            elif searchKey == 'studentId':
                index = 5
                if 'studentId' not in user and searchString.strip() == '':
                    user['studentId'] = ''
                    user_results.append(user)
                elif 'studentId' in user and searchString in user['studentId']:
                    user_results.append(user)
                continue
            else:
                index = 0
                user_results.append(user)
                continue
    request.session['index'] = index
    return user_results

def buildUserListEntry(user):

    userList = ''
    userList += '<tr>'
    userList += '<td><input class="userCheckbox" type="checkbox" name="users" value="' + user['userName'] + '"></td>'
    userList += '<td>' + user['userName'] + '</td>'
    if 'name' in user:
        if 'given' in user['name']:
            userList += '<td>' + user['name']['given'] + '</td>'
        else:
            userList += '<td></td>'
        if 'family' in user['name']:
            userList += '<td>' + user['name']['family'] + '</td>'
        else:
            userList += '<td></td>'
    else:
        userList += '<td></td>'
        userList += '<td></td>'
    if 'contact' in user:
        userList += '<td>' + user['contact']['email'] + '</td>'
    else:
        userList += '<td></td>'
    if 'studentId' in user: #guests don't have studentId
        userList += '<td>' + user['studentId'] + '</td>'
    else:
        userList += '<td></td>'
    userList += '</tr>'

    return userList
