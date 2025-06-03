import datetime

from django import template
from django.utils.html import mark_safe

from computers.models import CyberRiskAssessment

register = template.Library()




@register.simple_tag
def risk_matrix():
    s = "Likelihoods and consequences are represented by numbers, starting from 1 (0 is used to indicate it is not set). The numbers are added together to determine risk. A value over " + str(CyberRiskAssessment.MAX_ACCEPTABLE_BUT) + ' is considered "Unacceptable", a value over ' + str(CyberRiskAssessment.MAX_ACCEPTABLE) + ' is considered "Acceptable but", and a lower figure is considered "Acceptable". This is adapted from the matrix in Appendix F of the SLR data (the "Acceptable but" range is narrowed for higher impacts).'
    
    s += '<div id="show_div" onclick="document.getElementById(\'show_div\').style.display = \'none\';document.getElementById(\'hide_div\').style.display = \'block\'" style="color:blue">Show matrix (click matrix to hide it)</div>'
    s += '<div id="hide_div" onclick="document.getElementById(\'show_div\').style.display = \'block\';document.getElementById(\'hide_div\').style.display = \'none\'" style="display:none">'
    s += '<table><tr><th>&nbsp</th>'
    for el in CyberRiskAssessment.CONSEQUENCES[1:]:
        s += '<th>' + el['severity'] + '</th>'
    
    for i, el in enumerate(CyberRiskAssessment.LIKELIHOOD[1:], 1):
        s += '<tr><td>' + el['frequency'] + '</td>'
        for j in range(1, len(CyberRiskAssessment.CONSEQUENCES)):
            s += '<td>' + CyberRiskAssessment.risk_as_html_generic(i, j) + '</td>'
        s += '</tr>'
    
    s += '</table>'
    s += '</div>'
    
    return mark_safe(s)

