from django.urls import path

import check_api.views

urlpatterns = [
    path('create_check/', check_api.views.create_checks),
    path('new_checks/<str:api_key>/', check_api.views.get_new_checks),
    path('new_checks/', check_api.views.get_new_checks),
    path('check/<str:api_key>/<int:check_id>/', check_api.views.get_pdf),
    path('check/', check_api.views.get_pdf),
]
