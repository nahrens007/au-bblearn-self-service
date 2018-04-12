from BlackboardLearn import interface
import json

def getUserFromBlackboardById(request, id):
    path = '/learn/api/public/v1/users/' + id + '?fields=id,userName,name.given,name.family,contact.email,studentId,availability'
    r = interface.get(path)
    user = None
    if r == None:
        #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
        return None
    elif r.status_code == 200 and r.text:
        #Success!
        user = json.loads(r.text)
        addUserToSession(request, user)
    return user

def addUserToSession(request, user):
    if 'all_users' not in request.session:
        loadUsersIntoSession(request)
    request.session['all_users'].append(user)
    return

# Load all users from Bb into the Session
def loadUsersIntoSession(request):
    # See if all the users are in session. If not, get them from Bb
    if 'all_users' not in request.session:
        path = '/learn/api/public/v1/users?fields=id,userName,name.given,name.family,contact.email,studentId,availability'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return None
        elif r.status_code == 200 and r.text:
            #Success!
            res = json.loads(r.text)
            request.session['all_users'] = res['results']
        return r.status_code
    return 200 # users already in session

def getUser(request, userName):
    status = loadUsersIntoSession(request)
    '''
    if status == None:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif status == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif status == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif status == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    elif status != 200:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Error! Status code: ' + str(status), 'name': request.session['instructor_name'] })
    '''
    if status != 200:
        return None
    for user in request.session['all_users']:
        if user['userName'] == userName:
            return user

def getUserById(request, userId):
    status = loadUsersIntoSession(request)
    '''
    if status == None:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Could not connect to Blackboard!', 'name':request.session['instructor_name'] })
    elif status == 403:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'You are not authorized!', 'name': request.session['instructor_name'] })
    elif status == 400:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Bad request!', 'name': request.session['instructor_name'] })
    elif status == 401:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'There was a Blackboard authentication error!', 'name': request.session['instructor_name'] })
    elif status != 200:
        return render(request, 'learn/addUsers.html', { 'error_message' : 'Error! Status code: ' + str(status), 'name': request.session['instructor_name'] })
    '''
    if status != 200:
        return None
    for user in request.session['all_users']:
        if user['id'] == userId:
            return user
    #try finding the user from Blackboard
    return getUserFromBlackboardById(request, userId)

def getCourseInfo(courseId):
    path = '/learn/api/public/v1/courses/' + courseId
    response = interface.get(path)
    if response.text:
        return json.loads(response.text)
    return None

def getCourseInfoByCourseId(courseId):
    path = "/learn/api/public/v1/courses/courseId:"+courseId
    r = interface.get(path)
    if r.status_code == 200 and r.text:
        return json.loads(r.text)
    return None

def getUsersFromCourseByCourseId(courseId):
    path = "/learn/api/public/v1/courses/courseId:"+courseId+"/users"
    r = interface.get(path)

    if r.status_code == 200 and r.text:
        res = json.loads(r.text)
        '''Grabs all the userId's from the course'''
        return res['results']
    return None
