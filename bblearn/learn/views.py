from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json
from learn import manipulate, addusers


#Create your views here.
def index(request):
    # IF the user logged in, i.e., there is POST data
    if request.method == 'POST':
        #make sure cookies are enabled - which they will be if we get this for,
        #since the CSRF token cookie will have been set.
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            return render(request, 'cookies_not_enabled.html', {})

        # get the client's username and see if it exists in Bb
        user_name = request.POST.get('username')
        path = '/learn/api/public/v1/users/userName:' + user_name + '/courses'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
            return render(request, 'learn/index.html', { 'error_message' : 'Could not connect to Blackboard!' })
        elif r.status_code == 200:
            #Success!
            #user exists, log in:

            class_list = ''
            courses = {'courses':[]}

            if r.text:
                res = json.loads(r.text)

                results = res['results']
                isInstructor = False

                for resu in results:
                    if resu['courseRoleId'] == 'Instructor':
                        isInstructor = True
                        courses['courses'].append(resu['courseId'])
                        class_list += buildClassEntry(resu['courseId'])

                # If user is not an instructor in any course in Blackboard, don't allow the user to log in!
                if not isInstructor:
                    context = {
                    'error_message':"You must be an instructor!",
                    }
                    request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
                    return render(request, 'learn/index.html', context)

            # Get the user's name
            path = '/learn/api/public/v1/users/userName:' + user_name + '?fields=name.given,name.family'
            r = interface.get(path)

            name = ''

            if r.text:
                res = json.loads(r.text)

                name += res['name']['given'] + " " + res['name']['family']


            context ={
                'name': name,
                'classes': class_list,
            }

            # set the session data
            request.session['instructor_username'] = user_name
            request.session['instructor_name'] = name
            request.session['instructor_courses'] = courses
            return render(request, 'learn/courses.html', context)

        elif r.status_code == 404:
            request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
            return render(request, 'learn/index.html', { 'error_message' : 'That username is not valid!' })
        elif r.status_code == 403:
            request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
            return render(request, 'learn/index.html', { 'error_message' : 'You are not authorized!' })
        elif r.status_code == 400:
            request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
            return render(request, 'learn/index.html', { 'error_message' : 'Blackboard is not available!' })
        elif r.status_code == 401:
            request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
            return render(request, 'learn/index.html', { 'error_message' : 'There was a Blackboard authentication error!' })
        else:
            print("[DEBUG] r.status_code for courses get(): " + str(r.status_code))

    # if redirected here from another page, i.e., user is already logged in
    #   and has session data saved.
    elif 'instructor_courses' in request.session and 'instructor_name' in request.session and 'instructor_username' in request.session:

        name = request.session['instructor_name']

        # Class list for HTML template
        class_list = ''

        # user is already logged in - generate course list from session
        for course in request.session['instructor_courses']['courses']:
            # get the name of the courses for the template
            class_list += buildClassEntry(course)

        context ={
            'name': name,
            'classes': class_list,
        }
        return render(request, 'learn/courses.html', context)

    else: # regular index : sign in page
        request.session.flush() # make sure all current session data is deleted before starting a new session
        context = {}

        request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
        return render(request, 'learn/index.html', context)



def update(request):
    if request.method == "POST":
        courses = None
        if 'selected_courses' not in request.session:
            courses = request.POST.getlist('course')
            #no courses selected!
            if not courses:
                return redirect('index')
            request.session['selected_courses'] = courses

        action = request.POST.get('action')
        if action == 'addUsers':
            return addusers.addUsers(request)
        elif action == 'viewUsers':
            return manipulate.viewUsers(request)
        elif action == 'removeUsers':
            return manipulate.removeUsers(request)

    # Must either log in or go through selecting a course
    return redirect('index')

def signout(request):
    request.session.flush()
    return redirect('index')

def buildClassEntry(courseId):
    path = '/learn/api/public/v1/courses/' + courseId
    response = interface.get(path)
    if response.text:
        resJson = json.loads(response.text)
        return '''<tr>
            <td id="checkBoxCell">
                <input id="userCheckbox" type="checkbox" name="course" value="''' + courseId + '''">
            </td>
            <td>
                <span class="courseListing" name="course">''' + resJson['name'] + '''</span>
            </td>
        </tr>'''
    return ''
