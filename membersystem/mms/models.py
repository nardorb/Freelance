# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible



bargainingStatus = [
  ('I', 'Individual Member'),
  ('BU', 'Bargaining Unit Represented')
]

membership_options = [
  ('M', 'Member'),
  ('D', 'Delegate'),
  ('CD', 'Chief Delegate'),
  ('O', 'Officer')
]

parishes = [
  ('Clarendon', 'Clarendon'),
  ('Hanover', 'Hanover'),
  ('Kingston', 'Kingston'),
  ('Manchester', 'Manchester'),
  ('Portland', 'Portland'),
  ('St. Andrew', 'St. Andrew'),
  ('St. Ann', 'St. Ann'),
  ('St. Catherine', 'St. Catherine'),
  ('St. Elizabeth', 'St. Elizabeth'),
  ('St. James', 'St. James'),
  ('St. Mary', 'St. Mary'),
  ('St. Thomas', 'St. Thomas'),
  ('Trelawny', 'Trelawny'),
  ('Westmoreland', 'Westmoreland'),
]

salary_options =[
  ('Fortn', 'Fortnightly'),
  ('Month', 'Monthly')
]

sex_options = [
  ('M', 'Male'),
  ('F', 'Female')
]

status_options = [
  ('active', 'Active'),
  ('inactive', 'Inactive'),
  ('deceased', 'Deceased')
]

@python_2_unicode_compatible
class BargainingUnit(models.Model):
  """
  Represents a Bargaining Unit which exists as an entity within an
  Organization consisting of members.
  BargainingUnit exists in a many to one relationship with Organization
  and a one to many relationship with Member.
  """
  name = models.CharField(max_length=200, unique=True)
  agreementStart = models.DateField()
  agreementEnd = models.DateField()
  claimTime = models.DateField()
  organization = models.ForeignKey('Organization')
  officer = models.CharField(max_length=200)
  dues_percent = models.PositiveIntegerField()
  dues_min = models.PositiveIntegerField()
  last_reset = models.DateField(null=True, blank=True)

  def __str__(self):
    return '%s: %s' % (self.organization, self.name)

  class Meta:
    permissions = (("can_reset", "Can reset agreement"),)


@python_2_unicode_compatible
class Beneficiary(models.Model):
  """
  Represents a beneficiary of a NWU member. Exists in a one to one
  relationship with Member.
    """
  fname = models.CharField(max_length=50)
  mname = models.CharField(max_length=50)
  lname = models.CharField(max_length=50)
  dob = models.DateField()
  sex = models.CharField(max_length=1, choices=sex_options)
  city = models.CharField(max_length=100)
  parish = models.CharField(max_length=100, choices=parishes)
  email = models.EmailField(unique=True, null=True, blank=True)
  telephone = models.CharField(max_length=15, unique=True, null=True, blank=True)
  member = models.ForeignKey('Member')

  def __str__(self):
    return '%s %s' % (self.fname, self.lname)

  class Meta:
    verbose_name_plural = "Beneficiaries"


@python_2_unicode_compatible
class Branch(models.Model):
  """
  Represents a Bargaining Unit which exists as an entity within an
  Organization consisting of members.
  BargainingUnit exists in a many to one relationship with Organization
  and a one to many relationship with Member.
  """
  location = models.CharField(max_length=200)
  organization = models.ForeignKey('Organization')

  def __str__(self):
    return '%s: %s' % (self.organization, self.location)

  class Meta:
    verbose_name_plural = "Branches"


@python_2_unicode_compatible
class Category(models.Model):
  """
  Represents the category of worker to which each member belongs
  """
  name = models.CharField(max_length=200, unique=True)
  rateOfIncrease = models.FloatField(null=True, blank=True)
  lastIncrease = models.DateField(null=True, blank=True)
  nextIncrease = models.DateField(null=True, blank=True)
  increasePeriod = models.PositiveIntegerField(null=True, blank=True)
  currentPeriod = models.PositiveIntegerField(default=1)
  increaseHistory = models.CharField(null=True, blank=True, max_length=20)
  bargainingUnit = models.ForeignKey('BargainingUnit', null=True, blank=True)
  organization = models.ForeignKey('Organization')

  def __str__(self):
     return '%s: %s' % (self.organization, self.name)

  class Meta:
    verbose_name_plural = "Categories"
    permissions = (("can_apply_roi", "Can apply rate of increase"),)


@python_2_unicode_compatible
class Member(models.Model):
  """
  Represents a worker who is represented by the NWU. Member exist in a many to
  one relationship with Organization, many to one relationship with
  BargainingUnit and a one to one relationship with Beneficiary.
  """
  nwuid = models.CharField(max_length=12, unique=True, null=True, blank=True)
  fname = models.CharField(max_length=50)
  mname = models.CharField(max_length=50)
  lname = models.CharField(max_length=50)
  dob = models.DateField()
  sex = models.CharField(max_length=1, choices=sex_options)
  city = models.CharField(max_length=100)
  parish = models.CharField(max_length=100, choices=parishes)
  position = models.CharField(max_length=100)
  telephone = models.CharField(max_length=15, unique=True)
  email = models.EmailField(unique=True)
  salary = models.PositiveIntegerField()
  salary_type = models.CharField(max_length=5, choices=salary_options)
  dues = models.PositiveIntegerField(null=True, blank=True)
  employmentStart = models.DateField()
  employmentEnd = models.DateField(null=True, blank=True)
  unionStart = models.DateField()
  unionEnd = models.DateField(null=True, blank=True)
  status = models.CharField(max_length=8, choices=status_options)
  membership = models.CharField(max_length=2, choices=membership_options)
  bargainingStatus = models.TextField(max_length=2, choices=bargainingStatus)
  bargainingUnit = models.ForeignKey('BargainingUnit', null=True, blank=True)
  category = models.ForeignKey('Category', null=True, blank=True)
  organization = models.ForeignKey('Organization')
  branch = models.ForeignKey('Branch', null=True, blank=True)
  notes = models.TextField(max_length=500, null=True, blank=True)

  def save(self, *args, **kwargs):
    """
    Overrides the inbuilt Django save function to Auto-generate
    an NWU Member ID each time a new instance is created.
    Object is saved initially to trigger Django AutoField operation
    and applying a pk (next value in sequence) as id which is then
    prepended with 'NWU' and padded with leading 0's to create a
    12 character alphanumeric nwuid. [Key-space ~1,000,000,000].
    Dues are auto generated based on Bargaining Unit specified
    salary percentage or minimum payment (the greater of the two).
    """
    if not self.pk:
      super(Member, self).save(*args, **kwargs)
      self.nwuid = 'NWU' + str(self.id).zfill(9)

    if (self.salary_type == 'Fortn'):
      salary_percentage = ((self.salary*2)*self.bargainingUnit.dues_percent)/100
    else:
      salary_percentage = (self.salary*self.bargainingUnit.dues_percent)/100

    if (salary_percentage > self.bargainingUnit.dues_min):
      self.dues = salary_percentage
    else:
      self.dues = self.bargainingUnit.dues_min

    super(Member, self).save(*args, **kwargs)

  def __str__(self):
    return '%s %s' % (self.fname, self.lname)


class Message(models.Model):
  """
  Represents system notification messages being sent to users logged in to the
  system.
  """
  assignee = models.CharField(max_length=191)
  message = models.TextField(max_length=500)
  status = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class Organization(models.Model):
  """
  Represents an organization or company that has employees who are represented
  by the NWU. Organization exists in a one to many relationship with Member
  and  a one to many relationship with BargainingUnit.
  """
  name = models.CharField(max_length=200, unique=True)
  address = models.CharField(max_length=500)
  telephone = models.CharField(max_length=15, unique=True)
  contact_name = models.CharField(max_length=200)
  contact_tel = models.CharField(max_length=15)
  budgetStart = models.DateField()
  budgetEnd = models.DateField()

  def __str__(self):
    return self.name