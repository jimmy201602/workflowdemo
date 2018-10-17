from django.views.generic import TemplateView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
try:
    import simplejson as json
except ImportError:
    import json
from django import forms
from django.http import Http404,JsonResponse
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from crispy_forms.bootstrap import AppendedText, PrependedText
import datetime
import time
from workflow.apirequest import WorkFlowAPiRequest

class Index(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        #context['workflows'] = Workflow.objects.all()
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,data = ins.getdata(dict(username='admin', per_page=20, name=''),method='get',url='/api/v1.0/workflows')
        if status:
            context['workflows'] = data['data']['value']
        return context


class TicketDetail(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/ticketdetail.html'

    def get_context_data(self, **kwargs):
        context = super(TicketDetail, self).get_context_data(**kwargs)
        context['ticket_id'] = kwargs.get('ticket_id')
        return context


class TicketCreate(LoginRequiredMixin, FormView):
    template_name = 'workflow/ticketcreate.html'
    success_url = '/'

    def get_form_class(self):
        form_fields = dict()
        workflow_id = self.kwargs.get('workflow_id')

        #get ticket initial data
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(dict(username='admin'),method='get',url='/api/v1.0/workflows/{0}/init_state'.format(workflow_id))
        """
        state_result example
            {
              'data': {
                'id': 6,
                'name': '发起人-新建中',
                'creator': 'admin',
                'gmt_created': '2018-05-10 07:34:45',
                'distribute_type_id': 1,
                'transition': [
                  {
                    'transition_name': '提交',
                    'transition_id': 7
                  }
                ],
                'order_id': 1,
                'participant_type_id': 5,
                'type_id': 1,
                'is_hidden': False,
                'field_list': [
                  {
                    'boolean_field_display': {
                      
                    },
                    'order_id': 20,
                    'default_value': None,
                    'field_name': '标题',
                    'field_choice': {
                      
                    },
                    'field_key': 'title',
                    'field_type_id': 5,
                    'field_value': None,
                    'field_attribute': 2,
                    'field_template': '',
                    'description': '工单的标题'
                  },
                  {
                    'boolean_field_display': {
                      
                    },
                    'order_id': 110,
                    'default_value': '请填写申请vpn的理由',
                    'field_name': '申请原因',
                    'field_choice': {
                      
                    },
                    'field_key': 'vpn_reason',
                    'field_type_id': 55,
                    'field_value': None,
                    'field_attribute': 2,
                    'field_template': '',
                    'description': 'vpn申请原因'
                  }
                ],
                'participant': 'creator',
                'sub_workflow_id': 0,
                'workflow_id': 2,
                'label': {
                  
                }
              },
              'msg': '',
              'code': 0
            }
        """
        state_result = state_result['data']
        #set state_result to kwargs to avoid mutiple time to obtain ticket info
        self.kwargs.update({'state_result':state_result})

        if isinstance(state_result, dict) and 'field_list' in state_result.keys():
            class DynamicForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    self.helper = FormHelper()
                    self.helper.form_class = 'form-horizontal'
                    self.helper.label_class = 'col-md-2'
                    self.helper.field_class = 'col-md-8'
                    # DictionaryField bug
                    self.helper.layout = Layout(
                        *[Div(field['field_key'], css_class='form-group') for field in state_result['field_list']])
                    super(DynamicForm, self).__init__(*args, **kwargs)

            for field in state_result['field_list']:
                FIELD_TYPE_STR = 5  # 字符串类型
                FIELD_TYPE_INT = 10  # 整形类型
                FIELD_TYPE_FLOAT = 15  # 浮点类型
                FIELD_TYPE_BOOL = 20  # 布尔类型
                FIELD_TYPE_DATE = 25  # 日期类型
                FIELD_TYPE_DATETIME = 30  # 日期时间类型
                FIELD_TYPE_RADIO = 35  # 单选框
                FIELD_TYPE_CHECKBOX = 40  # 多选框
                FIELD_TYPE_SELECT = 45  # 下拉列表
                FIELD_TYPE_MULTI_SELECT = 50  # 多选下拉列表
                FIELD_TYPE_TEXT = 55  # 文本域
                FIELD_TYPE_USERNAME = 60  # 用户名，前端展现时需要调用方系统获取用户列表。loonflow只保存用户名
                if field['field_type_id'] == 5:
                    form_fields[field['field_key']] = forms.CharField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                                                                          'required': field['description']},
                                                                      widget=forms.TextInput(attrs={'placeholder': field['field_name']}))
                elif field['field_type_id'] in [10, 15]:
                    form_fields[field['field_key']] = forms.IntegerField(help_text=field['description'], label=field['field_name'],
                                                                         required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                         error_messages={
                        'required': field['description']},
                        widget=forms.NumberInput(attrs={'placeholder': field['field_name']}))
                elif field['field_type_id'] == 20:
                    form_fields[field['field_key']] = forms.BooleanField(help_text=field['description'], label=field['field_name'],
                                                                         required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                         error_messages={'required': field['description']})
                elif field['field_type_id'] == 25:
                    form_fields[field['field_key']] = forms.DateField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                        'required': field['description']},
                        widget=forms.DateInput(attrs={'placeholder': field['field_name'], 'class': 'dateinput'}))
                elif field['field_type_id'] == 30:
                    form_fields[field['field_key']] = forms.DateTimeField(help_text=field['description'], label=field['field_name'],
                                                                          required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                          error_messages={
                        'required': field['description']},
                        widget=forms.DateTimeInput(attrs={'placeholder': field['field_name'], 'class': 'datetimeinput'}))
                elif field['field_type_id'] in [35, 45]:
                    form_fields[field['field_key']] = forms.ChoiceField(help_text=field['description'], label=field['field_name'],
                                                                        required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                        error_messages={
                        'required': field['description']}, choices=[(k, v) for k, v in field['field_choice'].items()])
                elif field['field_type_id'] == [40, 50]:
                    form_fields[field['field_key']] = forms.MultipleChoiceField(help_text=field['description'], label=field['field_name'],
                                                                                required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                                error_messages={
                        'required': field['description']}, choices=[(k, v) for k, v in field['field_choice'].items()])
                elif field['field_type_id'] == 55:
                    form_fields[field['field_key']] = forms.CharField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                        'required': field['description']},
                        widget=CKEditorUploadingWidget(attrs={'placeholder': field['field_name'], 'cols': 20, 'rows': 10}))
                elif field['field_type_id'] == 60:
                    form_fields[field['field_key']] = forms.ChoiceField(help_text=field['description'], label=field['field_name'],
                                                                        required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                        error_messages={
                        'required': field['description']}, choices=[(1,1),(2,2)])
                # handle read only field
                if field['field_attribute'] == 1:
                    form_fields[field['field_key']
                                ].widget.attrs['disabled'] = 'disabled'
        else:
            raise Http404()
        return type('DynamicItemsForm', (DynamicForm,), form_fields)

    def get_context_data(self, **kwargs):
        context = super(TicketCreate, self).get_context_data(**kwargs)
        context['workflow_id'] = self.kwargs.get('workflow_id')
        state_result = self.kwargs.get('state_result',None)
        context['state_result'] = state_result
        #context['msg'] = msg
        if isinstance(state_result, dict) and 'field_list' in state_result.keys() and len(state_result['field_list']) == 0:
            context['noform'] = True
        if isinstance(state_result, dict) and 'transition' in state_result.keys():
            context['buttons'] = state_result['transition']
        return context

    def form_valid(self, form):
        # save ticket
        if 'transition_id' in form.data.keys():
            transition_id = form.data['transition_id']
            form_data = form.cleaned_data
            form_data['transition_id'] = int(transition_id)
            form_data['username'] = self.request.user.username
            form_data['workflow_id'] = int(self.kwargs.get('workflow_id'))
            for key, value in form_data.items():
                if isinstance(value, datetime.datetime):
                    form_data[key] = form.data[key]

            #for test only
            form_data['username'] = 'admin'
            ins = WorkFlowAPiRequest(appname='ops',username='admin')
            status,state_result = ins.getdata(data=form_data,method='post',url='/api/v1.0/tickets')
            print('111',status, state_result)
            # if new_ticket_result:
            # code, data = 0, {'ticket_id': new_ticket_result}
            # else:
            # code, data = -1, {}
        return super().form_valid(form)


class MyTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/my.html'

    def get_context_data(self, **kwargs):
        context = super(MyTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin',category='owner'),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class MyToDoTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/mytodo.html'

    def get_context_data(self, **kwargs):
        context = super(MyToDoTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin',category='duty'),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class MyRelatedTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/myrelated.html'

    def get_context_data(self, **kwargs):
        context = super(MyRelatedTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin',category='relation'),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class AllTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/allticket.html'

    def get_context_data(self, **kwargs):
        context = super(AllTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        #filter ticket in the future if necessary
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')

        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin',category='all'),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class TicketDetailApi(View):
    def get(self, request, *args, **kwargs):
        """
        获取工作流列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        name = request_data.get('name', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        username = request_data.get('username', '')  # 后续会根据username做必要的权限控制

        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin'),method='get',url='/api/v1.0/tickets/{0}'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

class TicketFlowStep(View):
    """
    工单流转step: 用于显示工单当前状态的step图(线形结构，无交叉)
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get(
            'username', request.user.username)  # 可用于权限控制
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin'),method='get',url='/api/v1.0/tickets/{0}/flowsteps'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

class TicketFlowlog(View):
    """
    工单流转记录
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get(
            'username', request.user.username)  # 可用于权限控制
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin'),method='get',url='/api/v1.0/tickets/{0}/flowlogs'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

class TicketTransition(View):
    """
    工单可以做的操作
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get('username', '')
        if not username:
            return api_response(-1, '参数不全，请提供username', '')
        ins = WorkFlowAPiRequest(appname='ops',username='admin')
        status,state_result = ins.getdata(parameters=dict(username='admin'),method='get',url='/api/v1.0/tickets/{0}/transitions'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

#class WorkflowView(View):
    #def get(self, request, *args, **kwargs):
        #"""
        #获取工作流列表
        #:param request:
        #:param args:
        #:param kwargs:
        #:return:
        #"""
        #request_data = request.GET
        #name = request_data.get('name', '')
        #per_page = int(request_data.get('per_page', 10))
        #page = int(request_data.get('page', 1))
        #username = request_data.get('username', '')  # 后续会根据username做必要的权限控制

        #workflow_result_restful_list, msg = WorkflowBaseService.get_workflow_list(
            #name, page, per_page)
        #if workflow_result_restful_list is not False:
            #data = dict(value=workflow_result_restful_list,
                        #per_page=msg['per_page'], page=msg['page'], total=msg['total'])
            #code, msg, = 0, ''
        #else:
            #code, data = -1, ''
        #return api_response(code, msg, data)


#class WorkflowInitView(View):
    #def get(self, request, *args, **kwargs):
        #"""
        #获取工作流初始状态信息，包括状态详情以及允许的transition
        #:param request:
        #:param args:
        #:param kwargs:
        #:return:
        #"""
        #workflow_id = kwargs.get('workflow_id')
        #request_data = request.GET
        #username = request_data.get(
            #'username', request.user.username)  # 后续会根据username做必要的权限控制

        #if not (workflow_id and username):
            #return api_response(-1, '请提供username', '')
        #state_result, msg = WorkflowStateService.get_workflow_init_state(
            #workflow_id)
        #if state_result is not False:
            #code, msg, data = 0, '', state_result
        #else:
            #code, msg, data = -1, msg, ''
        #return api_response(code, msg, data)


#class StateView(View):
    #def get(self, request, *args, **kwargs):
        #"""
        #获取状态详情
        #:param request:
        #:param args:
        #:param kwargs:
        #:return:
        #"""
        #state_id = kwargs.get('state_id')
        #request_data = request.GET
        #username = request_data.get('username', '')  # 后续会根据username做必要的权限控制
        #if not username:
            #return api_response(-1, '请提供username', '')

        #result, msg = WorkflowStateService.get_restful_state_info_by_id(
            #state_id)
        #if result is not False:
            #code, data = 0, result
        #else:
            #code, data = -1, ''
        #return api_response(code, msg, data)