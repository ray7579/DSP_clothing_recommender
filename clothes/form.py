from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Admin, Comment
from django import forms
from django.db import transaction

class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_no = forms.IntegerField(required=True)
    dob = forms.DateField(required=True)

    class Meta(UserCreationForm.Meta):
        model=User

    @transaction.atomic
    def save(self):
        user  = super().save(commit=False)
        user.is_user = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')  
        user.save()
        customer = Customer.objects.create(user=user)
        customer.phone_no = self.cleaned_data.get('phone_no')
        customer.dob = self.cleaned_data.get('dob')
        customer.save()
        return customer

        
class AdminSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_no = forms.IntegerField(required=True)
    dob = forms.DateField(required=True)

    class Meta(UserCreationForm.Meta):
        model=User

    @transaction.atomic
    def save(self):
        user  = super().save(commit=False)
        user.is_user = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')  
        user.save()
        admin = Admin.objects.create(user=user)
        admin.phone_no = self.cleaned_data.get('phone_no')
        admin.dob = self.cleaned_data.get('dob')
        admin.save()
        return admin




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }