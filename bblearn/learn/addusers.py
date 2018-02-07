from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json

def addUsers(request):
    '''
    request.POST contains:
        course - dict with list of courses selected to add users to (as guest or TA)
            Must not be empty
        user - dict with list of users to add to said courses.
            If empty: display empty list with search results (if search isn't empty)
            Else: create course memebership to add user to course as either guest or TA
        searchBy - string with category to search by
        searchBar - string with searchString
        action - dict with the specified action (addUsers, viewUsers, removeUsers)
    '''

    # NO NEED TO CHECK if request.method == 'POST' BECAUSE THE ONLY
    # WAY WE GET HERE IS FROM THE update() VIEW, WHICH VERIFIES POST
    user = request.POST.getlist('user')
    courses = request.POST.getlist('course')
    #searchBy = request.POST.getlist('searchBy')
    #searchBar = request.POST.getlist('searchBar')
    searchKey = str(request.POST.get('searchBy')) # if searchKey is name (first/last), further configuration will be needed.
    searchString = str(request.POST.get('searchBar')).lower()

    if not courses:
        # no courses selected!
        return redirect('index')

    print()
    print(request.POST)
    print()
    #search = request.POST.get('search') # contain searchKey and searchString
    #will replace with data from search
    #searchKey = 'email' # if searchKey is name (first/last), further configuration will be needed.

    #searchString = 'ba'.lower()

    path = '/learn/api/public/v1/users?fields=userName,name.given,name.family,contact.email,studentId,availability'
    r = interface.get(path)
    if r == None:
        #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif r.status_code == 200:
        #Success!

        userList = ''
        if r.text:
            res = json.loads(r.text)

            users = res['results']

            # build list of users to display
            index = 0
            for user in users:
                if 'availability' in user and user['availability']['available'] == 'Yes':

                    if searchKey == 'None':
                        index = 0
                        userList += buildList(user)
                        continue
                    elif searchKey == 'userName' and searchString in user['userName'] and 'userName' in user:
                        index = 1
                        userList += buildList(user)
                        continue
                    elif searchKey == 'firstName' and searchString in user['name']['given'] and 'name' in user:
                        index = 2
                        userList += buildList(user)
                        continue
                    elif searchKey == 'lastName' and searchString in user['name']['family']  and 'name' in user:
                        index = 3
                        userList += buildList(user)
                        continue
                    elif searchKey == 'contact' and 'contact' in user and searchString in user['contact']['email']:
                        index = 4
                        userList += buildList(user)
                        continue
                    elif searchKey == 'studentId' and 'studentId' in user and searchString in user['studentId']:
                        index = 5
                        userList += buildList(user)
                        continue
                    else:
                        continue


        if userList == '':
            context = {
                'name':request.session['instructor_name'],
                'error_message':"No users found!",
                'userList': '',
                'optionIndex': index,
            }
            return render(request, 'learn/addUsers.html', context)

        context ={
            'name': request.session['instructor_name'],
            'error_message': '',
            'userList': userList,
            'optionIndex': index,
        }

        return render(request, 'learn/addUsers.html', context)

    elif r.status_code == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif r.status_code == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif r.status_code == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    else:
        print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))


def buildList(user):

    userList = ''
    userList += '<tr>'
    userList += '<td><input class="userCheckbox" type="checkbox" name="user" value="' + user['userName'] + '"></td>'
    userList += '<td>' + user['userName'] + '</td>'
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

    return userList
