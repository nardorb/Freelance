from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, widgets

from models import *



TIME_FORMAT = '%d.%b.%Y'

class BargainingUnitForm(ModelForm):
  officer = forms.ModelChoiceField(queryset=User.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))
  organization = forms.ModelChoiceField(queryset=Organization.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))

  class Meta:
    model = BargainingUnit
    fields = ['name', 'agreementStart', 'agreementEnd', 'claimTime',
              'dues_percent', 'dues_min', 'organization', 'officer', 'last_reset']
    widgets = {
      'name': widgets.TextInput(attrs={'class': 'form-control'}),
      'agreementStart': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'agreementEnd': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'claimTime': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'dues_percent': widgets.NumberInput(attrs={'class': 'form-control'}),
      'dues_min': widgets.NumberInput(attrs={'class': 'form-control'}),
      'last_reset': widgets.DateInput(attrs={'readonly': 'True', 'class': 'form-control'})
    }


class BeneficiaryForm(ModelForm):
  member = forms.ModelChoiceField(queryset=Member.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))

  class Meta:
    model = Beneficiary
    fields = ['fname', 'mname', 'lname', 'dob', 'sex', 'city', 'parish',
              'email', 'telephone', 'member']
    widgets = {
    'fname': widgets.TextInput(attrs={'class': 'form-control'}),
    'mname': widgets.TextInput(attrs={'class': 'form-control'}),
    'lname': widgets.TextInput(attrs={'class': 'form-control'}),
    'dob': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    'sex': widgets.Select(attrs={'class': 'form-control'}),
    'city': widgets.TextInput(attrs={'class': 'form-control'}),
    'parish': widgets.Select(attrs={'class': 'form-control'}),
    'email': widgets.EmailInput(attrs={'class': 'form-control', 'type': 'email'}),
    'telephone': widgets.TextInput(attrs={'class': 'form-control form_telephone', 'max': '12', 'placeholder': '876-xxx-xxxx', 'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'})
    }


class BranchForm(ModelForm):
  organization = forms.ModelChoiceField(queryset=Organization.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))

  class Meta:
    model = Branch
    fields = ['location', 'organization']
    widgets = {
          'location': widgets.TextInput(attrs={'class': 'form-control'})
        }


class CategoryForm(ModelForm):
  bargainingUnit = forms.ModelChoiceField(queryset=BargainingUnit.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control org_dependent'}))
  organization = forms.ModelChoiceField(queryset=Organization.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))

  class Meta:
    model = Category
    fields = ['name', 'rateOfIncrease', 'lastIncrease', 'nextIncrease',
              'increasePeriod', 'currentPeriod', 'increaseHistory',
              'bargainingUnit', 'organization']
    widgets = {
          'name': widgets.TextInput(attrs={'class': 'form-control'}),
          'rateOfIncrease': widgets.NumberInput(attrs={'class': 'form-control', 'style': 'width:80%;'}),
          'lastIncrease': widgets.DateInput(attrs={'readonly': 'True', 'class': 'form-control', 'type': 'date'}),
          # 'nextIncrease': widgets.DateInput(attrs={'readonly': 'True', 'class': 'form-control', 'type': 'date'}),        'nextIncrease': widgets.DateInput(attrs={'readonly': 'True', 'class': 'form-control', 'type': 'date'}),
          'nextIncrease': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
          'increasePeriod': widgets.NumberInput(attrs={'class': 'form-control', 'style': 'width:60%;'}),
          'currentPeriod': widgets.NumberInput(attrs={'readonly': 'True', 'class': 'form-control', 'style': 'width:80%;'}),
          'increaseHistory': widgets.TextInput(attrs={'readonly': 'True', 'class': 'form-control'})
        }


class MemberForm(ModelForm):
  bargainingUnit = forms.ModelChoiceField(queryset=BargainingUnit.objects.all(), required=False,
                                widget=widgets.Select(attrs={'class': 'form-control org_dependent'}))
  branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False,
                                widget=widgets.Select(attrs={'class': 'form-control org_dependent'}))
  category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False,
                                widget=widgets.Select(attrs={'class': 'form-control org_dependent'}))
  organization = forms.ModelChoiceField(queryset=Organization.objects.all(),
                                widget=widgets.Select(attrs={'class': 'form-control'}))

  class Meta:
    model = Member
    fields = ['nwuid', 'fname', 'mname', 'lname', 'dob', 'sex', 'city',
              'parish', 'position', 'telephone', 'email', 'salary',
              'salary_type', 'dues', 'employmentStart', 'employmentEnd',
              'unionStart', 'unionEnd', 'status', 'membership', 'bargainingStatus',
              'category', 'organization', 'branch', 'bargainingUnit', 'notes']
    widgets = {
      'nwuid': widgets.TextInput(attrs={'readonly': 'True', 'class': 'form-control', 'placeholder': 'Generated after creation'}),
      'fname': widgets.TextInput(attrs={'class': 'form-control'}),
      'mname': widgets.TextInput(attrs={'class': 'form-control'}),
      'lname': widgets.TextInput(attrs={'class': 'form-control'}),
      'dob': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'sex': widgets.Select(attrs={'class': 'form-control'}),
      'city': widgets.TextInput(attrs={'class': 'form-control'}),
      'parish': widgets.Select(attrs={'class': 'form-control'}),
      'position': widgets.TextInput(attrs={'class': 'form-control'}),
      'telephone': widgets.TextInput(attrs={'class': 'form-control form_telephone', 'max': '12', 'placeholder': '876-xxx-xxxx', 'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}),
      'email': widgets.EmailInput(attrs={'class': 'form-control', 'type': 'email'}),
      'salary': widgets.NumberInput(attrs={'class': 'form-control', 'style': 'width:80%;'}),
      'salary_type': widgets.Select(attrs={'class': 'form-control'}),
      'dues': widgets.NumberInput(attrs={'readonly': 'True', 'class': 'form-control', 'style': 'width:80%;'}),
      'employmentStart': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'employmentEnd': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'unionStart': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'unionEnd': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'status': widgets.Select(attrs={'class': 'form-control'}),
      'membership': widgets.Select(attrs={'class': 'form-control'}),
      'bargainingStatus': widgets.Select(attrs={'class': 'form-control'}),
      'notes': widgets.Textarea(attrs={'class': 'form-control'})
    }

class OrganizationForm(ModelForm):
  class Meta:
    model = Organization
    fields = ['name', 'address', 'telephone', 'contact_name', 'contact_tel',
              'budgetStart', 'budgetEnd']
    widgets = {
      'name': widgets.TextInput(attrs={'class': 'form-control'}),
      'address': widgets.TextInput(attrs={'class': 'form-control'}),
      'telephone': widgets.TextInput(attrs={'class': 'form-control form_telephone', 'max': '12', 'placeholder': '876-xxx-xxxx', 'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}),
      'contact_name': widgets.TextInput(attrs={'class': 'form-control'}),
      'contact_tel': widgets.TextInput(attrs={'class': 'form-control form_telephone', 'max': '12', 'placeholder': '876-xxx-xxxx', 'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}),
      'budgetStart': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
      'budgetEnd': widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    }