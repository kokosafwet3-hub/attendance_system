from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'student_id']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'أدخل اسم الطالب',
                'class': 'input-field'
            }),
            'student_id': forms.TextInput(attrs={
                'placeholder': 'أدخل كود الطالب',
                'class': 'input-field'
            }),
        }