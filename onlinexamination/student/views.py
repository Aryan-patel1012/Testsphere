from django.shortcuts import render,redirect
from . import forms,models
from django.db.models import Sum 
from exam.models import Course 
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect , HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from .models import Exam
from django.urls import reverse  


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    exam_timer=course.exam_timer
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks , 'exam_timer': exam_timer})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    #breakpoint()
    course=Course.objects.get(id=pk)
    print("id",course.id)
    questions=QMODEL.Question.objects.all().filter(course=course)
    exam_timer=course.exam_timer
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions ,'exam_timer': exam_timer})
    response.set_cookie('course_id',course.id)
    return response


# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def calculate_marks_view(request):
#     breakpoint()
#     if request.COOKIES.get('course_id') is not None:
#         course_id = request.COOKIES.get('course_id')
#         course=QMODEL.Course.objects.get(id=course_id)
        
#         total_marks=0
#         questions=QMODEL.Question.objects.all().filter(course=course)
#         for i in range(len(questions)):
            
#             selected_ans = request.COOKIES.get(str(i+1))
#             actual_answer = questions[i].answer
#             if selected_ans == actual_answer:
#                 total_marks = total_marks + questions[i].marks
#         student = models.Student.objects.get(user_id=request.user.id)
#         result = QMODEL.Result()
#         result.marks=total_marks
#         result.exam=course
#         result.student=student
#         result.save()

#         return HttpResponseRedirect('view-result')



# def calculate_marks_view(request):
#     #breakpoint()  # Debugging step

#     if not request.user.is_authenticated:
#         return HttpResponseRedirect('login')  # Ensure user is logged in

#     course_id = request.COOKIES.get('course_id')
#     if not course_id:
#         return HttpResponse("Course ID not found in cookies.")

#     try:
#         course = QMODEL.Course.objects.get(id=course_id)
#     except QMODEL.Course.DoesNotExist:
#         return HttpResponse("Invalid course ID.")

#     total_marks = 0
#     questions = QMODEL.Question.objects.filter(course=course)

#     for i in range(len(questions)):
#         selected_ans = request.COOKIES.get(str(i + 1))
#         if selected_ans and selected_ans == questions[i].answer:
#             total_marks += questions[i].marks

#     student = models.Student.objects.filter(user_id=request.user.id).first()
#     if not student:
#         return HttpResponse("You are not registered as a student.")

#     result = QMODEL.Result(marks=total_marks, exam=course, student=student)
#     result.save()

#     return HttpResponseRedirect('view-result')

def calculate_marks_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('login')

    course_id = request.COOKIES.get('course_id')
    if not course_id:
        return HttpResponse("Course ID not found in cookies.")

    try:
        course = QMODEL.Course.objects.get(id=course_id)
    except QMODEL.Course.DoesNotExist:
        return HttpResponse("Invalid course ID.")

    total_marks = 0
    questions = QMODEL.Question.objects.filter(course=course)

    for i, question in enumerate(questions, start=1):
        selected_ans = request.COOKIES.get(str(i))  # Get answer from cookies

        if not selected_ans:  # ✅ Check if empty or None
            print(f"Question {i} was not attempted.")  
            continue  # Skip to next question (counts as wrong)

        if selected_ans == question.answer:
            total_marks += question.marks  # ✅ Only count correct answers

    student = models.Student.objects.filter(user_id=request.user.id).first()
    if not student:
        return HttpResponse("You are not registered as a student.")

    result = QMODEL.Result(marks=total_marks, exam=course, student=student)
    result.save()

    return HttpResponseRedirect('view-result')





@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  
def exam_view(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    return render(request, 'exam/exam.html', {'exam': exam})