from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json

def addUsers(request, error_message=None):
    '''
    request.POST contains:
        user - dict with list of selected users to add to said courses.
            If empty: display empty list with search results (if search isn't empty)
            Else: create course memebership to add user to course as either guest or TA
        searchBy - string with category to search by
        searchBar - string with searchString
        action - dict with the specified action (addUsers, viewUsers, removeUsers) (handled in views.update())
    '''

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

    user = None

    if 'selected_users' in request.session:
        user = request.session['selected_users']

    searchKey = str(request.POST.get('searchBy'))
    searchString = str(request.POST.get('searchBar')).lower()

    return search(request, searchKey, searchString)

def search(request, searchKey, searchString):
    path = '/learn/api/public/v1/users?fields=userName,name.given,name.family,contact.email,studentId,availability'
    r = interface.get(path)
    if r == None:
        #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif r.status_code == 200:
        #Success!

        userList = ''
        if r.text:
            res = json.loads(r.text)

            users = res['results']

            # build list of users to display
            index = 0
            for user in users:
                if 'availability' in user and user['availability']['available'] == 'Yes':
                    if searchKey == 'userName':
                        index = 1
                        if('userName' in user and searchString in user['userName'].lower()):
                            userList += buildList(user)
                        continue
                    elif searchKey == 'firstName':
                        index = 2
                        if('name' in user and searchString in user['name']['given'].lower()):
                            userList += buildList(user)
                        continue
                    elif searchKey == 'lastName':
                        index = 3
                        if('name' in user and searchString in user['name']['family'].lower()):
                            userList += buildList(user)
                        continue
                    elif searchKey == 'contact':
                        index = 4
                        if('contact' in user and searchString in user['contact']['email'].lower()):
                            userList += buildList(user)
                        continue
                    elif searchKey == 'studentId':
                        index = 5
                        if('studentId' in user and searchString in user['studentId']):
                            userList += buildList(user)
                        continue
                    else:
                        index = 0
                        userList += buildList(user)
                        continue


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

    elif r.status_code == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif r.status_code == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif r.status_code == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    else:
        print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))

def buildList(user):

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
