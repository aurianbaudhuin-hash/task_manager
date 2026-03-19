from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "status", "comment", "owner"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": " "}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": " ",
                    "style": "height: 100px",
                }
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": " ",
                    "style": "height: 100px",
                }
            ),
        }
