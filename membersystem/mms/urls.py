from django.conf.urls import url

import views



urlpatterns = [
    url(r'^$', views.homeView, name='dashboard'),
    url(r'^login/$', views.loginView, name='login'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^thankyou/$', views.thankyou, name='thankyou'),
    url(r'^ratio/$', views.ratio, name='ratio'),

    url(r'^assistant/contracts/$', views.contracts, name='contracts'),
    url(r'^assistant/budgets_start/$', views.budgets_start, name='budgets_start'),
    url(r'^assistant/budgets_end/$', views.budgets_end, name='budgets_end'),
    url(r'^assistant/birthdays/$', views.birthdays, name='birthdays'),
    url(r'^assistant/birthdays/today/$', views.birthdays_today, name='birthdays_today'),
    url(r'^assistant/roi_due/$', views.roi_due, name='roi_due'),
    url(r'^assistant/apply_roi/(?P<pk>\d+)/$', views.apply_ROI, name='apply_roi'),
    url(r'^assistant/rate_of_increase/$', views.rateofincrease, name='rateofincrease'),
    url(r'^assistant/reset_agreement/$', views.reset_agreement, name='reset_agreement'),
    url(r'^assistant/reset_agreement/(?P<pk>\d+)/$', views.reset_agreement_bu, name='reset_agreement_bu'),
    url(r'^assistant/warnings/$', views.warnings, name='warnings'),
    url(r'^assistant/delegate_ratio/(?P<pk>\d+)/$', views.delegate_ratio_list, name='delegate_ratio'),
    url(r'^assistant/delegates/$', views.buDelegatesListView, name='delegate_list'),
    url(r'^assistant/individual_members/$', views.individualMemberListView, name='individual_members'),
    url(r'^assistant/officers/$', views.officers, name='officers'),

    url(r'^bargaining_unit/$', views.bargainingUnitView, name='bargaining_unit'),
    url(r'^bargaining_unit/(?P<pk>\d+)/$', views.bargainingUnitView, name='bargaining_unit_instance'),
    url(r'^bargaining_unit/(?P<pk>\d+)/categories/$', views.buCategoriesDataView, name='bu_categories_data'),
    url(r'^bargaining_unit/(?P<pk>\d+)/delegates/$', views.buDelegatesDataView, name='bu_delegates'),
    url(r'^bargaining_units/$', views.bargainingUnitListView, name='bargaining_units'),
    url(r'^bargaining_units/data/$', views.bargainingUnitDataView, name='bargaining_units_data'),

    url(r'^beneficiary/$', views.beneficiaryView, name='beneficiary'),
    url(r'^beneficiary/(?P<pk>\d+)/$', views.beneficiaryView, name='beneficiary_instance'),
    url(r'^beneficiaries/$', views.beneficiaryListView, name='beneficiaries'),
    url(r'^beneficiaries/data/$', views.beneficiaryDataView, name='beneficiaries_data'),

    url(r'^branch/$', views.branchView, name='branch'),
    url(r'^branch/(?P<pk>\d+)/$', views.branchView, name='branch_instance'),
    url(r'^branches/$', views.branchListView, name='branches'),
    url(r'^branches/(?P<pk>\d+)/data/$', views.branchDataView, name='branches_data'),

    url(r'^category/$', views.categoryView, name='category'),
    url(r'^category/(?P<pk>\d+)/$', views.categoryView, name='category_instance'),
    url(r'^category/(?P<pk>\d+)/update_roi/$', views.update_ROI, name='update_roi'),
    url(r'^categories/$', views.categoryListView, name='categories'),
    url(r'^categories/(?P<pk>\d+)/data/$', views.categoryDataView, name='categories_data'),

    url(r'^member/$', views.memberView, name='member'),
    url(r'^member/(?P<pk>\d+)/$', views.memberView, name='member_instance'),
    url(r'^members/$', views.memberListView, name='members'),
    url(r'^members/data/$', views.memberDataView, name='members_data'),
    url(r'^members/individual/data/$', views.individualMemberDataView, name='individual_members_data'),

    url(r'^organization/$', views.organizationView, name='organization'),
    url(r'^organization/(?P<pk>\d+)/$', views.organizationView, name='organization_instance'),
    url(r'^organizations/$', views.organizationListView, name='organizations'),
    url(r'^organizations/data/$', views.organizationDataView, name='organizations_data'),
]

handler404 = 'mms.views.pagenotfound'
handler403 = 'mms.views.access_denied'