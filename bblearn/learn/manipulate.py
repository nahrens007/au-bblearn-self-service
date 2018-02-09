from django.shortcuts import render
from BlackboardLearn import interface
from learn import confirmUsers
import json

'''
def viewUsers(request):
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

                "Grabs individual user information to display"
                path = "/learn/api/public/v1/users/"+member
                r = interface.get(path)

                if r.text

                    res = json.loads(r.text)

                    fName = res['name']['given']
                    lName = res['name']['family']
                    email = res['contact']['email']
                    idNumber = res['studentId']

                "Gets current user's role in the course"
                path = "GET /learn/api/public/v1/courses/"+course+"/users/"+member
                r = interface.get(path)

                if r.text

                    res = json.loads(r.text)
                    courseRole = res['courseRoleId']

    context = {
    'first name': fName,
    'last name': lName,
    'email': email,
    'studentId': idNumber,
    'courseRoleId': courseRole
    }
    return render(request, 'learn/viewUsers.html', context)
'''
'''
def removeUsers(request):

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
    return render(request, 'learn/removeUsers.html', context)
'''

def addUsers(request):

    selectedUsers = request.session['selected_users']

    userList = confirmUsers.search(selectedUsers)


    context = {

        'addedUser': userList,
    }
    return render(request, 'learn/confirmAddedUsers.html', context)
