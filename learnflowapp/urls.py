from django.urls import path
from . import views

urlpatterns = [
    path('', views.logIn),
    path('register', views.addRegistrations),
    path('login', views.addLogin),
    path('courses', views.course),
    path('course/add', views.addcourse),
    path('notes', views.Update, name='view_courses'),
    path('notes/<int:co_id>/update', views.updateCourse, name='update_course'),
    path('course/delete',views.deleteCourse),
    path('logout', views.logOut),
    path('search-courses', views.search_courses, name='search_courses'),
    path('courses/<int:co_id>/', views.show_course, name='show_course'),
    path('grade',views.Grade),
    path('grade/add/', views.addGrade, name='add_grade'),
    path('grade/<int:co_id>', views.getGradeId, name='getGradeId'),
    path('notes/<int:co_id>/edit',views.editCourse)

]