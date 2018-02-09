from django.shortcuts import render
from BlackboardLearn import interface
import json

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

def removeUsers(request):
    context = {

    }
    return render(request, 'learn/removeUsers.html', context)
