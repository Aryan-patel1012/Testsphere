from django.db import models
import pytz
from student.models import Student  
from django.utils.timezone import now
from django.utils import timezone

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=50)
    question_number = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    exam_timer = models.IntegerField(help_text="Duration of the exam in minutes")
    exam_date = models.DateTimeField(default=timezone.now, help_text="Scheduled exam date and time")   
    def __str__(self):
        return self.course_name
   
   

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)  # Stored in UTC
    ist_date = models.DateTimeField(blank=True, null=True)
 
    def save(self, *args, **kwargs):
        if self.date is None:  # Ensure date is set
            self.date = timezone.now()  # Assign current UTC time
 
        ist = pytz.timezone('Asia/Kolkata')
        self.ist_date = self.date.astimezone(ist)  # Convert UTC to IST before saving
        super().save(*args, **kwargs)  # Save object



