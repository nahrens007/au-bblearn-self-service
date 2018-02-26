from BlackboardLearn import interface
import json

# Load all users from Bb into the Session
def loadUsersIntoSession(request):
    # See if all the users are in session. If not, get them from Bb
    if 'all_users' not in request.session:
        path = '/learn/api/public/v1/users?fields=userName,name.given,name.family,contact.email,studentId,availability'
        print(path)
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return None
        elif r.status_code == 200 and r.text:
            #Success!
            if r.text:
                res = json.loads(r.text)
                request.session['all_users'] = res['results']
        return r.status_code
    return 200 # users already in session

def getUser(request, userName):
    for user in request.session['all_users']:
        if user['userName'] == userName:
            return user
