from django.conf.urls import url, include

from workflow.views import Index ,TicketCreate#, MyTicket, MyToDoTicket, MyRelatedTicket, AllTicket, TicketDetail, TicketCreate

urlpatterns = [
    url(r'^$', Index.as_view(), name='workflow-index'),
    #url(r'^my/$', MyTicket.as_view(), name='ticket-my'),
    #url(r'^todo/$', MyToDoTicket.as_view(), name='ticket-my-todo'),
    #url(r'^myrelated/$', MyRelatedTicket.as_view(), name='ticket-my-related'),
    #url(r'^all/$', AllTicket.as_view(), name='ticket-all'),
    #url(r'^$', WorkflowView.as_view(), name='workflow-all'),
    #url(r'^(?P<workflow_id>[0-9]+)/init_state',
        #WorkflowInitView.as_view(), name='workflow-init'),
    #url(r'^states/(?P<state_id>[0-9]+)', StateView.as_view()),
    #url(r'^ticket/(?P<ticket_id>[0-9]+)/$',
        #TicketDetail.as_view(), name='ticketdetailtable'),
    url(r'^ticket/(?P<workflow_id>[0-9]+)/new/$',
        TicketCreate.as_view(), name='ticketcreate'),
]
