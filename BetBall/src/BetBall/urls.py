from django.conf.urls.defaults import *
from BetBall.bet.page import *
import os
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^BetBall/', include('BetBall.foo.urls')),
     (r'^matches/', listTodayMatches),
     (r'^viewMatches/(?P<year>\d{4})-(?P<month>\d{2})-(?P<date>\d{2})/$', viewMatches),
     (r'^allmatches/', listTodayAllMatches),
     (r'^viewGambler/', viewGambler),
     (r'^admin/', admin),
     (r'^adminLogout/', adminLogout),
     (r'^bet/(\d{1,10})/(\d{1,10})/$', betMatch),
     (r'^openMatch/(\d{1,10})/$', openMatch),
     (r'^closeMatch/(\d{1,10})/$', closeMatch),
     (r'^openGambler/(\d{1,10})/$', openGambler),
     (r'^closeGambler/(\d{1,10})/$', closeGambler),
     (r'^search/', search),
     (r'^register/', register),
     (r'^gologin/', gologin),
     (r'^saveRegister/', saveRegister),
     (r'^adminLogin/', adminLogin),
     (r'^login/', login),
     (r'^recharge/', recharge),
     (r'^logout/', logout),
     (r'^myaccount/', myaccount),
     (r'^updateAccount/', updateAccount),
     (r'^mybet/', mybet),
     (r'^refreshMatches/', refreshMatches),
     (r'^image/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(globals()["__file__"]) + '/image'})
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
