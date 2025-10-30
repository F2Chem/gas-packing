from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
#from django.utils.timezone import now
import datetime

from util.util import *



def home(request):
    return render(request, "home.html", {})
    
    
def test_email(request):
    html_content = '<h4>Test email from F2DB</h4>'
    html_content += '<p><i>Sent by:</i> ' + request.user.username + '</p>'
    html_content += '<p><i>Date/time:</i> ' + datetime.datetime.now().strftime("%d/%b/%y %H:%M") + '</p>'
    
    email(request, 'F2DB Test Email', [request.user.email], 'Blank', html_content)
    return render(request, "home.html", {})
    