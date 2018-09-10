# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
# from django.contrib.auth.models import Permission
# from django.contrib.admin.models import LogEntry

from models import *


# Register your models here.
class BargainingUnitAdmin(admin.ModelAdmin):
  search_fields = ('name', 'organization',)
class BeneficiaryAdmin(admin.ModelAdmin):
  search_fields = ('fname', 'lname',)
class BranchAdmin(admin.ModelAdmin):
  search_fields = ('location',)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('lastIncrease', 'increasePeriod',
                       'currentPeriod', 'increaseHistory')
class MemberAdmin(admin.ModelAdmin):
    fields = ('nwuid', 'fname', 'mname', 'lname', 'dob', 'sex', 'city',
              'parish', 'position', 'telephone', 'email', 'salary',
              'salary_type','dues', 'employmentStart', 'employmentEnd',
              'unionStart', 'unionEnd', 'status', 'membership', 'organization',
              'bargainingUnit', 'category')
    readonly_fields = ('nwuid', 'dues')
    search_fields = ('nwuid', 'fname', 'lname',)
class OrganizationAdmin(admin.ModelAdmin):
  search_fields = ('name',)

admin.site.register(BargainingUnit, BargainingUnitAdmin)
admin.site.register(Beneficiary, BeneficiaryAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Organization, OrganizationAdmin)