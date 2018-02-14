from django.shortcuts import render
from BlackboardLearn import interface
from learn import confirmUsers
import json


def viewUsers(request):
    # not possible to get here without selected courses in SESSION from views.update()
    courses = request.session['selected_courses']

    tableCreator = ''
    for course in courses:

        '''Creates table for each course'''
        tableCreator += '<table class="userTable"'
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

    context = {
    'name': request.session['instructor_name'],
    'tableCreator': tableCreator,
    }
    return render(request, 'learn/viewUsers.html', context)

'''def removeUsers(request):

        courses = request.POST.getlist('course')


        for course in courses:

            "Gets all users from course"
            path = "/learn/api/public/v1/courses/"+course+"/users"
            r = interface.get(path)

            if r.text

                res = json.loads(r.text)
                "Grabs all the userId's from the course"
                members = res['results']['userId']

                for member in members:

                        "Gets current user's role in the course"
                        path = "GET /learn/api/public/v1/courses/"+course+"/users/"+member
                        r = interface.get(path)

                        if r.text

                            res = json.loads(r.text)
                            courseRole = res['courseRoleId']

                            "Check to see if the user is a TA or Guest since those will be the only"
                            "Users that can be removed."
                            if(courseRole == "teaching assistant")

                                    "Grabs individual user information to display"
                                    path = "/learn/api/public/v1/users/"+member
                                    r = interface.get(path)

                                    if r.text

                                        res = json.loads(r.text)

                                        fName = res['name']['given']
                                        lName = res['name']['family']
                                        email = res['contact']['email']
                                        idNumber = res['studentId']

                            elif(courseRole == "guest")

                                    "Grabs individual user information to display"
                                    path = "/learn/api/public/v1/users/"+member
                                    r = interface.get(path)

                                    if r.text

                                        res = json.loads(r.text)

                                        fName = res['name']['given']
                                        lName = res['name']['family']
                                        email = res['contact']['email']
                                        idNumber = res['studentId']

    context = {
    'first name': fName,
    'last name': lName,
    'email': email,
    'studentId': idNumber,
    'courseRoleId': courseRole,
    }
    return render(request, 'learn/removeUsers.html', context)'''

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

            userList +=  '<td>' + courseRole + '</td>'


        userList += '</tr>'

    return userList
