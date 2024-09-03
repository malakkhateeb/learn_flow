from django.db import models
import bcrypt
import re
from django.conf import settings
from datetime import datetime 
from django.core.exceptions import ObjectDoesNotExist

class UserManager(models.Manager):
    def basic_validator(self, postData):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        # add keys and values to errors dictionary for each invalid field
        if len(postData['firstname']) < 2:
            errors["firstname"] = "First name should be at least 2 characters"
        if len(postData['lastname']) < 2:
            errors["lastname"] = "Last name should be at least 2 characters"
        if len(postData['password']) < 8:
            errors["password"] = "Password should be at least 8 characters"
        if  User.objects.filter(email=postData['email']).exists():
            errors['email'] = "Email already exists"
        if postData['password'] != postData['copassword']:
            errors['password_match'] = "Passwords do not match"
        if not EMAIL_REGEX.match(postData['email']):         
            errors['email'] = "Invalid email address!"
            # validated dob to required in database and age grater than 13
        return errors
    def basic_validatorlogin(self,postData):
            errors = {}
            try:
                user = User.objects.get(email=postData['email'])
            except ObjectDoesNotExist:
                errors['email'] = "Email not found."
                return errors
            if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                errors['password'] = "Invalid password."
            return errors

class User(models.Model):  
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


    
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    class_number = models.IntegerField()
    file = models.FileField(upload_to='materials/')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Note(models.Model):
    note = models.TextField()
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f"Note by {self.student} - {self.note[:20]}"



class Grade(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    student_name=models.CharField(max_length=255)
    grade = models.CharField(max_length=2)
    class_number = models.IntegerField()  

    def __str__(self):
        return f"{self.student.username} - {self.course.name} - {self.grade}"


class Estimation(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='estimations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_estimations')
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Estimation by {self.student.username} for {self.teacher.username}"
    


def all_registrations():
    return User.objects.all()


def add_newreg(POST):
    password = bcrypt.hashpw(POST['password'].encode(), bcrypt.gensalt()).decode()
    return User.objects.create(
        role=POST['role'],
        firstname=POST['firstname'],
        lastname=POST['lastname'],
        email=POST['email'],
        password=password
    )

def get_reid(session):
    return User.objects.get(id=session['reg_id'])

def all_courses():
    return Course.objects.all()

def all_users():
    return User.objects.all()

def get_course_id(co_id):
    return Course.objects.get(id=co_id)

def get_user_id(user_id):
    return User.objects.get(id=user_id)

def all_grades():
    return Grade.objects.all()


def add_courses(request, POST):
    try:
        user = User.objects.get(id=request.session['user_id'])

        # Accessing the POST data correctly
        course_name = POST.get('name')
        course_description = POST.get('description')
        class_number = POST.get('class_number')
        if not class_number or not class_number.isdigit():
            raise ValueError("Class number must be a valid number.")
        # Debugging the uploaded file
        uploaded_file = request.FILES.get('upload')
        print(f"Uploaded file: {uploaded_file}")

        # Creating the Course object
        Course.objects.create(
            name=course_name,
            description=course_description,
            class_number=class_number,
            file=uploaded_file,
            teacher=user,
        )
        print("Course added successfully!")
    except User.DoesNotExist:
        raise ValueError("User not found")
    except Exception as e:
        print(f"Error while adding course: {e}")

# ________________________________________________________
def add_grades(request, POST, co_id):

        # Retrieve the user and the course using co_id
        user = User.objects.get(id=request.session['user_id'])
        course = Course.objects.get(id=co_id)

        Grade.objects.create(
            course=course,
            student=user,
            student_name=POST.get('student_name'),
            grade=POST.get('grade'),
            class_number=POST.get('class_number'),
        )

        print("Grade added successfully!")


def update_course(POST,co_id):
    course = Course.objects.get(id=co_id)
    course.name =POST['name']
    course.desc = POST['description']
    course.save()


def edit_course(POST,co_id):
    course = Course.objects.get(id=co_id)
    course.name =POST['name']
    course.class_number=POST['class_number']
    course.desc = POST['description']
    course.save()


def delete_course(co_id):
        course = Course.objects.get(id=co_id)
        course.delete()