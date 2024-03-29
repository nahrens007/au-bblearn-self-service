from django.shortcuts import render, redirect
from BlackboardLearn import interface
from . import util
import json


def buildListWithRadioBoxes(request, selectedUsers):
    # build list of users to display
    userList = '<div class="tables">'
    for course in request.session['selected_courses']:

        # Need to create separate tables for each course
        '''Gets the course name'''
        path = "/learn/api/public/v1/courses/courseId:"+course+'?fields=name'
        r = interface.get(path)
        if r.status_code != 200 or not r.text:
            userList += '<div class="courseName">Course with ID: ' + course + ' could not be retrieved!</div>'
            continue
        res = json.loads(r.text)
        courseName = res['name']


        '''Creates table for each course'''
        userList += ''
        #userList += '<div class=tables>'
        userList += '<table class="userTable" style="display:table;">'
        userList += '<tr class="courseNameRow">'
        userList += '<td colspan="7"><div class="courseName">'+ courseName + '</div></td>'
        userList += '</tr>'
        userList += '<tr id="tableHeader">'
        userList += '<th class="cancelColumn">Cancel&nbsp&nbsp</th>'
        userList += '<th class="guestColumn">Guest</th>'
        userList += '<th class="TAColumn">TA</th>'
        userList += '<th>User Name</th>'
        userList += '<th>First Name</th>'
        userList += '<th>Last Name</th>'
        userList += '<th>User ID</th>'
        userList += '</tr>'

        for selectedUser in selectedUsers:
            user = util.getUser(request, selectedUser)
            if 'availability' in user and user['availability']['available'] == 'Yes':
                if('userName' in user and selectedUser in user['userName'].lower()):
                    userList += buildUserListEntry(user, course)
                    continue
        userList += '</table>'
        #userList += '</div>'
        userList += '<div class="tableBreak"></div>'
    userList += '</div>'

    userList += '<div class="submitRow">'
    userList += '<input id="submit" type="submit" name="action" value="Confirm" />'
    userList += '</div>'
    return userList


def buildUserListEntry(user, course):

    userList = ''
    userList += '<tr>'
    userList += '<td><input class="cancelColumn" type="radio" name="' + user['userName'] + ',' + course + '" value="C,' + course + '" checked="checked"><br></td>'
    userList += '<td><input class="guestColumm" type="radio" name="' + user['userName'] + ',' + course + '" value="G,' + course + '"><br></td>'
    userList += '<td><input class="TAColumm" type="radio" name="' + user['userName'] + ',' + course + '" value="TA,' + course + '"><br></td>'
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
    userList = buildListWithRadioBoxes(request, selectedUsers)


    context = {

        'addedUser': userList,
        'name': request.session['instructor_name'],
        'label': 'Are these the users you wish to add?',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)

def confirmAddUsersSuccess(request):

    htmlResponse = addToCourse(request)
    context = {

        'addedUser': '',
        'name': request.session['instructor_name'],
        'add_results': htmlResponse,
        'label': 'Here are the results of adding the users:',
    }
    return render(request, 'learn/confirmAddedUsers.html', context)

''' This function builds an HTML view of the users that were added to which courses, or not added. '''
def addToCourse(request):
    #html = '<h2>Here are the results of adding the users:</h2>'
    html = ''
    for course in request.session['selected_courses']:
        '''Gets the course name'''
        path = "/learn/api/public/v1/courses/courseId:"+course+'?fields=name'
        r = interface.get(path)
        if r.status_code != 200 or not r.text:
            html += '<div class="courseName">Course with ID: ' + course + ' could not be retrieved!</div>'
            continue
        res = json.loads(r.text)
        courseName = res['name']

        '''Creates table for each course'''
        html += '<div class="tables">'
        html += '<table class="userTable"'
        html += '<tr class="courseNameRow">'
        html += '<td colspan="6"><div class="courseName">'+ courseName + '</div></td>'
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
            userInfo = util.getUser(request, user)
            if not userInfo:
                return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not load Blackboard users!', 'name':request.session['instructor_name'] })
            path = '/learn/api/public/v1/courses/courseId:'+ course +'/users/userName:'+ user
            choice = 'C'
            payload = None
            if user + "," + course in request.POST:
                choice = request.POST.get(user + "," + course)
            if choice == 'G' + "," + course:
                # Add user to json as a guest
                payload = {
                "courseRoleId": "Guest"
                }

            elif choice == 'TA' + "," + course:
                # Add user role to json as a TA
                payload = {
                "courseRoleId": "TeachingAssistant"
                }
            else:
                ## We no longer want to add the user to the course
                html += '<tr>'
                html += '<td>' + user + '</td>'
                if 'name' in userInfo and 'given' in userInfo['name']:
                    html += '<td>' + userInfo['name']['given'] + '</td>'
                else:
                    html += '<td></td>'
                if 'name' in userInfo and 'family' in userInfo['name']:
                    html += '<td>' + userInfo['name']['family'] + '</td>'
                else:
                    html += '<td></td>'
                if 'contact' in userInfo and 'email' in userInfo['contact']:
                    html += '<td> ' + userInfo['contact']['email'] + ' </td>'
                else:
                    html += '<td></td>'
                if 'studentId' in userInfo:
                    html += '<td>' + userInfo['studentId'] + '</td>'
                else:
                    html += '<td></td>'
                html += '<td class="error_message">Cancelled</td>'
                html += '</tr>'
                continue

            # add user to course
            r = interface.put(path, json.dumps(payload))
            response = json.loads(r.text)
            if r == None:
                #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
                html += '<tr>'
                html += '<td>' + user + '</td>'
                if 'name' in userInfo and 'given' in userInfo['name']:
                    html += '<td>' + userInfo['name']['given'] + '</td>'
                else:
                    html += '<td></td>'
                if 'name' in userInfo and 'family' in userInfo['name']:
                    html += '<td>' + userInfo['name']['family'] + '</td>'
                else:
                    html += '<td></td>'
                if 'contact' in userInfo and 'email' in userInfo['contact']:
                    html += '<td> ' + userInfo['contact']['email'] + ' </td>'
                else:
                    html += '<td></td>'
                if 'studentId' in userInfo:
                    html += '<td>' + userInfo['studentId'] + '</td>'
                else:
                    html += '<td></td>'
                html += '<td class="error_message">Blackboard Error!</td>'
                html += '</tr>'
            elif r.status_code != 201:
                # 400 - Invalid request, logged in user not in same domain as user trying to add, or user is observer
                # 403 - User is system admin and logged in user isn't
                # 404 - User doesn't exist or course doesn't exist
                # 409 - User already enrolled in the course as a student, TA, Guest, or Instructor.
                html += '<tr>'
                html += '<td>' + user + '</td>'
                if 'name' in userInfo and 'given' in userInfo['name']:
                    html += '<td>' + userInfo['name']['given'] + '</td>'
                else:
                    html += '<td></td>'
                if 'name' in userInfo and 'family' in userInfo['name']:
                    html += '<td>' + userInfo['name']['family'] + '</td>'
                else:
                    html += '<td></td>'
                if 'contact' in userInfo and 'email' in userInfo['contact']:
                    html += '<td> ' + userInfo['contact']['email'] + ' </td>'
                else:
                    html += '<td></td>'
                if 'studentId' in userInfo:
                    html += '<td>' + userInfo['studentId'] + '</td>'
                else:
                    html += '<td></td>'
                html += '<td class="error_message">' + response['message'] + '</td>'
                html += '</tr>'
            else:
                # 201 - Successful enrollment
                html += '<tr>'
                html += '<td>' + user + '</td>'
                if 'name' in userInfo and 'given' in userInfo['name']:
                    html += '<td>' + userInfo['name']['given'] + '</td>'
                else:
                    html += '<td></td>'
                if 'name' in userInfo and 'family' in userInfo['name']:
                    html += '<td>' + userInfo['name']['family'] + '</td>'
                else:
                    html += '<td></td>'
                if 'contact' in userInfo and 'email' in userInfo['contact']:
                    html += '<td> ' + userInfo['contact']['email'] + ' </td>'
                else:
                    html += '<td></td>'
                if 'studentId' in userInfo:
                    html += '<td>' + userInfo['studentId'] + '</td>'
                else:
                    html += '<td></td>'
                if response['courseRoleId'] == 'TeachingAssistant':
                    html += '<td>Teaching Assistant</td>'
                else:
                    html += '<td>' + response['courseRoleId'] + '</td>'
                html += '</tr>'

        html += '</table></div>'

        html += '<div class="tableBreak"></div>'
    return html
