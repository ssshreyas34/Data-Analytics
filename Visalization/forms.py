from django import forms
# from .models import Registration,Hash_key
from  django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class Registration_form(UserCreationForm):
    username=forms.EmailField(required=True,widget= forms.EmailInput(attrs={'placeholder':'Ex. youremail@gmail.com/user@123'}))
    password1= forms.CharField(max_length=20,required=True,widget=forms.PasswordInput(attrs={"placeholder":"Enter password"}))
    password2 = forms.CharField(max_length=20,required=True,widget=forms.PasswordInput(attrs={"placeholder":"Re-enter password"}))
    class Meta:
        model=User
        fields = ["username","password1","password2"]


class log_form(forms.Form):
    log_username = forms.EmailField(required=True,
                                widget=forms.EmailInput(attrs={'placeholder': 'Ex. youremail@gmail.com'}))
    log_password = forms.CharField(max_length=20, required=True,
                               widget=forms.PasswordInput(attrs={"placeholder": "Enter Password"}))


class load_form(forms.Form):
    file_name=forms.CharField(label="filename",widget=forms.TextInput(attrs={"placeholder":"Enter name for to save dataset"}))
    file_upload=forms.FileField()