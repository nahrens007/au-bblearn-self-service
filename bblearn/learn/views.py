from django.shortcuts import render
from django.template import loader, engines, Template
from BlackboardLearn import LearnInterface
import static
import json

interface = LearnInterface(static.server, static.key, static.secret)

#Create your views here.

def index(request):
    template = loader.get_template('learn/index.html')
    context ={

    }
    return render(request, 'learn/index.html', context)

def courses(request):
    user_name =''
    class_list =''
    r = None


    if request.method == "POST":
        user_name = request.POST.get('username')
        path = '/learn/api/public/v1/users/userName:' + user_name + '/courses'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return render(request, 'learn/error.html', { 'error' : 'Error Connecting: The server could not connect to Blackboard!' })
        elif r.status_code == 200:
            #Success!

            isInstructor = False

            if r.text:
                res = json.loads(r.text)

                results = res['results']


                for resu in results:
                    if resu['courseRoleId'] == 'Instructor':
                        isInstructor = True
                        path = '/learn/api/public/v1/courses/' + resu['courseId']
                        r1 = interface.get(path)
                        if r1.text:
                            res1 = json.loads(r1.text)
                            #html += "<a href='course.py?courseId=" + resu['courseId'] + "'>" + courseId + "</a><br/>"
                            class_list += '<label class="container"><input type="checkbox"><button class="checkMark" name="course" type="submit" value="' + resu['courseId'] + '">' + res1['name'] + '</button></label>'

            # Get the user's name
            path = '/learn/api/public/v1/users/userName:' + user_name
            r = interface.get(path)

            name = ''

            if r.text:
                res = json.loads(r.text)

                name_data = res['name']
                name += name_data['given'] + " " + name_data['family']

            print("Token expires: " + str(interface.getTokenExpires()))

            if not isInstructor:
                context = {
                    'name':name,
                    'message':"I'm sorry, you are not an instructor in any course. You do not have access to this tool.",
                }
                return render(request, 'learn/notInstructor.html', context)

            context ={
                'name': name,
                'classes': class_list,
            }

            return render(request, 'learn/courses.html', context)
        elif r.status_code == 404:
            return render(request, 'learn/error.html', { 'error' : 'Error 404: The username you entered is not valid!' })
        elif r.status_code == 403:
            return render(request, 'learn/error.html', { 'error' : 'Error 403: You are not authorized!' })
        elif r.status_code == 400:
            return render(request, 'learn/error.html', { 'error' : 'Error 400: There was an error communicating with Blackboard!' })
        elif r.status_code == 401:
            return render(request, 'learn/error.html', { 'error' : 'Error 401: There was an error authenticating this app with Blackboard Learn!' })
        else:
            print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))
    else:
        # How did we get this far? Should have had a post request with the username.
        return render(request, 'learn/error.html', { 'error' : 'No POST request!' })


def viewUsers(request):
    context = {

    }
    return render(request, 'learn/viewUsers.html', context)

def addUsers(request):
    context = {

    }
    return render(request, 'learn/addUsers.html', context)
