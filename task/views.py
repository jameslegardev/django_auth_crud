from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'html/index.html')

def signup(request):

    if (request.method) == 'GET':
        print('enviando formulario')
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'html/signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        return render(request, 'html/signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

    return render(request, 'html/signup.html', {
        'form': UserCreationForm
    })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):

    if request.method == 'GET':
        return render(request, 'html/login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'html/login.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect',
            })
        else:
            login(request, user)
            return redirect('tasks')


@login_required
def task(request):

    # Control de arreglos por librerias de python "filter, all, etc. explorar mas"
    task = Task.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'html/task.html', {
        'list': task,
    })

@login_required
def task_all(request):

    # Control de arreglos por librerias de python "filter, all, etc. explorar mas"
    task = Task.objects.filter(user=request.user).order_by('-date_completed')
    return render(request, 'html/task.html', {
        'list': task,
    })

@login_required
def create_task(request):

    if request.method == "GET":

        return render(request, 'html/create_task.html', {
            'form': TaskForm
        })

    else:
        try:
            form = TaskForm(request.POST)
            # Guardará los datos del formulario
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            print(new_task)
            return redirect('tasks')

        except ValueError:
            return render(request, 'html/create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid data',
            })

@login_required
def task_detail(request, tasker_id: int):

    if request.method == 'GET':

        tasker = get_object_or_404(Task, pk=tasker_id, user = request.user)
        form = TaskForm(instance=tasker)
        return render(request, 'html/task_detail.html',
                    {
                        'tasker': tasker,
                        'form': form,
                    })
    else:
        try:
            tasker = get_object_or_404(Task, pk=tasker_id, user = request.user)
            form = TaskForm(request.POST, instance=tasker)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'html/task_detail.html',
                    {
                        'tasker': tasker,
                        'form': form,
                        'error': "Error updating task"
                    })

@login_required        
def task_complete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')

@login_required    
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

