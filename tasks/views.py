from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Task
from .forms import TaskForm
from datetime import date



@login_required
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "tasks/task_form.html", {"form": form})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save(commit=False)
            # updated_task.owner = request.user
            updated_task.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/edit_task.html", {"form": form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")

    return render(request, "tasks/delete_task.html", {"task": task})

@login_required
def dashboard(request):
    tasks = Task.objects.filter(owner=request.user).order_by('due_date')
    today = date.today()
    for task in tasks:
        # Add a flag dynamically
        task.is_overdue = task.due_date and task.due_date < today and task.status != "Completed"
    return render(request, "tasks/dashboard.html", {"tasks": tasks})