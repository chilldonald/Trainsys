from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import User, Exercise, Workout, WorkoutEntry
from django.utils import timezone
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required  
from django.db.models import F, Sum, FloatField

def homepage(request):
    if not request.user.is_authenticated:
        return redirect('login')

    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    context = {'workouts': workouts}
    return render(request, 'home.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
        
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'GET':
        return render(request, 'register.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password_confirm')

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return redirect('home')

@login_required
def analytics(request):
    entries = WorkoutEntry.objects.filter(workout__user=request.user)\
                                  .select_related('exercise', 'workout')\
                                  .order_by('workout__date')

    analytics_data = {}

    for entry in entries:
        ex_name = entry.exercise.name
        date_str = entry.workout.date.strftime('%d.%m') 
        if entry.reps == 1:
            estimated_1rm = entry.weight
        else:
            estimated_1rm = entry.weight * (1 + entry.reps / 30)

        estimated_1rm = round(estimated_1rm, 1)
        volume = entry.weight * entry.reps * entry.sets

        if ex_name not in analytics_data:
            analytics_data[ex_name] = {}

        if date_str not in analytics_data[ex_name]:
            analytics_data[ex_name][date_str] = {
                'max_1rm': estimated_1rm,
                'volume': volume
            }
        else:
            analytics_data[ex_name][date_str]['max_1rm'] = max(
                analytics_data[ex_name][date_str]['max_1rm'], 
                estimated_1rm
            )
            analytics_data[ex_name][date_str]['volume'] += volume

    final_data = {}
    for ex_name, dates_dict in analytics_data.items():
        final_data[ex_name] = {
            'labels': list(dates_dict.keys()),
            'max_1rms': [d['max_1rm'] for d in dates_dict.values()],
            'volumes': [d['volume'] for d in dates_dict.values()]
        }

    context = {
        'chart_data_json': json.dumps(final_data, ensure_ascii=False)
    }

    return render(request, 'analytics.html', context)

@login_required
def scoreboard(request):
    if request.method == 'GET':
        return render(request, 'scoreboard.html')

@login_required
def profile(request):
    if request.method == 'GET':
        workout = Workout.objects.filter(user=request.user)
        total_workouts = workout.count()
        total_volume = WorkoutEntry.objects.filter(workout__user=request.user).aggregate(
        total=Sum(F('weight') * F('reps') * F('sets'), output_field=FloatField()))['total'] or 0 
        total_volume = round(total_volume / 1000, 2)
        return render(request, 'profile.html', {"total_workouts": total_workouts, "MMR": request.user.MMR, "total_volume": total_volume})


def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def new_workout(request):
    if request.method == 'GET':
        exercises = Exercise.objects.all()

        context = {
            'exercises': exercises,
            'today': datetime.date(datetime.now())
        }
        return render(request, 'new_workout.html', context)
    
    elif request.method == 'POST' and request.content_type == 'application/json':
        data = json.loads(request.body)
        entires = data.get('entries', [])
        if entires:
            workout = Workout.objects.create(user=request.user, date=timezone.now())

            obj = [
                WorkoutEntry(
                    user=request.user,
                    workout=workout,
                    exercise=Exercise.objects.get(id=entry['exercise_id']),
                    weight=entry['weight'],
                    reps=entry['reps'],
                    sets=entry['sets']
                ) for entry in entires
            ]
            WorkoutEntry.objects.bulk_create(obj)
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'error': 'No entries provided'}, status=400)

@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    entries = WorkoutEntry.objects.filter(workout=workout)

    context = {
        'workout': workout,
        'entries': entries
    }

    return render(request, 'workout_detail.html', context)

@login_required
@require_POST
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout.delete()
    return redirect('home')