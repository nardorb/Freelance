# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods

import forms
import models



now = date.today()

def loginView(request):
    return render(request, 'login.html')


def user_login(request):
  username = request.POST['username']
  password = request.POST['password']
  user = authenticate(request, username=username, password=password)
  if user:
    login(request, user)
    return redirect('dashboard')
  else:
    errors = True
    return render(request, 'login.html', {'errors': errors})


def user_logout(request):
  logout(request)
  return redirect('login')


@login_required()
def homeView(request):
    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET"])
def access_denied(request):
  return render(request, 'access_denied.html')


@login_required
@require_http_methods(["GET"])
def pagenotfound(request):
  return render(request, '404.html')

def thankyou(request):
    return render(request, 'thankyoupageOrg')


@login_required
@require_http_methods(['GET'])
def dump_db(request):
  from django.core.management import call_command

  file = open("mms_dump-{0}.json".format(now),'w')

  call_command('dumpdata','mms',format='json',indent=2,stdout=file)
  file.close()

  return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


# ======================== Assistant Views =======================

@login_required
@require_http_methods(["GET"])
def contracts(request):
  bargainingUnits = models.BargainingUnit.objects.filter(agreementEnd__range=(now,
                      (now + timedelta(4*365.25/12)))).select_related(
                        'organization'
                      ).values('id', 'name',
                      'agreementStart', 'agreementEnd', 'claimTime',
                      'organization__name', 'officer').order_by('-agreementEnd')
  return JsonResponse(list(bargainingUnits), safe=False)


@login_required
@require_http_methods(["GET"])
def birthdays(request):
  members = models.Member.objects.filter(dob__month=now.month).select_related(
                      'organization'
                      ).values('id',
                      'nwuid', 'fname', 'mname', 'lname', 'dob', 'telephone',
                      'email', 'organization__name').order_by('-dob')
  return JsonResponse(list(members), safe=False)


@login_required
@require_http_methods(["GET"])
def birthdays_today(request):
  members = models.Member.objects.filter(dob__month=now.month,
                      dob__day=now.day).select_related('organization'
                      ).values('id', 'nwuid', 'fname', 'mname', 'lname', 'dob',
                      'telephone', 'email', 'organization__name').order_by('-dob')
  return JsonResponse(list(members), safe=False)


@login_required
@require_http_methods(["GET"])
def budgets_start(request):
  organizations = models.Organization.objects.filter(budgetStart__range=(now,
                (now + timedelta(4*365.25/12)))).values('id', 'name', 'address',
                      'telephone', 'contact_name', 'contact_tel', 'budgetStart',
                      'budgetEnd').order_by('-budgetStart')
  return JsonResponse(list(organizations), safe=False)

@login_required
@require_http_methods(["GET"])
def budgets_end(request):
  organizations = models.Organization.objects.filter(budgetEnd__range=(now,
                (now + timedelta(4*365.25/12)))).values('id', 'name', 'address',
                      'telephone', 'contact_name', 'contact_tel', 'budgetStart',
                      'budgetEnd').order_by('-budgetEnd')
  return JsonResponse(list(organizations), safe=False)


@login_required
@permission_required('mms.can_apply_roi', raise_exception=True)
@require_http_methods(["GET"])
def rateofincrease(request):
  organizations = models.Organization.objects.all()
  bargaining_units = models.BargainingUnit.objects.all()
  return render(request, 'roi.html', {'bargaining_units': bargaining_units, 'organizations': organizations, 'name': request.user.get_full_name()})


@login_required
@permission_required('mms.can_apply_roi', raise_exception=True)
@require_http_methods(["POST"])
def apply_ROI(request, pk=None):
  bargainingUnit = get_object_or_404(models.BargainingUnit, pk=pk)
  categoryList = []
  members = models.Member.objects.filter(bargainingUnit=bargainingUnit,status='active')
  categories = models.Category.objects.filter(Q(nextIncrease__lte=now) | Q(nextIncrease__isnull=True), bargainingUnit=pk)
  if not categories:
    return JsonResponse({'status': 'failed', 'message': 'ROI could not be applied! No valid category found.'}, safe=False)
  for member in members:
    category = member.category
    if (category.currentPeriod <= category.increasePeriod):
      member.salary += (member.salary*category.rateOfIncrease)/100
      member.save()

  for category in categories:
    year = str(now.year)
    category.lastIncrease = now
    category.nextIncrease = now + relativedelta(years=1)
    category.currentPeriod += 1
    if not category.increaseHistory:
      category.increaseHistory = "{0}: {1}%".format(year, category.rateOfIncrease)
    else:
      category.increaseHistory = str(category.increaseHistory) + ", " + year + ": " + str(category.rateOfIncrease)
    category.save()
    categoryList.append({'id': category.id, 'name': category.name})
  return JsonResponse({'status': 'done', 'bargainingUnit':bargainingUnit.name,
                       'message': 'ROI successfully applied to ' +  bargainingUnit.name
                      }, safe=False)


@login_required
@permission_required('mms.can_reset', raise_exception=True)
@require_http_methods(["GET"])
def reset_agreement(request):
  bargaining_units = models.BargainingUnit.objects.all()
  return render(request, 'resetAgreement.html', {'bargaining_units': bargaining_units, 'name': request.user.get_full_name()})


@login_required
@permission_required('mms.can_reset', raise_exception=True)
@require_http_methods(["GET"])
def reset_agreement_bu(request, pk=None):
  bargainingUnit = get_object_or_404(models.BargainingUnit, pk=pk)
  categories = models.Category.objects.filter(bargainingUnit=bargainingUnit)
  bargainingUnit.last_reset = now
  bargainingUnit.save()
  if categories:
    categories.update(lastIncrease=None, nextIncrease=None, currentPeriod=0, increaseHistory=None)
    return JsonResponse({'status': 'done', 'message': 'Agreement has be reset for all Categories in ' + bargainingUnit.name}, safe=False)
  else:
    return JsonResponse({'status': 'failed', 'message': 'Agreement could not be reset! No valid category found for ' + bargainingUnit.name}, safe=False)


@login_required
@require_http_methods(["POST"])
def update_ROI(request, pk=None):
  category = get_object_or_404(models.Category, pk=pk)
  category.rateOfIncrease = request.POST['roi']
  category.save()
  return JsonResponse({'status': 'done', 'category': category.name + " --> " + category.rateOfIncrease }, safe=False)


@login_required
@require_http_methods(["GET"])
def roi_due(request):
  categories = models.Category.objects.filter(nextIncrease__lte=now).select_related(
                            'organization'
                            ).values('id', 'name', 'rateOfIncrease',
                            'lastIncrease', 'nextIncrease', 'increasePeriod',
                            'currentPeriod', 'increaseHistory',
                            'bargainingUnit__name', 'organization__name').order_by('-nextIncrease')
  return JsonResponse(list(categories), safe=False)


@login_required
@require_http_methods(["GET"])
def ratio(request):
  organizations = models.Organization.objects.all()
  return render(request, 'ratio.html', {'organizations': organizations, 'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET"])
def delegate_ratio(request, pk=None):
  bargainingUnit = get_object_or_404(models.BargainingUnit, pk=pk)
  members = models.Member.objects.filter(bargainingUnit=bargainingUnit, membership="M").count()
  delegates = models.Member.objects.filter(Q(membership="D") | Q(membership="CD"), bargainingUnit=bargainingUnit).count()
  ratio = "{0}:1".format(int(members + delegates)/int(delegates))
  return JsonResponse({'members': members, 'delegates': delegates, 'ratio': ratio}, safe=False)


@login_required
@require_http_methods(["GET"])
def delegate_ratio_list(request, pk=None):
  bargaining_units = models.BargainingUnit.objects.filter(organization=pk)
  bu_list = []

  for bargaining_unit in bargaining_units:
    members = models.Member.objects.filter(bargainingUnit=bargaining_unit, membership="M").count()
    delegates = models.Member.objects.filter(Q(membership="D") | Q(membership="CD"), bargainingUnit=bargaining_unit).count()
    split = int(members + delegates)/int(delegates)

    if split < 25:
      status = -1
    elif split >= 30:
      status = 1
    else:
      status = 0

    ratio = "{0}:1".format(split)
    bu_list.append({'id': bargaining_unit.id, 'name': bargaining_unit.name, 'members': members, 'delegates': delegates, 'ratio': ratio, 'status': status})

  return JsonResponse(bu_list, safe=False)


@login_required
@require_http_methods(["GET"])
def warnings(request):
  bargainingUnits = models.BargainingUnit.objects.all()

  return render(request, 'warnings.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET"])
def officers(request):
  from django.core import serializers

  officers = User.objects.all().values('pk', 'username', 'first_name', 'last_name', 'email')
  print(officers)
  return render(request, 'officers.html', {'officers': officers, 'name': request.user.get_full_name()})


# ================== CREATE/DETAILS/UPDATE Views =====================

@login_required
@require_http_methods(["GET", "POST"])
def bargainingUnitView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.BargainingUnit.objects.get(name=request.POST.get('name'))
      form = forms.BargainingUnitForm(request.POST, instance=instance)
    except models.BargainingUnit.DoesNotExist:
      form = forms.BargainingUnitForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageCat.html', {'name': request.user.get_full_name()})
    else:
      return render(request, 'bargaining_unit.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.BargainingUnit, pk=pk)
      try:
        officer = User.objects.get(username=instance.officer)
      except User.DoesNotExist:
        officer = None

      form = forms.BargainingUnitForm(instance=instance, initial = {'officer': officer })
    else:
      form = forms.BargainingUnitForm()
    return render(request, 'bargaining_unit.html', {'form': form, 'name': request.user.get_full_name()})

  # elif request.method == 'DELETE':
  #   instance = get_object_or_404(models.BargainingUnit, pk=pk)
  #   instance.delete()

    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET", "POST"])
def beneficiaryView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.Beneficiary.objects.get(email=request.POST.get('email'))
      form = forms.BeneficiaryForm(request.POST, instance=instance)
    except models.Beneficiary.DoesNotExist:
      form = forms.BeneficiaryForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageBeneficiaries.html', {'name': request.user.get_full_name()})
    else:
      return render(request, 'beneficiary.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.Beneficiary, pk=pk)
      form = forms.BeneficiaryForm(instance=instance)
    else:
      form = forms.BeneficiaryForm()
    return render(request, 'beneficiary.html', {'form': form, 'name': request.user.get_full_name()})

  # elif request.method == 'DELETE':
  #   instance = get_object_or_404(models.Beneficiary, pk=pk)
  #   instance.delete()

    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET", "POST"])
def branchView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.Branch.objects.get(location=request.POST.get('location'),
                                  organization=request.POST.get('organization'))
      form = forms.BranchForm(request.POST, instance=instance)
    except models.Branch.DoesNotExist:
      form = forms.BranchForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageBranch.html', {'name': request.user.get_full_name()})
    else:
        return render(request, 'branch.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.Branch, pk=pk)
      form = forms.BranchForm(instance=instance)
    else:
      form = forms.BranchForm()
    return render(request, 'branch.html', {'form': form, 'name': request.user.get_full_name()})

  # elif request.method == 'DELETE':
  #   instance = get_object_or_404(models.Branch, pk=pk)
  #   instance.delete()

    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET", "POST"])
def categoryView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.Category.objects.get(name=request.POST.get('name'))
      form = forms.CategoryForm(request.POST, instance=instance)
    except models.Category.DoesNotExist:
      form = forms.CategoryForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageCat.html', {'name': request.user.get_full_name()})
    else:
        return render(request, 'category.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.Category, pk=pk)
      form = forms.CategoryForm(instance=instance)
    else:
      form = forms.CategoryForm()
    return render(request, 'category.html', {'form': form, 'name': request.user.get_full_name()})

  # elif request.method == 'DELETE':
  #   instance = get_object_or_404(models.Category, pk=pk)
  #   instance.delete()

    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


@login_required
@require_http_methods(["GET", "POST"])
def memberView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.Member.objects.get(nwuid=request.POST.get('nwuid'))
      form = forms.MemberForm(request.POST, instance=instance)
    except models.Member.DoesNotExist:
      form = forms.MemberForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageMembers.html', {'name': request.user.get_full_name()})
    else:
      return render(request, 'member.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.Member, pk=pk)
      form = forms.MemberForm(instance=instance)
    else:
      form = forms.MemberForm()
    return render(request, 'member.html', {'form': form, 'name': request.user.get_full_name()})

  # elif request.method == 'DELETE':
  #   instance = get_object_or_404(models.Member, pk=pk)
  #   instance.delete()

    return render(request, 'thankyoupageMembers.html')


@login_required
@require_http_methods(["GET", "POST"])
def organizationView(request, pk=None):
  if request.method == 'POST':
    try:
      instance = models.Organization.objects.get(name=request.POST.get('name'))
      form = forms.OrganizationForm(request.POST, instance=instance)
    except models.Organization.DoesNotExist:
      form = forms.OrganizationForm(request.POST)

    if form.is_valid():
      form.save()
      return render(request, 'thankyoupageOrg.html', {'name': request.user.get_full_name()})
    else:
      return render(request, 'organization.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'GET':
    if pk:
      instance = get_object_or_404(models.Organization, pk=pk)
      form = forms.OrganizationForm(instance=instance)
    else:
      form = forms.OrganizationForm()
    return render(request, 'organization.html', {'form': form, 'name': request.user.get_full_name()})

  elif request.method == 'DELETE':
    instance = get_object_or_404(models.Organization, pk=pk)
    instance.delete()

    return render(request, 'dashboard.html', {'name': request.user.get_full_name()})


# ================== LIST Template Views =====================

@login_required
@require_http_methods(["GET"])
def bargainingUnitListView(request):
  return render(request, 'bargaining_unit_list.html', {'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def buDelegatesListView(request):
  bargaining_units = models.BargainingUnit.objects.all()
  return render(request, 'delegates_list.html', {'bargaining_units':bargaining_units, 'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def beneficiaryListView(request):
  return render(request, 'beneficiary_list.html', {'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def branchListView(request):
  organizations = models.Organization.objects.all()
  return render(request, 'branch_list.html', {'organizations': organizations, 'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def categoryListView(request):
  organizations = models.Organization.objects.all()
  return render(request, 'category_list.html', {'organizations': organizations, 'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def memberListView(request):
  return render(request, 'member_list.html', {'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def individualMemberListView(request):
  return render(request, 'individual_member_list.html', {'name': request.user.get_full_name()})

@login_required
@require_http_methods(["GET"])
def organizationListView(request):
  return render(request, 'organization_list.html', {'name': request.user.get_full_name()})


# ================== LIST Data Views =========================

@login_required
@require_http_methods(["GET"])
def bargainingUnitDataView(request):
  bargainingUnits = models.BargainingUnit.objects.select_related(
                        'organization').values('id', 'name',
                        'agreementStart', 'agreementEnd', 'claimTime',
                        'dues_percent', 'dues_min', 'organization__name',
                        'officer', 'last_reset')
  return JsonResponse(list(bargainingUnits), safe=False)


@login_required
@require_http_methods(["GET"])
def beneficiaryDataView(request):
  beneficiaries = models.Beneficiary.objects.select_related('member', 'member'
                                ).values('id', 'fname', 'mname', 'lname',
                                'dob', 'sex', 'city', 'parish', 'email',
                                'telephone', 'member__fname', 'member__lname')
  return JsonResponse(list(beneficiaries), safe=False)


@login_required
@require_http_methods(["GET"])
def branchDataView(request, pk=None):
  branches = models.Branch.objects.filter(organization=pk).select_related(
                          'organization__name').values('id', 'location',
                          'organization__name')
  return JsonResponse(list(branches), safe=False)


@login_required
@require_http_methods(["GET"])
def categoryDataView(request, pk=None):
  categories = models.Category.objects.filter(organization=pk).select_related(
                            'bargainingUnit', 'organization',
                            ).values('id', 'name', 'rateOfIncrease', 'lastIncrease',
                            'nextIncrease', 'increasePeriod', 'currentPeriod',
                            'increaseHistory', 'bargainingUnit__name',
                            'organization__name')
  return JsonResponse(list(categories), safe=False)


@login_required
@require_http_methods(["GET"])
def buCategoriesDataView(request, pk=None):
  categories = models.Category.objects.filter(
                            Q(nextIncrease__lte=now) | Q(nextIncrease__isnull=True),
                            bargainingUnit=pk).select_related(
                            'bargainingUnit', 'organization'
                            ).values('id', 'name', 'rateOfIncrease',
                            'lastIncrease', 'nextIncrease', 'increasePeriod',
                            'currentPeriod', 'increaseHistory',
                            'bargainingUnit__name', 'organization__name')
  return JsonResponse(list(categories), safe=False)


@login_required
@require_http_methods(["GET"])
def buDelegatesDataView(request, pk=None):
  members = models.Member.objects.filter(
                            Q(membership='CD') | Q(membership='D'),
                            bargainingUnit=pk).select_related(
                            'organization', 'category'
                            ).values('id', 'nwuid', 'fname', 'mname', 'lname',
                            'sex', 'position', 'telephone', 'email', 'membership',
                            'membership', 'category__name', 'organization__name')
  return JsonResponse(list(members), safe=False)


@login_required
@require_http_methods(["GET"])
def memberDataView(request, status=None):
  members = models.Member.objects.select_related('bargainingUnit',
                      'organization', 'category'
                      ).values('id', 'nwuid', 'fname', 'lname', 'dob',
                      'sex', 'position', 'telephone', 'email',
                      'category__name', 'organization__name',
                      'bargainingUnit__name')
  return JsonResponse(list(members), safe=False)


@login_required
@require_http_methods(["GET"])
def individualMemberDataView(request):
  dataset = models.Member.objects.filter(bargainingStatus='I')
  members = dataset.select_related('bargainingUnit',
                      'organization', 'category'
                      ).values('id', 'nwuid', 'fname', 'lname', 'dob',
                      'sex', 'position', 'telephone', 'email',
                      'status', 'category__name', 'organization__name')
  return JsonResponse(list(members), safe=False)


@login_required
@require_http_methods(["GET"])
def organizationDataView(request):
  organizations = models.Organization.objects.values('id', 'name', 'address',
                      'telephone', 'contact_name', 'contact_tel', 'budgetStart',
                      'budgetEnd')
  return JsonResponse(list(organizations), safe=False)