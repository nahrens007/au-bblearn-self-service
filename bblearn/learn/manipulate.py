from django.shortcuts import render
from BlackboardLearn import interface
from learn import confirmUsers
import json
from . import util


def viewUsers(request):
    # not possible to get here without selected courses in SESSION from views.update()
    courses = request.session['selected_courses']

    tableCreator = ''
    for course in courses:

        '''Gets the course name'''
        courseInfo = util.getCourseInfoByCourseId(course)
        courseName = courseInfo['name']

        '''Creates table for each course'''
        tableCreator += '<div class="tables">'
        tableCreator += '<table class="userTable"'
        tableCreator += '<tr class="courseNameRow">'
        tableCreator += '<div class="courseName">'+ courseName + '</div>'
        tableCreator += '</tr>'
        tableCreator += '<tr id="tableHeader">'
        tableCreator += '<th>User Name</th>'
        tableCreator += '<th>First Name</th>'
        tableCreator += '<th>Last Name</th>'
        tableCreator += '<th> Email </th>'
        tableCreator += '<th>User ID</th>'
        tableCreator += '<th>Status</th>'
        tableCreator += '</tr>'

        '''Gets all users from course'''
        members = util.getUsersFromCourseByCourseId(course)
        if not members:
            return render(request, 'learn/viewUsers.html', {'error_message': 'Could not recover users from the course.'})

        for member in members:
            '''Adds User Information into the table'''
            if(member['courseRoleId'] == 'TeachingAssistant'):
                courseRole = 'Teaching Assistant'
            else:
                courseRole = member['courseRoleId']

            # Get the user from session
            user = util.getUserById(request, member['userId'])
            if not user:
                return render(request, 'learn/viewUsers.html', { 'error_message' : 'Could not load Blackboard users!', 'name':request.session['instructor_name'] })

            tableCreator += buildViewList(course, user, courseRole)

        '''Closes Table for the course'''
        tableCreator += '</table>'
        tableCreator += '</div>'
        tableCreator +="<div class='tableBreak'></div>"


    context = {
    'name': request.session['instructor_name'],
    'tableCreator': tableCreator,
    }
    return render(request, 'learn/viewUsers.html', context)

def removeUsers(request):
    courses = request.session['selected_courses']

    tableCreator = ''
    errorMessage = ''

    if('removeUserError' in request.session):
        errorMessage = request.session['removeUserError']

    for course in courses:

        '''Gets the course name'''
        courseInfo = util.getCourseInfoByCourseId(course)
        courseName = courseInfo['name']

        '''Creates table for each course'''
        tableCreator += '<div class="tables">'
        tableCreator += '<table class="userTable">'
        tableCreator += '<tr class="courseNameRow">'
        tableCreator += '<div class="courseName">'+ courseName + '</div>'
        tableCreator += '</tr>'
        tableCreator += '<tr id="tableHeader">'
        tableCreator += '<th class="checkBoxCell"></th>'
        tableCreator += '<th>User Name</th>'
        tableCreator += '<th>First Name</th>'
        tableCreator += '<th>Last Name</th>'
        tableCreator += '<th>User ID</th>'
        tableCreator += '<th>Status</th>'
        tableCreator += '</tr>'

        '''Gets all users from course'''
        '''Gets all users from course'''
        members = util.getUsersFromCourseByCourseId(course)
        if not members:
            return render(request, 'learn/removeUsers.html', {'error_message': 'Could not recover users from the course.'})

        for member in members:

            "Gets current user's role in the course"
            courseRole = member['courseRoleId']
            '''Checks for all teaching assistants and guests in the selected courses'''
            user = util.getUserById(request, member['userId'])
            if not user:
                return render(request, 'learn/removeUsers.html', { 'error_message' : 'Could not load Blackboard users!', 'name':request.session['instructor_name'] })
            if(courseRole == 'TeachingAssistant'):
                tableCreator += buildRemoveList(course, user, 'Teaching Assistant')
            elif(courseRole == 'Guest'):
                tableCreator += buildRemoveList(course, user, 'Guest')
        tableCreator += '<tr id="submitRow">'
        tableCreator += '<td></td>'
        tableCreator += '<td></td>'
        tableCreator += '<td></td>'
        tableCreator += '<td></td>'
        tableCreator += '<td></td>'
        tableCreator +='<td></td>'
        tableCreator += '</tr>'
        tableCreator += '</table>'
        tableCreator += '</div>'


        tableCreator +="<div class='tableBreak'></div>"

    context = {
    'name': request.session['instructor_name'],
    'tableCreator': tableCreator,
    'error_message': errorMessage,
    }

    return render(request, 'learn/removeUsers.html', context)

def buildViewList(course, res, role):

    userList = ''
    userList += '<tr>'
    userList += '<td>' + res['userName'] + '</td>'
    if 'name' in res:
        if 'given' in res['name']:
            userList += '<td>' + res['name']['given'] + '</td>'
        else:
            userList += '<td></td>'
        if 'family' in res['name']:
            userList += '<td>' + res['name']['family'] + '</td>'
        else:
            userList += '<td></td>'
    else:
        userList += '<td></td>'
        userList += '<td></td>'
    if 'contact' in res:
        userList += '<td>' + res['contact']['email'] + '</td>'
    else:
        userList += '<td></td>'
    if 'studentId' in res: #guests don't have studentId
        userList += '<td>' + res['studentId'] + '</td>'
    else:
        userList += '<td></td>'
    userList +=  '<td>' + role + '</td>'
    userList += '</tr>'

    return userList

def buildRemoveList(course, res, role):

    userList = ''
    userList += '<tr>'
    userList += '<td class="checkBoxCell"><input class="userCheckbox" type="checkbox" value ="'+res['userName']+','+course+'" name = "users" ></td>'
    userList += '<td>' + res['userName'] + '</td>'
    if 'name' in res:
        if 'given' in res['name']:
            userList += '<td>' + res['name']['given'] + '</td>'
        else:
            userList += '<td></td>'
        if 'family' in res['name']:
            userList += '<td>' + res['name']['family'] + '</td>'
        else:
            userList += '<td></td>'
    else:
        userList += '<td></td>'
        userList += '<td></td>'
    if 'studentId' in res: #guests don't have studentId
        userList += '<td>' + res['studentId'] + '</td>'
    else:
        userList += '<td></td>'

    userList +=  '<td>' + role + '</td>'
    userList += '</tr>'

    return userList

def submitRemoveUsers (request):

    removeResults = '<table class = "userTable">'
    removeResults += '<th> User Name </th>'
    removeResults += '<th> Result </th>'
    removeResults += '<th> Course </th>'

    selectedValues = request.POST.getlist("users")

    if(not selectedValues):
        request.session['removeUserError'] = "Must select a user to remove!"
        return removeUsers(request)

    for value in selectedValues:

        user = value.split(',')[0]
        course = value.split(',')[1]

        path = '/learn/api/public/v1/courses/courseId:'+course+'/users/userName:'+user
        r = interface.delete(path)

        removeResults += '<tr>'
        if r.status_code == '404':
            removeResults += failedToRemove(user, course, "Not Found")
        elif r.status_code == '403':
            removeResults += failedToRemove(user, course, "Forbidden")
        elif r.status_code == '400':
            removeResults += failedToRemove(user, course, "Bad Request")
        else:
            removeResults += successfullyRemove(user, course)
        removeResults += '</tr>'
    removeResults += '</table>'

    context = {
        'name': request.session['instructor_name'],
        'removeResults': removeResults,
    }

    return render(request, 'learn/submitRemoveUsers.html', context)

def failedToRemove(user, course, reason):
    userResult = ""
    userResult += '<td>'+ user + '</td>'
    userResult += '<td>' + " not removed from </td>"
    userResult += '<td>' + course + '</td>'
    userResult += '<td>Error: ' + reason + '</td>'

    return userResult

def successfullyRemove(user, course):
    userResult = ""
    userResult += '<td>'+ user + '</td>'
    userResult += "<td> was removed from </td>"
    userResult += '<td>' + course + '</td>'

    return userResult
