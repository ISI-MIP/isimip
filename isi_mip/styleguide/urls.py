from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from .views import StyleguideView

app_name = 'styleguide'

urlpatterns = [
    re_path(_(r'^$'), StyleguideView.as_view(), name='styleguide'),
    re_path(_(r'^mockups/(?P<template>.*)/$'), StyleguideView.as_view(), name='styleguide'),
]
