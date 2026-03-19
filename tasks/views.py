from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from datetime import date


@login_required
def task_list(request):
    """
    Display all tasks ordered by due date.
    Overdue tasks are marked via 'is_overdue' attribute.
    """
    tasks = Task.objects.all().order_by('due_date')
    today = date.today()
    for task in tasks:
        task.is_overdue = task.due_date and task.due_date < today and task.status != "done"
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def dashboard(request):
    """
    Display logged-in user's tasks ordered by due date.
    Overdue tasks are highlighted.
    """
    tasks = Task.objects.filter(owner=request.user).order_by('due_date')
    today = date.today()
    for task in tasks:
        task.is_overdue = task.due_date and task.due_date < today and task.status != "done"
    return render(request, 'tasks/dashboard.html', {'tasks': tasks})


@login_required
def create_task(request):
    """
    Create a new task.
    The owner is selected from a dropdown in the form.
    """
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # owner comes from the form
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "tasks/task_form.html", {"form": form})


@login_required
def edit_task(request, task_id):
    """
    Edit an existing task.
    Owner can be changed via the form.
    """
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()  # saves changes including owner
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/edit_task.html", {"form": form})


@login_required
def delete_task(request, task_id):
    """
    Delete a task after confirmation.
    """
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")

    return render(request, "tasks/delete_task.html", {"task": task})