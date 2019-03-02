from django.shortcuts import render, HttpResponse
from django import forms
from django.forms import formset_factory

from formset import models


class MultiPermissionForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    menu_id = forms.ChoiceField(
        choices=[(None, '------')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    pid_id = forms.ChoiceField(
        choices=[(None, '-------')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list('id', 'title')


def multi_add(request):
    """
    批量添加
    :param request:
    :return:
    """
    formset_class = formset_factory(MultiPermissionForm, extra=2)  # 在内部生成2个form表单
    if request.method == 'GET':
        formset = formset_class()
        return render(request, 'multi_add.html', {'formset': formset})
    formset = formset_class(data=request.POST)
    # [form(字段,错误信息),form(字段,错误信息),form(字段,错误信息)......]
    if formset.is_valid():
        flag = True
        # print(formset.cleaned_data)  # 如果不填写任何内容，formset就不会进行表单验证，而提交过来两空字典 [{}, {}]
        # [{},{},{}......]
        post_row_list = formset.cleaned_data  # 检查formset中有没有错误信息，没有则将用户提交的数据取到。有错误信息就报错
        for i in range(0, formset.total_form_count()):
            row = post_row_list[i]
            if not row:
                continue
            try:
                obj = models.Permission(**row)
                obj.validate_unique()
                obj.save()
                # post_row_list[i]
                # formset.errors[i]  # 如果这一句执行了，cleaned_data就会检测到错误信息从而报错，所以要在for循环前给cleaned_data赋一个变量
            except Exception as e:
                formset.errors[i].update(e)
                flag = False
        if flag:
            return HttpResponse('提交成功')
        else:
            return render(request, 'multi_add.html', {'formset': formset})
    return render(request, 'multi_add.html', {'formset': formset})
