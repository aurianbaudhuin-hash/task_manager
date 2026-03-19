from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task
from datetime import date, timedelta


class TaskManagerTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        # Create tasks with specific owners
        self.task1 = Task.objects.create(
            title="Task 1",
            description="First task",
            due_date=date.today() + timedelta(days=1),
            status="not_started",
            owner=self.user1,
        )

        self.task2 = Task.objects.create(
            title="Task 2",
            description="Second task",
            due_date=date.today() - timedelta(days=1),  # overdue
            status="not_started",
            owner=self.user2,
        )

    def test_task_list_page(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
        # Check overdue highlighting
        self.assertContains(response, "bg-danger-subtle")  # bootstrap class for overdue

    def test_dashboard_shows_only_user_tasks(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")  # task2 belongs to user2

    def test_task_creation(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.post(
            reverse("create_task"),
            {
                "title": "New Task",
                "description": "A new test task",
                "due_date": date.today(),
                "status": "not_started",
                "owner": self.user2.id,  # assign to user2
                "comment": "Test comment",
            },
            follow=True,
        )
        self.assertEqual(Task.objects.filter(title="New Task").count(), 1)
        task = Task.objects.get(title="New Task")
        self.assertEqual(task.owner, self.user2)

    def test_task_edit(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.post(
            reverse("edit_task", args=[self.task1.id]),
            {
                "title": "Updated Task 1",
                "description": self.task1.description,
                "due_date": self.task1.due_date,
                "status": self.task1.status,
                "owner": self.user2.id,  # change owner
                "comment": self.task1.comment,
            },
            follow=True,
        )
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task 1")
        self.assertEqual(self.task1.owner, self.user2)

    def test_edit_other_users_task(self):
        self.client.login(username="user1", password="pass1")
        # Edit task2 which belongs to user2
        response = self.client.post(
            reverse("edit_task", args=[self.task2.id]),
            {
                "title": "Edited by user1",
                "description": self.task2.description,
                "due_date": self.task2.due_date,
                "status": self.task2.status,
                "owner": self.user2.id,
                "comment": self.task2.comment,
            },
            follow=True,
        )
        self.task2.refresh_from_db()
        self.assertEqual(self.task2.title, "Edited by user1")
        self.assertEqual(self.task2.owner, self.user2)

    def test_delete_task(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.post(reverse("delete_task", args=[self.task1.id]), follow=True)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_form_validation(self):
        self.client.login(username="user1", password="pass1")
        # Missing title
        response = self.client.post(
            reverse("create_task"),
            {
                "title": "",  # empty
                "description": "No title",
                "due_date": date.today(),
                "status": "not_started",
                "owner": self.user1.id,
                "comment": "",
            },
        )
        self.assertContains(response, "This field is required.")

    def test_overdue_task_highlight(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("task_list"))
        # The overdue task should appear with the correct class
        self.assertContains(response, "bg-danger-subtle")  # matches dashboard and task_list HTML