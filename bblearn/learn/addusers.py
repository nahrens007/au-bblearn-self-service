from django.shortcuts import render, redirect
from BlackboardLearn import interface
from . import util
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def getPage(request, user_list):

    page = request.session.get('page', 1)

    paginator = Paginator(user_list, 20)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        request.session['page'] = 1
        users = paginator.page(1)
    except EmptyPage:
        request.session['page'] = paginator.num_pages
        users = paginator.page(paginator.num_pages)

    userList = ''
    for user in users:
        userList += user
    return userList

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

    # search for users based on criteria, then sort the results, then build an HTML list of them.
    users = search(request, searchKey, searchString)
    users = sortUsers(searchKey, users, False)
    userList = buildHtmlUserList(users)

    pageContext = getPage(request, userList)
    print(pageContext)


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
        'userList': pageContext,
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
def buildHtmlUserList(users):

    userList = []
    for user in users:
        userList.append(buildUserListEntry(user))
    return userList


''' create a list of users from search info. '''
def search(request, searchKey, searchString):
    user_results = []
    index = 0
    # build list of users to display
    if not 'all_users' in request.session:
        status = util.loadUsersIntoSession(request)
        if status != 200:
            return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not load Blackboard users!', 'name':request.session['instructor_name'] })
    for user in request.session['all_users']:
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
