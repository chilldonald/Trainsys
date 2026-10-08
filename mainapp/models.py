from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):   
    MMR = models.FloatField(default=0)
    def __str__(self):
        return self.username

class Exercise(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%Y-%m-%d')}"   

class WorkoutEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.FloatField()
    reps = models.IntegerField()
    sets = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.weight}kg x {self.reps} reps x {self.sets} sets"
    
