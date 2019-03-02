from django.contrib import admin
from django.urls import path, re_path

from formset import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'multi_add', views.multi_add),

]
