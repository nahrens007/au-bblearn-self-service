from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json

def addUsers(request):
    '''
    request.POST contains:
        course - list of courses selected to add users to (as guest or TA)
            Must not be empty!
        user - dict with list of users to add to said courses.
            If empty: display empty list with search results (if search isn't empty)
            Else: create course memebership to add user to course as either guest or TA
        searchBy - string with category to search by
        searchBar - string with searchString
        action - dict with the specified action (addUsers, viewUsers, removeUsers) (handled in views.update())
    '''
    user = None
    courses = None

    user = request.POST.getlist('user')
    if 'selected_courses' in request.session:
        courses = request.session['selected_courses']

    searchKey = str(request.POST.get('searchBy'))
    searchString = str(request.POST.get('searchBar')).lower()


    if not courses:
        # no courses selected!
        return redirect('index')


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

                    if searchKey == 'None':
                        index = 0
                        userList += buildList(user)
                        continue
                    elif searchKey == 'userName':
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
    userList += '<td><input class="userCheckbox" type="checkbox" name="user" value="' + user['userName'] + '"></td>'
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
