from django.shortcuts import render
from django.template import loader, engines, Template
from BlackboardLearn import LearnInterface
import keys
import json

interface = LearnInterface(keys.server, keys.key, keys.secret)

#Create your views here.

def index(request):
    if request.method == "POST":

        user_name = request.POST.get('username')
        path = '/learn/api/public/v1/users/userName:' + user_name + '/courses'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return render(request, 'learn/index.html', { 'error_message' : 'Could not connect to Blackboard!' })
        elif r.status_code == 200:
            #Success!

            class_list = ''
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
                            class_list += '''<tr>
                                <td id="checkBoxCell">
                                    <input class="userCheckbox" type="checkbox" name="course" value="''' + resu['courseId'] + '''">
                                </td>
                                <td>
                                    <span class="courseListing" name="course">''' + res1['name'] + '''</span>
                                </td>
                            </tr>'''
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
                    'error_message':"You must be an instructor!",
                }
                return render(request, 'learn/index.html', context)

            context ={
                'name': name,
                'classes': class_list,
            }

            return render(request, 'learn/courses.html', context)

        elif r.status_code == 404:
            return render(request, 'learn/index.html', { 'error_message' : 'That username is not valid!' })
        elif r.status_code == 403:
            return render(request, 'learn/index.html', { 'error_message' : 'You are not authorized!' })
        elif r.status_code == 400:
            return render(request, 'learn/index.html', { 'error_message' : 'Blackboard is not available!' })
        elif r.status_code == 401:
            return render(request, 'learn/index.html', { 'error_message' : 'There was a Blackboard authentication error!' })
        else:
            print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))
    else: # regular index : sign in page
        context ={
            'error_message' : ''
        }
        return render(request, 'learn/index.html', context)

def viewUsers(request):
    context = {

    }
    return render(request, 'learn/viewUsers.html', context)

def addUsers(request):

    #will be:   once we get POST working...
    #if request.method == 'POST':
    if True:
        #courses = request.POST.get('courses') # returns None if courses was not posted
        #search = request.POST.get('search') # contain searchKey and searchString
        #will replace with data from search
        searchKey = 'userName' # if searchKey is name (first/last), further configuration will be needed.
        searchString = 'ba'.lower()

        path = '/learn/api/public/v1/users?fields=userName,name,contact,studentId,availability'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!' })
        elif r.status_code == 200:
            #Success!

            userList = ''
            if r.text:
                res = json.loads(r.text)

                users = res['results']

                # build list of users to display
                for user in users:
                    if 'availability' in user and user['availability']['available'] == 'Yes' and searchString in user[searchKey]:
                        userList += '<tr>'
                        userList += '<td><input class="userCheckbox" type="checkbox" ></td>'
                        if 'userName' in user:
                            userList += '<td>' + user['userName'] + '</td>'
                        else:
                            userList += '<td></td>'
                        if 'name' in user:
                            userList += '<td>' + user['name']['given'] + '</td>'
                            userList += '<td>' + user['name']['family'] + '</td>'
                        else:
                            userList += '<td></td>'
                            userList += '<td></td>'
                        if 'contact' in user:
                            userList += '<td>' + user['contact']['email'] + '</td>'
                        else:
                            userList += '<td></td>'
                        if 'studentId' in user: #guests don't have studentId
                            userList += '<td>' + user['studentId'] + '</td>'
                        else:
                            userList += '<td></td>'
                        userList += '</tr>'

            if userList == '':
                context = {
                    'name': 'From Cookies',
                    'error_message':"No users found!",
                    'userList': '',
                }
                return render(request, 'learn/addUsers.html', context)

            context ={
                'name': 'From Cookies',
                'error_message': '',
                'userList': userList,
            }

            return render(request, 'learn/addUsers.html', context)

        elif r.status_code == 403:
            return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!' })
        elif r.status_code == 400:
            return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!' })
        elif r.status_code == 401:
            return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!' })
        else:
            print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))
    else: # regular index : sign in page
        context ={
            'name': 'From Cookies',
            'error_message': '',
            'userList': '',
        }
        return render(request, 'learn/addUsers.html', context)

    context = {

    }
    return render(request, 'learn/addUsers.html', context)
def course(request):
    if request.method == "POST":
        print(request.POST)

    return viewUsers(request)
