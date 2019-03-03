from django.shortcuts import render, HttpResponse
from django.forms import formset_factory

from formset import models
from .forms.formset import MultiPermissionForm, MultiUpdatePermissionForm


def multi_add(request):
    """
    批量添加
    :param request:
    :return:
    """
    formset_class = formset_factory(MultiPermissionForm, extra=2)
    if request.method == 'GET':
        formset = formset_class()
        return render(request, 'multi_add.html', {'formset': formset})
    formset = formset_class(data=request.POST)
    if formset.is_valid():
        flag = True
        post_row_list = formset.cleaned_data
        for i in range(0, formset.total_form_count()):
            row = post_row_list[i]
            if not row:
                continue
            try:
                obj = models.Permission(**row)
                obj.validate_unique()
                obj.save()
            except Exception as e:
                formset.errors[i].update(e)
                flag = False
        if flag:
            return HttpResponse('提交成功')
        else:
            return render(request, 'multi_add.html', {'formset': formset})
    return render(request, 'multi_add.html', {'formset': formset})


def multi_edit(request):
    formset_class = formset_factory(MultiUpdatePermissionForm, extra=0)  # 默认等于1，如果不想让它多增加一个，就把默认改成0
    if request.method == 'GET':
        formset = formset_class(
            initial=models.Permission.objects.all().values('id', 'title', 'name', 'url', 'menu_id', 'pid_id'))
        return render(request, 'multi_edit.html', {'formset': formset})

    formset = formset_class(data=request.POST)
    if formset.is_valid():
        post_row_list = formset.cleaned_data
        flag = True
        for i in range(0, formset.total_form_count()):
            row = post_row_list[i]
            if not row:
                continue
            permission_id = row.pop('id')
            try:
                permission_obj = models.Permission.objects.filter(id=permission_id).first()
                for key, value in row.items():
                    setattr(permission_obj, key, value)
                permission_obj.validate_unique()
                permission_obj.save()
            except Exception as e:
                formset.errors[i].update(e)
                flag = False
        if flag:
            return HttpResponse('提交成功')
        else:
            return render(request, 'multi_edit.html', {'formset': formset})
    return render(request, 'multi_edit.html', {'formset': formset})
