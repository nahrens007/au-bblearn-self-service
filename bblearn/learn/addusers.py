from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json

def addUsers(request, error_message=None):
    '''
    request.POST contains:
        if from course selection page (views.index()):
            action - value='addUsers' - used by views.update()
                no use here
            course - value='courseId' - list of courses selected
                use courses=request.POST.getlist('course')
        if from this page (search form):
            action - value='addUsers' - used by views.update()
                no use here
            searchBy - value='None', 'userName', 'firstName', 'lastName',
                                'contact', 'studentId'
                use searchKey=request.POST.get('searchBy')
            searchBar - value='searchString'
                use searchString=request.POST.get('searchBar')
    request.session contains:
        key='instructor_name', 'instructor_courses', 'instructor_username',
        or 'selected_courses'
        use: value=request.session[key]
    '''

    ''' If we are displaying an error message, then display blank page w/ no users '''
    if error_message is not None:
        context = {
            'name':request.session['instructor_name'],
            'error_message':error_message,
            'userList': '',
        }
        return render(request, 'learn/addUsers.html', context)

    ''' if there is no search bar data then this is coming straight from course selection - display no users '''
    if 'searchBar' not in request.POST:
        context = {
            'name':request.session['instructor_name'],
            'error_message': '',
            'userList': '',
        }
        return render(request, 'learn/addUsers.html', context)

    searchKey = str(request.POST.get('searchBy'))
    searchString = str(request.POST.get('searchBar')).lower()

    # search for users based on criteria, then sort the results, then build an HTML list of them.
    users = search(request, searchKey, searchString)
    users = sortUsers(searchKey, users, False)
    userList = buildHtmlUserList(request, users)

    index = 0
    if 'index' in request.session:
        index = request.session['index']
        del request.session['index']

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

''' Given a dict of users (key of 'users'), this method returns the same dict, but sorted according to searchKey '''
def sortUsers(searchKey, users, reverse):
    user_results = {'users':[]}
    if searchKey == 'userName':
        from operator import itemgetter
        user_results['users'] = sorted(users['users'], key=itemgetter('userName'), reverse=reverse)
    elif searchKey == 'firstName':
        user_results['users'] = sorted(users['users'], key=lambda e: e.get('name', {}).get('given'), reverse=reverse)
    elif searchKey == 'lastName':
        user_results['users'] = sorted(users['users'], key=lambda e: e.get('name', {}).get('family'), reverse=reverse)
    elif searchKey == 'contact':
        user_results['users'] = sorted(users['users'], key=lambda e: e.get('contact', {}).get('email'), reverse=reverse)
    elif searchKey == 'studentId':
        from operator import itemgetter
        user_results['users'] = sorted(users['users'], key=itemgetter('studentId'), reverse=reverse)
    else:
        from operator import itemgetter
        user_results['users'] = sorted(users['users'], key=itemgetter('userName'), reverse=reverse)
    return user_results

''' given a dict of users, this method builds an html list of them. '''
def buildHtmlUserList(request, users):
    userList = ''
    for user in users['users']:
        userList += buildUserListEntry(user)
    return userList


''' create a dict list of users from search info. key to list in dict is 'users' '''
def search(request, searchKey, searchString):
    user_results = {'users':[]}
    print(searchString)
    path = '/learn/api/public/v1/users?fields=userName,name.given,name.family,contact.email,studentId,availability'
    print(path)
    r = interface.get(path)
    if r == None:
        #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif r.status_code == 200:
        #Success!
        index = 0
        if r.text:
            res = json.loads(r.text)

            users = res['results']

            # build list of users to display
            for user in users:
                if 'availability' in user and user['availability']['available'] == 'Yes':
                    if searchKey == 'userName':
                        index = 1
                        if 'userName' not in user and searchString == '':
                            user['userName'] = ''
                            user_results['users'].append(user)
                        elif 'userName' in user and searchString in user['userName'].lower():
                            user_results['users'].append(user)
                        continue
                    elif searchKey == 'firstName':
                        index = 2
                        if 'name' not in user and searchString == '':
                            user['name'] = {'family':'','given':''}
                            user_results['users'].append(user)
                        elif 'name' in user and searchString in user['name']['given'].lower():
                            user_results['users'].append(user)
                        continue
                    elif searchKey == 'lastName':
                        index = 3
                        if 'name' not in user and searchString == '':
                            user['name'] = {'family':'','given':''}
                            user_results['users'].append(user)
                        elif 'name' in user and searchString in user['name']['family'].lower():
                            user_results['users'].append(user)
                        continue
                    elif searchKey == 'contact':
                        index = 4
                        if 'contact' not in user and (not searchString or not searchString.strip()):
                            user['contact'] = {'email':''}
                            user_results['users'].append(user)
                        elif 'contact' in user and searchString in user['contact']['email'].lower():
                            user_results['users'].append(user)
                        continue
                    elif searchKey == 'studentId':
                        index = 5
                        if 'studentId' not in user and searchString.strip() == '':
                            user['studentId'] = ''
                            user_results['users'].append(user)
                        elif 'studentId' in user and searchString in user['studentId']:
                            user_results['users'].append(user)
                        continue
                    else:
                        index = 0
                        user_results['users'].append(user)
                        continue
        request.session['index'] = index
        return user_results
    elif r.status_code == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif r.status_code == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif r.status_code == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    else:
        print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))

def buildUserListEntry(user):

    userList = ''
    userList += '<tr>'
    userList += '<td><input class="userCheckbox" type="checkbox" name="users" value="' + user['userName'] + '"></td>'
    userList += '<td>' + user['userName'] + '</td>'
    if 'name' in user:
        if 'given' in user['name']:
            userList += '<td>' + user['name']['given'] + '</td>'
        else:
            userList += '<td></td>'
        if 'family' in user['name']:
            userList += '<td>' + user['name']['family'] + '</td>'
        else:
            userList += '<td></td>'
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
