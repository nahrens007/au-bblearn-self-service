from django.shortcuts import render
from django.template import loader, engines, Template
from BlackboardLearn import interface
import keys
import json
import learn.manipulate as manipulate



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
            #user exists, log in:

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
                                    <input id="userCheckbox" type="checkbox" name="course" value="''' + resu['courseId'] + '''">
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


def addUsers(request):
    '''
    request.POST contains:
        course - dict with list of courses selected to add users to (as guest or TA)
            Must not be empty
        user - dict with list of users to add to said courses.
            If empty: display empty list with search results (if search isn't empty)
            Else: create course memebership to add user to course as either guest or TA
        search - dict with a searchKey and searchString, to determine which user we're searching for.
            If empty: display empty list with no search results
            - searchKey = 'userName', 'studentId', 'firstName', 'lastName', 'email'
        action - dict with the specified action (addUsers, viewUsers, removeUsers)
    '''

    # NO NEED TO CHECK if request.method == 'POST' BECAUSE THE ONLY
    # WAY WE GET HERE IS FROM THE update() VIEW, WHICH VERIFIES POST
    user = request.POST.getlist('user')
    course = request.POST.getlist('course')
    search = request.POST.getlist('search')

    print()
    print(user)
    print(course)
    print(search)
    print()
    #search = request.POST.get('search') # contain searchKey and searchString
    #will replace with data from search
    searchKey = 'userName' # if searchKey is name (first/last), further configuration will be needed.

    searchString = ''.lower()

    path = '/learn/api/public/v1/users?fields=userName,name.given,name.family,contact.email,studentId,availability'
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
                if 'availability' in user and user['availability']['available'] == 'Yes':

                    if searchString in user['name']['given']:
                         userList += buildList(user)
                         continue
                    #if searchString in user['contact'][searchKey]:
                    #     userList = buildList(user)
                    #     continue
                    # else:
                        #continue


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

def update(request):
    if request.method == "POST":

        action = request.POST.get('action')
        if action == 'addUsers':
            return addUsers(request)
        elif action == 'viewUsers':
            return manipulate.viewUsers(request)
        elif action == 'removeUsers':
            return manipulate.removeUsers(request)

    return render(request, 'learn/courses.html', {'error_message':'Must select an action!'}) # will have to change

def buildList(user):

        userList = ''
        userList += '<tr>'
        userList += '<td><input class="userCheckbox" type="checkbox" name="user" value="' + user['userName'] + '"></td>'
        userList += '<td>' + user['userName'] + '</td>'
        if 'name' in user:
            userList += '<td>' + user['name']['given'] + '</td>'
            #userList += '<td>' + user['name']['family'] + '</td>'
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

        return userList
