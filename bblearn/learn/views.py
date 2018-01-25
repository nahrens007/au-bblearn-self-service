from django.shortcuts import render
from django.template import loader, engines, Template
from BlackboardLearn import LearnInterface
import json

# Erich
#secret = 'DM3ioqNu07Wlo2OxXHYgJNgeqbo8dxT9'
#key = '31496793-121b-4ab5-a068-83a9c20faed4'

# Desktop
key = "0de73b0f-68e7-48cc-b1e9-0fbefe209b74"
secret = "2Fz6vO82Y035LfoYxlQrY7xyV21SAYPK"

# Laptop
#key = "45ff63ad-e072-42fb-b6af-3c33bff846b4"
#secret = "cQXOMrwe0pxMaTQbnozmUvjCxzeGSbKM"

server = 'https://localhost:9877'

interface = LearnInterface(server, key, secret)

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
        if r.status_code == 404:
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

    if r.text:
        res = json.loads(r.text)

        results = res['results']

        for resu in results:
            if resu['courseRoleId'] == 'Instructor':
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

    print("[DEBUG] Token expires: " + str(interface.getTokenExpires()))

    context ={
        'name': name,
        'classes': class_list,
    }
    return render(request, 'learn/courses.html', context)
