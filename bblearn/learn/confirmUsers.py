from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json


def search(searchString):
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
            for searchItem in searchString:
                for user in users:
                    if 'availability' in user and user['availability']['available'] == 'Yes':
                        if('userName' in user and searchItem in user['userName'].lower()):
                            userList += buildList(user,index)
                            index+=1
                            continue



    return userList

def buildList(user,userCount):

    userCount = (str)(userCount)

    userList = ''
    userList += '<tr>'
    userList += '<td><input type="radio" name="user' + userCount + '" value="' + user['userName'] + '" checked="checked">Guest<br></td>'
    userList += '<td><input class="TAColumm"  type="radio" name="user' + userCount + '" value="' + user['userName'] + '">TA<br></td>'
    userList += '<td class="userNameColumn">' + user['userName'] + '</td>'
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

''' Returns the view for confirming adding the selected users to the courses '''
def confirmAddUsers(request):

    selectedUsers = request.session['selected_users']

    userList = search(selectedUsers)


    context = {

        'addedUser': userList,
        'name': request.session['instructor_name'],
        'label': 'Are these the users you wish to add?',
        'submit': '<table class="userTable" style="display:table;">',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)

def confirmAddUsersSuccess(request):


    context = {

        'addedUser': '',
        'name': request.session['instructor_name'],
        'label': 'Successfully added user!',
        'submit': '<table class="userTable" style="display:none;">',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)
def addToCourse(request):

    for course in request.session['selected_courses']:
        for user in request.session['selected_users']:
            path = '/learn/api/public/v1/courses/'+ course +'/users/'+ user
            choice = 'C'
            if user in request.session:
                choice = request.session[user]
            if choice == 'G':
                # Add user to json as a guest
                payload = {
                "courseRoleId": "Guest"
                }
            elif choice == 'TA':
                # Add user role to json as a TA
                payload = {
                "courseRoleId": "TeachingAssistant"
                }
            else:
                # Do not add user to json
                continue
            # add user to course
            r = interface.put(path, payload)
            if r == None:
                #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
                return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
            elif r.status_code == 200:
