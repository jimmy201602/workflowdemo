from django.conf.urls import url, include,re_path

from workflow.views import Index ,TicketCreate,AllTicket,TicketDetail,MyTicket,MyToDoTicket, MyRelatedTicket#, , TicketDetail, TicketCreate

urlpatterns = [
    re_path(r'^$', Index.as_view(), name='workflow-index'),
    re_path(r'^my/$', MyTicket.as_view(), name='ticket-my'),
    re_path(r'^mytodo/$', MyToDoTicket.as_view(), name='ticket-my-todo'),
    re_path(r'^myrelated/$', MyRelatedTicket.as_view(), name='ticket-my-related'),
    re_path(r'^all/$', AllTicket.as_view(), name='ticket-all'),
    #url(r'^$', WorkflowView.as_view(), name='workflow-all'),
    #url(r'^(?P<workflow_id>[0-9]+)/init_state',
        #WorkflowInitView.as_view(), name='workflow-init'),
    #url(r'^states/(?P<state_id>[0-9]+)', StateView.as_view()),
    re_path(r'^ticket/(?P<ticket_id>[0-9]+)/$',
        TicketDetail.as_view(), name='ticketdetailtable'),
    re_path(r'^ticket/(?P<workflow_id>[0-9]+)/new/$',
        TicketCreate.as_view(), name='ticketcreate'),
]
