from django.shortcuts import render
from BlackboardLearn import interface
import json
from learn import manipulate, addusers


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



def update(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'addUsers':
            return addusers.addUsers(request)
        elif action == 'viewUsers':
            return manipulate.viewUsers(request)
        elif action == 'removeUsers':
            return manipulate.removeUsers(request)

    # In production, we should never get to this part!!!!
    return render(request, 'learn/courses.html', {'error_message':'Must select an action!'}) # will have to change
