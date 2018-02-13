from django.shortcuts import render, redirect
from BlackboardLearn import interface
import json
from learn import manipulate, addusers, confirmUsers

'''
    index view is for login screen and list of courses; main/initial view.
'''
def index(request):
    '''
        If there is POST data, varify that the user has access (is an instructor)
        and, if so, display list of courses. If the user doesn't have access or
        there was an error, send the user to the login screen again.
    '''
    if request.method == 'POST':
        #make sure cookies are enabled - which they will be if we get this for,
        #since the CSRF token cookie will have been set.
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            # will probably never get here since template 403_csrf.html template will be displayed
            return loginError(request, 'You must have browser cookies enabled!')

        # get the client's username and see if it exists in Bb
        user_name = request.POST.get('username')
        path = '/learn/api/public/v1/users/userName:' + user_name + '/courses'
        r = interface.get(path)
        if r == None:
            #This could be caused when either the server url is incorrect or Python can't connect to Bb at all
            return loginError(request, 'Could not connect to Blackboard!')
        elif r.status_code == 200:
            #Success!
            #user exists, log in:

            class_list = ''
            courses = {'courses':[]}

            if r.text:
                res = json.loads(r.text)

                results = res['results']
                isInstructor = False

                # Go through all the courses that the user is associated with
                # and see if the user is an instructor in any of them.
                # If the user is an instructor in any, then create an
                # entry for the course for the table in the template.
                for resu in results:
                    if resu['courseRoleId'] == 'Instructor':
                        isInstructor = True
                        courses['courses'].append(resu['courseId'])
                        class_list += buildClassEntry(resu['courseId'])

                # If user is not an instructor in any course in Blackboard, don't allow the user to log in!
                if not isInstructor:
                    return loginError(request, "You must be an instructor!")

            # Get the user's name
            path = '/learn/api/public/v1/users/userName:' + user_name + '?fields=name.given,name.family'
            r = interface.get(path)
            name = ''
            if r.text:
                res = json.loads(r.text)
                name += res['name']['given'] + " " + res['name']['family']

            # Set context for the template
            context ={
                'name': name,
                'classes': class_list,
            }

            # set the session data
            request.session['instructor_username'] = user_name
            request.session['instructor_name'] = name
            request.session['instructor_courses'] = courses
            return render(request, 'learn/courses.html', context)

        ## Handle errors from attempting to get user info from Bb, from the username user entered in login
        elif r.status_code == 404:
            return loginError(request, 'That username is not valid!')
        elif r.status_code == 403:
            return loginError(request, 'You are not authorized!')
        elif r.status_code == 400:
            return loginError(request, 'Blackboard is not available!')
        elif r.status_code == 401:
            return loginError(request, 'There was a Blackboard authentication error!')
        else:
            print("[DEBUG] views.py -> index(): r.status_code for courses get(): " + str(r.status_code))
            return loginError(request, 'Unknown error!')

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

        error_message = ''
        # if we were redirected here with an error:
        if 'courses_error_message' in request.session:
            error_message = request.session['courses_error_message']
            del request.session['courses_error_message']

        context ={
            'name': name,
            'classes': class_list,
            'error_message': error_message,
        }
        return render(request, 'learn/courses.html', context)

    else: # regular index : sign in page
        request.session.flush() # make sure all current session data is deleted before starting a new session
        request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
        return render(request, 'learn/index.html', {})

'''
    This view is responsible for managing which view is displayed based on which form action is being performed.
    The URL will remain in update().
    This view also checks for erros, such as making sure courses are selected, etc.. coming from the index view.
'''
def update(request):

    if request.method == "POST":

        #Ensure that at this point we have selected courses! And always
        #use the selected courses from POST before SESSION

        #if selected courses aren't in POST
        if not request.POST.getlist('course'):
            #if selected courses aren't in SESSION
            if 'selected_courses' not in request.session or not request.session['selected_courses']:
                #NO COURSES SELECTED!
                request.session['courses_error_message'] = "You must select a course!"
                return redirect('index')
            # selected courses must be in SESSION already.
            # No need for further action.
        else:
            # Selected courses must be in POST, put them in SESSION
            request.session['selected_courses'] = request.POST.getlist('course')

        #possibility selected courses aren't in POST but in SESSION?
        print(request.session['selected_courses'])

        action = request.POST.get('action')
        # Could be searching for a user or could be coming straight from course list

        if action == 'addUsers':
            return addusers.addUsers(request)
        elif action == 'viewUsers':
            return manipulate.viewUsers(request)
        elif action == 'removeUsers':
            return manipulate.removeUsers(request)
        elif action == 'Add':
            # Confirming selected users!
            selectedUsers = request.POST.getlist('users')
            if selectedUsers:
                request.session['selected_users'] = selectedUsers
                return confirmUsers.confirmAddUsers(request)
            else:
                # No selected users, send back to list of users to select some
                return addusers.addUsers(request, error_message="No users selected!")
        elif action == 'Confirm':
            return confirmUsers.confirmAddUsersSuccess(request)
        else:
            request.session['courses_error_message'] = "You must select an action!"
            return redirect('index')

    # Must either log in or go through selecting a course
    return redirect('index')

''' The view which doesn't have a view, per say, but deletes the session data and redirects to the login page. '''
def signout(request):
    request.session.flush()
    return redirect('index')

'''
    Get's a course ID (primary ID for the course) and returns a string with HTML tags
    which fit into the HTML table for the list of courses that the user is an instructor of.
    - Used in index() only (only view to display the instructor's courses)
'''
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

def loginError(request, message):
    request.session.set_test_cookie() #prepare for use of sessions (testing cookies are enabled)
    return render(request, 'learn/index.html', { 'error_message' : message })

'''
View for showing stats of the selected courses.
Initial view, when there is no POST, displays the list of instructor's courses.
View when there is POST of selected users, stats are displayed.
Description of requirment:
    For each instructor, create a tool to generate statistics showing the number of
    unique students that instructor has enrolled in all selected courses.
    (E.g. If the instructor is presented with a list of all courses, and checks the
    five courses that are taught this term, this tool should be able to show them
    the number of unique students they have enrolled in those five checked courses.
    A unique student count does not count a student who is taking multiple course
    from the same instructor twice.)

'''
def stats(request):
    # Class list for HTML template
    class_list = ''

    # Generate course list from session
    for course in request.session['instructor_courses']['courses']:
        # get the name of the courses for the template
        class_list += buildClassEntry(course)

    error_message = ''
    # if we were redirected here with an error:
    if 'courses_error_message' in request.session:
        error_message = request.session['courses_error_message']
        del request.session['courses_error_message']

    context ={
        'name': request.session['instructor_name'],
        'classes': class_list,
        'error_message': error_message,
    }
    return render(request, 'learn/stats.html', context)
