from django.shortcuts import render,redirect
import pytz
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM
from django.urls import reverse
from django.utils.timezone import make_aware , is_naive
from .forms import ExamScheduleForm



def schedule_exam(request):
    if request.method == "POST":
        form = ExamScheduleForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.teacher = request.user  # Assign logged-in teacher
            exam.save()
            return redirect('exam_list')  # Redirect to a page listing scheduled exams
    else:
        form = ExamScheduleForm()
    return render(request, 'schedule_exam.html', {'form': form})
#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
# def teacher_add_exam_view(request):
#     courseForm=ExamScheduleForm()
#     if request.method=='POST':
#         courseForm=ExamScheduleForm(request.POST)
#         if courseForm.is_valid():        
#             courseForm.save()
#         else:
#             print(courseForm.errors)
#         return HttpResponseRedirect('/teacher/teacher-view-exam')
#     return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})


# def teacher_add_exam_view(request):
#     courseForm = ExamScheduleForm()
#     if request.method == 'POST':
#         courseForm = ExamScheduleForm(request.POST)
#         if courseForm.is_valid():
#             # Extract the exam date from the form
#             exam_date = courseForm.cleaned_data['exam_date']
            
#             # Check if the datetime is naive or aware
#             if exam_date.tzinfo is None:
#                 # If naive, localize to IST
#                 ist = pytz.timezone('Asia/Kolkata')
#                 exam_date_ist = ist.localize(exam_date)
#             else:
#                 # If aware, just use it as is
#                 exam_date_ist = exam_date
            
#             # Convert IST to UTC
#             exam_date_utc = exam_date_ist.astimezone(pytz.utc)
            
#             # Save the course with the corrected UTC datetime
#             course = courseForm.save(commit=False)
#             course.exam_date = exam_date_utc
#             course.save()
            
#             return HttpResponseRedirect('/teacher/teacher-view-exam')
#         else:
#             print(courseForm.errors)
#     return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})

# def teacher_add_exam_view(request):
#     courseForm = ExamScheduleForm()
#     if request.method == 'POST':
#         courseForm = ExamScheduleForm(request.POST)
#         if courseForm.is_valid():
#             # Extract the exam date from the form
#             exam_date = courseForm.cleaned_data['exam_date']
            
#             # Localize to IST if the datetime is naive
#             ist = pytz.timezone('Asia/Kolkata')
#             if exam_date.tzinfo is None:
#                 # If naive, localize to IST
#                 exam_date_ist = ist.localize(exam_date)
#             else:
#                 # If aware, just use it as is
#                 exam_date_ist = exam_date
            
#             # Save the course with the IST datetime
#             course = courseForm.save(commit=False)
#             print(exam_date_ist)
#             course.exam_date = exam_date_ist  # Store as IST
#             course.save()
            
#             return HttpResponseRedirect('/teacher/teacher-view-exam')
#         else:
#             print(courseForm.errors)
#     return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})

def teacher_add_exam_view(request):
    if request.method == 'POST':
        courseForm = ExamScheduleForm(request.POST)
        if courseForm.is_valid():
            exam_instance = courseForm.save(commit=False)
 
            # Define IST timezone
            ist = pytz.timezone('Asia/Kolkata')
 
            # Ensure datetime is in IST
            if is_naive(exam_instance.exam_date):
                exam_instance.exam_date = make_aware(exam_instance.exam_date, timezone=ist)
 
            exam_instance.save()
            return HttpResponseRedirect('/teacher/teacher-view-exam')
 
    else:
        courseForm = ExamScheduleForm()
 
    return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')
