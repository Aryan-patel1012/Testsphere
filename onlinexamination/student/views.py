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
# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, localtime
from django.contrib import messages
import pytz
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User


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
# def start_exam_view(request,pk):
#     #breakpoint()
#     course=Course.objects.get(id=pk)
#     print("id",course.id)
#     questions=QMODEL.Question.objects.all().filter(course=course)
#     exam_timer=course.exam_timer
#     if request.method=='POST':
#         pass
#     response= render(request,'student/start_exam.html',{'course':course,'questions':questions ,'exam_timer': exam_timer})
#     response.set_cookie('course_id',course.id)
#     return response


# def start_exam_view(request, pk):
#     course = Course.objects.get(id=pk)
#     current_time = localtime(now())
 
#     # Ensure exam is only accessible at the scheduled time
#     if not (course.exam_date <= current_time <= course.exam_date + timedelta(minutes=course.exam_timer)):
#         messages.error(request, "The exam is not available at this time.")
#         return redirect('student-dashboard')  # Redirect to dashboard or another page
 
#     questions = QMODEL.Question.objects.filter(course=course)
#     exam_timer = course.exam_timer
#     response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions, 'exam_timer': exam_timer})
#     response.set_cookie('course_id', course.id)
#     return response


# def start_exam_view(request, pk):
#     # Retrieve the course object
#     course = Course.objects.get(id=pk)
#     ist = pytz.timezone('Asia/Kolkata')

#     # Assume exam_date is stored in IST, so we need to convert it to UTC
#     exam_date_ist = course.exam_date  # This is in IST

#     # Convert IST to UTC for internal processing
#     exam_date_utc = exam_date_ist.astimezone(pytz.utc)

#     # Convert UTC to IST for start time
#     exam_start_time = exam_date_utc.astimezone(ist)
#     exam_end_time = exam_start_time + timedelta(minutes=course.exam_timer)

#     # Get current time in IST
#     current_time = timezone.localtime(timezone.now()).astimezone(ist)

#     print("Raw Exam Date from DB (IST):", exam_date_ist)
#     print("Converted Exam Date to UTC:", exam_date_utc)
#     print("Corrected Exam Start Time (IST):", exam_start_time)
#     print("Exam End Time (IST):", exam_end_time)
#     print("Current Time (IST):", current_time)

#     # Check if the current time is within the exam start and end time
#     if exam_start_time <= current_time <= exam_end_time:
#         questions = QMODEL.Question.objects.filter(course=course)
#         response = render(request, 'student/start_exam.html', {
#             'course': course,
#             'questions': questions,
#             'exam_timer': course.exam_timer
#         })
#         response.set_cookie('course_id', course.id)
#         return response
#     else:
#         messages.error(request, "❌ Exam is not available now")
#         return redirect('student-dashboard')

def start_exam_view(request, pk):
    course = Course.objects.get(id=pk)
    ist = pytz.timezone('Asia/Kolkata')
 
    # Exam date is stored directly in IST
    exam_start_time = course.exam_date.replace(tzinfo=None)  # No conversion applied
    exam_end_time = (exam_start_time + timedelta(minutes=course.exam_timer)).replace(tzinfo=None)
 
    # Get current time without conversion
    current_time = timezone.now().astimezone(ist).replace(tzinfo=None)
 
    print("Raw Exam Date from DB (IST as stored):", course.exam_date)
    print("Exam Start Time (IST, directly from DB):", exam_start_time)
    print("Exam End Time (IST, directly from DB):", exam_end_time)
    print("Current Time (IST, as fetched):", current_time)
 
    # Check if exam is available
    if exam_start_time <= current_time <= exam_end_time:
        questions = QMODEL.Question.objects.filter(course=course)
        response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions, 'exam_timer': course.exam_timer})
        response.set_cookie('course_id', course.id)
        return response
    else:
        messages.error(request, "❌ Exam is not available now")
        return redirect('student-dashboard')
# @csrf_protect

@csrf_exempt
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
        selected_ans = request.COOKIES.get(str(i))
        if not selected_ans:
            continue
        if selected_ans == question.answer:
            total_marks += question.marks

    student = models.Student.objects.filter(user_id=request.user.id).first()
    if not student:
        return HttpResponse("You are not registered as a student.")

    result = QMODEL.Result(
        marks=total_marks,
        exam=course,
        student=student,
        date=timezone.now()
    )
    result.save()
    

    # ✅ Send result email
    user_email = student.email or request.user.email
    if user_email:
        send_mail(
            subject="Your TestSphere Exam Result",
            message=f"Hi {student.user.first_name},\n\nYou scored {total_marks} marks in the exam: {course.course_name}.\n\nGood luck!\nTestSphere Team",
            from_email='aryanpatel6966@gmail.com',  # use the email from settings.py
            recipient_list=[user_email],
            fail_silently=False
        )

    return HttpResponseRedirect('view-result')


# @csrf_exempt
# def calculate_marks_view(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect('login')
 
#     course_id = request.COOKIES.get('course_id')
#     if not course_id:
#         return HttpResponse("Course ID not found in cookies.")
 
#     try:
#         course = QMODEL.Course.objects.get(id=course_id)
#     except QMODEL.Course.DoesNotExist:
#         return HttpResponse("Invalid course ID.")
 
#     total_marks = 0
#     questions = QMODEL.Question.objects.filter(course=course)
 
#     for i, question in enumerate(questions, start=1):
#         selected_ans = request.COOKIES.get(str(i))  # Get answer from cookies
 
#         if not selected_ans:  # ✅ Check if empty or None
#             print(f"Question {i} was not attempted.")  
#             continue  # Skip to next question (counts as wrong)
 
#         if selected_ans == question.answer:
#             total_marks += question.marks  # ✅ Only count correct answers
 
#     student = models.Student.objects.filter(user_id=request.user.id).first()
#     if not student:
#         return HttpResponse("You are not registered as a student.")
 
#     result = QMODEL.Result(
#         marks=total_marks, 
#         exam=course, 
#         student=student,
#         date=timezone.now()  # ✅ Ensure date is set before saving
#     )
#     result.save()
 
#     return HttpResponseRedirect('view-result')




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