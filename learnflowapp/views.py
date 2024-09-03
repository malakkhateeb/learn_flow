from django.shortcuts import render, redirect
from . import models
from django.contrib import messages
import bcrypt
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse


def logIn(request):
    return render(request, 'index.html')
# -------------------------------------------------------------------------
# this method to add new user to database
def addRegistrations(request):
    if request.method == 'POST':
        errors = models.User.objects.basic_validator(request.POST)
        print(f"Validation errors: {errors}")
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return redirect('/')
        else:
            user = models.add_newreg(request.POST)
            print(f"User registered: {user}")
            request.session['reg_id'] = user.id 
            messages.success(request, "Successfully registered")
            return redirect('/')  # Redirect to courses or any other relevant page after registration
    return redirect('/')

# -------------------------------------------------------------------------
#this method to add the email and passswored and hash the password and returns the error when logi with email and password invalid
def addLogin(request):
    if request.method == 'POST':
        errors = models.User.objects.basic_validatorlogin(request.POST)
        # Check if the errors dictionary has anything in it
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            # Redirect the user back to the form to fix the errors
            return redirect('/')
        else:
            user = models.User.objects.filter(email=request.POST['email'])
            if user:
                logged_user = user[0]
                if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                    request.session['user_id'] = logged_user.id
                    # Redirect based on the user's role
                    if logged_user.role == 'teacher':
                        return redirect('/courses')
                    else:
                        return redirect('/notes')
                else:
                    messages.error(request, 'Invalid login credentials')
                    return redirect('/')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('/')
    
    return redirect('/')

# _____________________________________________________________________________________________
# this methode to render the page to make the teacher when logged in add courses 
def course(request):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'courses': models.all_courses(),
        'user': models.get_user_id(request.session['user_id'])
    }
    
    return render(request, 'addcourse.html', context)
# _______________________________________________________________________________________________
# this method to render the table and add the courses in the table 
def addcourse(request):
    if request.method == 'POST':
        try:
            # Call add_courses with request and request.POST
            models.add_courses(request, request.POST)
            return redirect('/courses')
        except Exception as e:
            # Log or handle the exception
            print(f"Error: {e}")
            return render(request, 'teacher.html', {'error': str(e)})
    else:
        context={
            'user': models.get_user_id(request.session['user_id'])
        }
        # Render the form template for GET requests
        return render(request, 'teacher.html', context)


# _______________________________________________
# this methode to show course for students 
def Update(request):
    if 'user_id' not in request.session:
        return redirect('/')
    
    context = {
        'courses': models.all_courses(),
        'user': models.get_user_id(request.session['user_id'])
    }
    
    return render(request, 'viewcourse.html', context)

# ___________________________________________________________
# this one 
def updateCourse(request, co_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'course': models.get_course_id(co_id),
        'user': models.get_user_id(request.session['user_id'])
    }
    if request.method == 'POST':
    
        models.update_course(request.POST,co_id)
        return redirect(f'/notes/{co_id}')
        
    return render(request, 'student.html', context)
#_________________________________________________________



@require_GET
def search_courses(request):
    query = request.GET.get('query', '')
    if query:
        courses = models.Course.objects.filter(name__icontains=query)
        course_list = []
        for course in courses:
            course_list.append({
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'class_number': course.class_number,
                'teacher': f'{course.teacher.firstname} {course.teacher.lastname}',
            })
        return JsonResponse(course_list, safe=False)
    else:
        return JsonResponse([], safe=False)


def show_course(request, co_id):
    if 'user_id' not in request.session:
        return redirect('/')
    
    context = {
        'course': models.get_course_id(co_id),
        'courses': models.all_courses()
    }
    
    return render(request, 'student.html', context)

def Grade(request):
    if 'user_id' not in request.session:
        return redirect('/')

    context = {
        'courses': models.get_course_id(request.GET.get('id')),
        'user': models.get_user_id(request.session['user_id']),
        'grades':models.all_grades(),
    }
    print(context['courses'])
    #print courses ids
    return render(request, 'addgrade.html', context)

def addGrade(request):
    if 'user_id' not in request.session:
        return redirect('/')

    if request.method == 'POST':
        co_id = request.POST.get('co_id')
        print(f"co_id received: {co_id}")  

        if not co_id:
            print("co_id is missing or empty!")
            return redirect('/grade')

        try:

            course = models.Course.objects.get(id=co_id)
            user = models.User.objects.get(id=request.session['user_id'])
        except models.Course.DoesNotExist:
            print(f"Course with id {co_id} does not exist!")
            return redirect('/grade')

        context = {
            'course': course,
            'user': user,
            'grades':models.all_grades(),
        }

        models.add_grades(request, request.POST, co_id)
        print('malak')
        return redirect(f'/grade/{co_id}')    #

    return render(request, 'grades.html', context)

def getGradeId(request, co_id):
    context = {
        "course" : models.Course.objects.get(id=co_id),
        'grades':models.all_grades(),
        
    }
    return render( request,'grades.html',context)


def editCourse(request, co_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'course': models.get_course_id(co_id),
        'user': models.get_user_id(request.session['user_id'])
    }
    if request.method == 'POST':
    
        models.edit_course(request.POST,co_id)
        return redirect(f'/notes/{co_id}')
        
    return render(request, 'editcourse.html', context)


def deleteCourse(request):
    models.delete_course(request.POST['id'])
    return redirect('/courses')

def logOut(request):
    request.session.clear()
    return redirect('/')




