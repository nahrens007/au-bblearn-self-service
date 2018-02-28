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
        path = "/learn/api/public/v1/courses/"+course
        r = interface.get(path)

        if r.text:
            res = json.loads(r.text)
            courseName = res['name']

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
        path = "/learn/api/public/v1/courses/"+course+"/users"
        r = interface.get(path)

        if r.text:

            res = json.loads(r.text)
            '''Grabs all the userId's from the course'''
            members = res['results']

            for member in members:
                '''Adds User Information into the table'''
                if(member['courseRoleId'] == 'TeachingAssistant'):
                    courseRole = 'Teaching Assistant'
                else:
                    courseRole = member['courseRoleId']
                user = util.getUserById(request, member['userId'])
                if not user:
                    return render(request, 'learn/viewUsers.html', { 'error_message' : 'Could not load Blackboard users!', 'name':request.session['instructor_name'] })
                tableCreator += buildViewList(course, user, courseRole)

        '''Closes Table for the course'''
        tableCreator += '</table>'
        tableCreator += '</div>'


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
        path = "/learn/api/public/v1/courses/"+course
        r = interface.get(path)

        if r.text:
            res = json.loads(r.text)
            courseName = res['name']

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
            path = "/learn/api/public/v1/courses/"+course+"/users"
            r = interface.get(path)

            if r.text:
                res = json.loads(r.text)

                "Grabs all the userId's from the course"
                members = res['results']

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
                tableCreator += '<td class="checkBoxCell"><input id="checkAll" type="checkbox" onclick="check()" ></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '</tr>'
                tableCreator += '</table>'
                tableCreator += '</div>'
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

    selectedValues = request.POST.getlist("users")

    if(not selectedValues):
        request.session['removeUserError'] = "Must select a user to remove!"
        return removeUsers(request)

    for value in selectedValues:

        user = value.split(',')[0]
        course = value.split(',')[1]
        print(user)
        print(course)
        path = '/learn/api/public/v1/courses/'+course+'/users/userName:'+user
        r = interface.delete(path)

        print(r.status_code)

    return render(request, 'learn/removeUsers.html', {})
