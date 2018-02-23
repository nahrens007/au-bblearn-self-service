from django.shortcuts import render, redirect
from BlackboardLearn import interface
from . import util
import json


def search(request, searchString):
    # Ensure users are loaded from Bb
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

    users = request.session['all_users']
    # build list of users to display
    index = 0
    userList = ''
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
    userList += '<td><input class="guestColumn" type="radio" name="' + user['userName'] + '" value="C" checked="checked"><br></td>'
    userList += '<td><input class="TAColumm" type="radio" name="' + user['userName'] + '" value="G"><br></td>'
    userList += '<td><input class="cancelColumm" type="radio" name="' + user['userName'] + '" value="TA"><br></td>'
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
    if 'studentId' in user: #guests don't have studentId
        userList += '<td>' + user['studentId'] + '</td>'
    else:
        userList += '<td></td>'
    userList += '</tr>'

    return userList

''' Returns the view for confirming adding the selected users to the courses '''
def confirmAddUsers(request):

    selectedUsers = request.session['selected_users']
    userList = search(request, selectedUsers)


    context = {

        'addedUser': userList,
        'name': request.session['instructor_name'],
        'label': 'Are these the users you wish to add?',
        'submit': '<table class="userTable" style="display:table;">',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)

def confirmAddUsersSuccess(request):

    htmlResponse = addToCourse(request)
    context = {

        'addedUser': '',
        'name': request.session['instructor_name'],
        'label': htmlResponse,
        'submit': '<table class="userTable" style="display:none;">',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)

''' This function builds an HTML view of the users that were added to which courses. '''
def addToCourse(request):
    html = ''
    for course in request.session['selected_courses']:
        '''Gets the course name'''
        path = "/learn/api/public/v1/courses/"+course+'?fields=name'
        r = interface.get(path)
        if r.status_code != 200 or not r.text:
            html += '<p>Course with ID: ' + course + ' could not be retrieved!</p>'
            continue
        res = json.loads(r.text)
        courseName = res['name']

        '''Creates table for each course'''
        html += '<div class="tables">'
        html += '<table class="userTable"'
        html += '<tr class="courseNameRow">'
        html += '<div class="courseName">'+ courseName + '</div>'
        html += '</tr>'
        html += '<tr id="tableHeader">'
        html += '<th>User Name</th>'
        html += '<th>First Name</th>'
        html += '<th>Last Name</th>'
        html += '<th> Email </th>'
        html += '<th>User ID</th>'
        html += '<th>Status</th>'
        html += '</tr>'
        for user in request.session['selected_users']:
            path = '/learn/api/public/v1/courses/'+ course +'/users/userName:'+ user
            choice = 'C'
            payload = None
            if user in request.POST:
                choice = request.POST.get(user)
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
                continue


            # add user to course
            r = interface.put(path, json.dumps(payload))
            print(r.text)
            if r == None:
                #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
                return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
            elif r.status_code == 409:
                # User already enrolled in the course as a student, TA, Guest, or Instructor.
                print("User already enrolled!")
            elif r.status_code != 201:
                print('error adding a user!')
                print(r.status_code)
            else:
                print('success!')
    return html
