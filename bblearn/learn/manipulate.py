from django.shortcuts import render
from BlackboardLearn import interface
from learn import confirmUsers
import json


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
            courseName = res['courseId']

        '''Creates table for each course'''
        tableCreator += '<div class="tables">'
        tableCreator += '<table class="userTable"'
        tableCreator += '<tr id="courseName">'
        tableCreator += '<th>'+courseName+'</th>'
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
                tableCreator += buildViewList(course, member['userId'])

        '''Closes Table for the course'''
        tableCreator += '</table>'
        tableCreator += '</div>'


    context = {
    'name': request.session['instructor_name'],
    'tableCreator': tableCreator,
    }
    return render(request, 'learn/viewUsers.html', context)

def removeUsers(request):

    courses = request.POST.getlist('course')

    tableCreator = ''

    for course in courses:

        '''Gets the course name'''
        path = "/learn/api/public/v1/courses/"+course
        r = interface.get(path)

        if r.text:
            res = json.loads(r.text)
            courseName = res['courseId']

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

            "Gets all users from course"
            path = "/learn/api/public/v1/courses/"+course+"/users"
            r = interface.get(path)

            if r.text:
                res = json.loads(r.text)

                "Grabs all the userId's from the course"
                members = res['results']

                for member in members:

                    "Gets current user's role in the course"
                    path = "/learn/api/public/v1/courses/"+course+"/users/"+member['userId']
                    r = interface.get(path)

                    if r.text:
                        res = json.loads(r.text)
                        courseRole = res['courseRoleId']

                        '''Checks for all teaching assistants and guests in the selected courses'''
                        if(courseRole == 'TeachingAssistant'):
                            tableCreator += buildRemoveList(course, member['userId'], 'Teaching Assistant')
                        elif(courseRole == 'Guest'):
                            tableCreator += buildRemoveList(course, member['userId'], 'Guest')
                tableCreator += '<tr id="submitRow">'
                tableCreator += '<td class="checkBoxCell"><input id="checkAll" type="checkbox" onclick="check()" ></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td></td>'
                tableCreator += '<td><input id="submit" type="button" value="Remove"></td>'
                tableCreator += '</tr>'
                tableCreator += '</table>'
                tableCreator += '</div>'
    context = {
    'name': request.session['instructor_name'],
    'tableCreator': tableCreator,
    }

    return render(request, 'learn/removeUsers.html', context)

def buildViewList(course, member):

    userList = ''
    '''Grabs individual user information to display'''
    path = "/learn/api/public/v1/users/"+member
    r = interface.get(path)

    if r.text:

        res = json.loads(r.text)

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

        '''Gets current user's role in the course'''
        path = "/learn/api/public/v1/courses/"+course+"/users/"+member
        r = interface.get(path)

        if r.text:

            res = json.loads(r.text)
            courseRole = res['courseRoleId']

            if(courseRole == 'TeachingAssistant'):
                courseRole = 'Teaching Assistant'

            userList +=  '<td>' + courseRole + '</td>'


        userList += '</tr>'

    return userList

def buildRemoveList(course, member, role):

    userList = ''

    '''Grabs individual user information to display'''
    path = "/learn/api/public/v1/users/"+member
    r = interface.get(path)

    if r.text:

        res = json.loads(r.text)

        userList += '<tr>'
        userList += '<td class="checkBoxCell"><input class="userCheckbox" type="checkbox" ></td>'
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
