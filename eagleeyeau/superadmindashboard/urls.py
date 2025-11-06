from django.urls import path
from .views import TermsAndConditionsView, PrivacyPolicyView

urlpatterns = [
    path('terms-and-conditions/', TermsAndConditionsView.as_view(), name='terms-and-conditions'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]
