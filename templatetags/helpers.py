import datetime
import re
import sys
import os
import django

from django import template
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.utils.html import mark_safe
from django.utils.module_loading import import_string
from django.conf import settings
from django.urls import reverse

from util.util import *


register = template.Library()

"""
These are functions that are available in templates (as long as the template has {% load helpers %} in it near the top!).

They are split into two parts.

The first section is general functions, tested in util/test/test_helpers.py

The second section is functions that generate HTML for the generic templates, tested in util/test/test_helpers_html.py




"""







@register.simple_tag
def site_data():
    html = '<hr/><small><i>Debugging data</i>'
    html += '<br/>F2DB_PY version: ' + settings.VERSION
    html += '<br/>Mode: ' + os.environ['f2_mode']
    html += '<br/>Python version: ' + sys.version
    html += '<br/>Django version: ' + django.get_version()    
    return mark_safe(html + '</small>')




@register.simple_tag
def today():
    return date_only(datetime.datetime.now())


@register.filter
def date_only(datetime):
    if datetime:
        return datetime.strftime("%d/%b/%y")
    return '--'

@register.filter
def date_time(datetime):
    if datetime:
        return datetime.strftime("%H:%M %d/%b/%y")
    return '--'

@register.simple_tag
def time_stamp(obj):
    s = '<small>'
    s += 'Record created at '
    s += date_time(obj.created_at)
    s += ' | Record last updated at '
    s += date_time(obj.updated_at)
    s += ' | Times in GMT'
    s += '</small>'
    return mark_safe(s)

# The link_data should be in the format:
#    {'klass':GenericSampleMetaDatum, 'lst':['Create']}
# If a link is to a specific record, you need to pass the object too:
#    {'klass':CylinderEvent, 'obj':obj, 'lst':['List', 'Edit']}
@register.simple_tag
def extra_links(link_data):
    if not link_data or not 'lst' in link_data:
        #print('do nothing')
        return ''
        
    links = []
    for el in link_data['lst']:
        if el == 'List':
            name = link_data['klass'].URL_NAME
            url = reverse(name)
            s = '<a href="' + url + '">List</a>'
            links.append(s)
        elif el == 'Search':
            name = link_data['klass'].URL_NAME + '_search'
            url = reverse(name)
            s = 'Search: <form action="' + url + '" style="display:inline">'
            s += '<input type="text" name="term" style="height:9px;font-size:10pt" id="search_box"/>'
            s += '</form>'
            links.append(s)
        elif el == 'New':
            name = link_data['klass'].URL_NAME + '_new'
            url = ''
            url = reverse(name)
            s = '<a href="' + url + '">' + el + '</a>'
            links.append(s)
        elif isinstance(el, str):
            name = link_data['klass'].URL_NAME + '_' + _linkify(el)
            url = ''
            if 'obj' in link_data:
                url = reverse(name, args=[link_data['obj'].id])
            else:
                url = reverse(name)
            s = '<a href="' + url + '">' + el + '</a>'
            links.append(s)
        else:
            name = link_data['klass'].URL_NAME + '_' + el[0]
            url = ''
            if 'obj' in link_data:
                url = reverse(name, args=[link_data['obj'].id])
            else:
                url = reverse(name)
            s = '<a href="' + url + '">' + el[1] + '</a>'
            links.append(s)
    html = '<br/><i>ACTIONS:</i> ' + ' | '.join(links)
    if 'extra' in link_data:
        html += link_data['extra']
    return mark_safe(html)


# Internal function, not unit tested
def _linkify(s):
    return s.lower().replace(' ', '_')


# Will remove anything in parentheses, including brackets
def _no_parenthesis(s):
    return re.sub(r"\(.*\)", "", s)

"""
def get_reverse(name, args=None):
    try:
        reverse(name, args)
    except Exception e:
        print()
        raise e
"""


"""
Gives an HTML snippet that summarises the given user's permissions.
Not unit tested; not sure how and not that important as it is only useful during development.
"""
@register.simple_tag
def permissions(user):

    html = '<div id="show_div" onclick="document.getElementById(\'show_div\').style.display = \'none\';document.getElementById(\'hide_div\').style.display = \'block\'" style="color:blue">Show user permissions (click again to hide it)</div>'
    html += '<div id="hide_div" onclick="document.getElementById(\'show_div\').style.display = \'block\';document.getElementById(\'hide_div\').style.display = \'none\'" style="display:none">'


    if user.is_anonymous:
        return mark_safe('<p>No user logged in</p>')
    
    html += '<h5>User Permissions</h5>'
    lst = user.user_permissions.all()
    html += '<p>Permissions set on a per-user basis (' + str(len(lst)) + ')</p><ul>'
    for el in lst:
        html += '<li>' + str(el) + ' (' + el.codename + ')</li>'    
    html += '</ul>'

    #lst = Permission.objects.filter(group__user=user)
    #html += '<p>Permissions set on a group-wise basis (' + str(len(lst)) + ')</p><ul>'
    #for el in lst:
    #    html += '<li>' + str(el) + ' (' + el.codename + ')</li>'
    #html += '</ul>'

    #lst = Group.objects.filter(group__user=user)
    lst = user.groups.all()
    html += '<p>Permission groups (' + str(len(lst)) + ')</p><ul>'
    for el in lst:
        sublst = el.permissions.all()
        html += '<li>' + str(el) + ' (' + str(len(sublst)) + ')</li><ul>'
        for subel in sublst:
            html += '<li>' + str(subel) + ' (' + subel.codename + ')</li>'
        html += '</ul>'
    html += '</ul>'

    if user.is_superuser:
        html +=  '<p>Superuser!</p>'

    html += '</div>'

    #print(html)
    return mark_safe(html)




# So we can do loops in templates from 1 to number
@register.filter(name='times') 
def times(number):
    return range(1, number)

# So we can do loops in templates from 0 to number
@register.filter(name='times0') 
def times0(number):
    return range(0, number)







# Get a value from an object, using the object's get method
@register.simple_tag
def get(obj, cell, metal):
    return obj.get(cell, metal)






"""
The following functions are for creating HTML. They do so on the basis of meta_data.
Details in docs\docs\generic_views.txt
"""






"""
Creates HTML to display the data - a list of objects - in a table.
meta_data defines each field and how to display it.
options determines if we have "show", "edit" and "delete" options.
"""
@register.simple_tag
def to_table(data, meta_data, options):
    html = '<table>'

    # Table headings
    html += '  <tr>'
    for col in meta_data:
        if 'condition' in col:
            continue
        if 'no_list' not in col and 'edit_only' not in col:
            html += '<th>'
            html += _no_parenthesis(col['heading'])
            html += '</th>\n'
    for s in options:
        html += '<th>&nbsp</th>'
    html += '  </tr>\n\n'

    # Table body
    count = 0
    row_classes = ['odd', 'even']
    for row in data:
        html += f'  <tr class={row_classes[count % 2]}'
        
        if hasattr(row, 'greyed_out') and row.greyed_out():
            html += ' style="color:grey"'
        html += '>'
        count += 1
        
        # Each column is a field
        for col in meta_data:
            if 'condition' in col:
                continue
            if 'no_list' not in col:
                html += interpolate('<td>{value}</td>\n', col, row)
                
        # Add links at the end of the row
        for s in options:
            if s == 'Enable':
                if row.greyed_out():
                    html += '<td><a href="' + str(row.id) + '/enable">Enable</a></td>'
                else:
                    html += '<td><a href="' + str(row.id) + '/disable">Disable</a></td>'

            elif s == 'Show':
                html += '<td><a href="' + str(row.id) + '">Show</a></td>'
                
            elif type(s) == dict:
                if 'condition' in s and not s['condition'](row):
                    html += '<td></td>'
                elif 'link' in s:
                    html += f'<td><a href="{row.id}/{s["link"]}">{s["name"]}</a></td>'
                else:
                    html += f'<td><a href="{row.id}/{_linkify(s["name"])}">{s["name"]}</a></td>'
                
            else:
                html += f'<td><a href="{row.id}/{_linkify(s)}">{s}</a></td>'

        html += '  </tr>\n\n'
    
    html += '</table>\n\n'
    return mark_safe(html)
    
    


@register.simple_tag
def to_show(obj, meta_data, options):
    html = ''

    if 'topics' in options:
        for topic in options['topics']:
            html += '<hr/>\n<b><i>' + topic + '</i></b>\n'
            for row in meta_data:
                if 'topic' in row and row['topic'] == topic:
                    html += interpolate('<p><b>{name}:</b> {value}</p>\n', row, obj, True)
    else:
        for row in meta_data:
            if 'list_only' in row:
                continue
            if 'condition' in row:
                result = row['condition'](obj)
                if result:
                    html += f'<b><i>{result}</i></b>\n'
                else:
                    return mark_safe(html)
            else:
                html += interpolate('<p><b>{name}:</b> {value}</p>\n', row, obj)
    
    return mark_safe(html)




"""
Used internally to fill out an HTML snippet. The HTML should have {name} and {value} in it as place holders.
The former will be replaced by the name of the attribute, while the latter by its value.
col is the meta_data for a single column as passed to the above functions
obj is the Django object
It will process the value according to what it finds in the meta_data
"""
def interpolate(html, col, obj, optional = False):
    if 'heading' not in col:
        return ''
        
    if 'edit_only' in col:
        return ''
    name = col['heading']
    raw_value = ''
    if 'column' in col:
        if not hasattr(obj, col['column']):
            print('No attribute found')
            print(col['column'])
            print(dir(obj))
        raw_value = getattr(obj, col['column'])  # could be any type!
        if raw_value == None and ('optional' in col or optional):
            return ''
    
    value = ''
    field_type = None
    if 'column' in col:
        field_type = get_field_type(obj, col['column'])
    if 'options' in col:
        if raw_value or raw_value == 0:
            value = col['options'][raw_value]
        else:
            value = '---'

    # elif 'options_from_hash' in col:
        # print("ERROR: 'options_from_hash' not yet implemented")
        # value = '---'
        
    elif 'options_from_array' in col:
        # raw_value is the index of the selected value
        if raw_value or raw_value == 0:
            if isinstance(col['options_from_array'][raw_value], str):
                value = col['options_from_array'][raw_value]
            else:
                attribute = col['attribute'] if 'attribute' in col else 'name'
                value = col['options_from_array'][raw_value][attribute]
        else:
            value = '---'

    elif 'options_from_table' in col:
        # raw_value is the index of the selected value
        attribute = col['attribute'] if 'attribute' in col else 'name'
        if raw_value:
            klass = import_string(col['options_from_table'])
            try:
                obj = klass.objects.get(id=raw_value)
                value = getattr(obj, attribute)
            except Exception as e:
                print("Exception in helpers/interpolate")
                print(f"id={raw_value}")
                print(f"table={col['options_from_table']}")
                print(f"attribute={attribute}")
                print(col)
                raise e
                
        else:
            value = '---'
        
    elif 'func' in col:
        value = col['func'](obj)
    elif 'link_func' in col:
        value = '<a href="' + col['link_func'](obj) + '">' + col['heading'] + '</a>'
    elif 'ex_link_func' in col:
        value = '<a href="' + col['ex_link_func'](obj) + '" target="_blank">' + col['heading'] + '</a>'
    elif field_type == 'DateField' and col['column']:
        if raw_value:
            #print('col=', col)
            #print('Date=', raw_value)
            value = raw_value.strftime('%d/%b/%Y')
        else:
            value = 'Not set'
    elif raw_value == None:
        value = None
    else:
        value = raw_value
        
    html = html.replace('{name}', name)
    if value == None:
        html = html.replace('{value}', '-')
    elif 'money' in col and type(value) == int:
        html = html.replace('{value}', "{:.2f}".format(value/100))
    elif 'pence' in col and type(value) == int:
        html = html.replace('{value}', '&pound;' + "{:.2f}".format(value/100))
    elif 'pounds' in col and type(value) == int:
        html = html.replace('{value}', '&pound;' + str(value))
    elif 'units' in col:
        html = html.replace('{value}', str(value) + col['units'])
    else:
        html = html.replace('{value}', str(value))
    return html




"""
Gives an HTML snippit; a table with widgets. The obj is the object (record) to be edited; meta_data is an array with data about each row  in the table (or fiekd in the record); options is not currently used.
Adds a submit button, but does not inclide the "form" tags.
"""
@register.simple_tag
def to_edit(obj, meta_data, options):
    html = '<table>'

    for row in meta_data:
        if 'no_edit' in row:
            continue
        if 'list_only' in row:
            continue
        elif 'columns' in row:
            html += multi_widget_row(row, obj)
        elif 'column' not in row:
            html += interpolate('<tr><td>{name}</td><td> {value}</td></tr>\n' , row, obj)
        elif 'read_only' in row:
            html += interpolate('<tr><td>{name}</td><td> {value}</td></tr>\n' , row, obj)
            html += '<input type="hidden" name="' + row['column'] + '" value="' + _to_str(obj, row) + '"/>'
        else:
            html += widget_row(row, obj)

    html += '<tr><td colspan="2" style="text-align:right"><input type="submit" value="Submit"/></td></tr>\n'        
    html += '</table>\n\n'
    return mark_safe(html)



def _to_str(obj, row):
    value = getattr(obj, row['column'])
    if value == None:  # do not want to catch zero here
        return ''
       
    if 'options' in row:
        value = row['options'][value]
       
    if 'options_from_array' in row: # and not 'read_only' in meta_data:
        if isinstance(row['options_from_array'][value], str):
            value = row['options_from_array'][value]
        else:
            attribute = row['attribute'] if 'attribute' in row else 'name'
            value = row['options_from_array'][value][attribute]

    if 'options_from_table' in row: # and not 'read_only' in meta_data:
        attribute = row['attribute'] if 'attribute' in row else 'name'
        klass = import_string(row['options_from_table'])
        record = klass.objects.get(id=value)
        value = getattr(record, attribute)

    return str(value)
    


"""
Used internally to fill out an HTML snippet. Exactly as interpolate, but it will insert a widget rather than just the value.
"""
def multi_widget_row(col, obj):
    name = col['heading']
    if 'explanation' in col:
        name += ' [' + col['explanation'] + ']'
 
    # value is an HTML snippet that will get inserted into something later
    value = ''
    for data in col['columns']:
        val = None
        if hasattr(obj, data['column']):
            val = getattr(obj, data['column'])
        if val == None:
            val = ''
        else:
            val = str(val)

        field_type = get_field_type(obj, data['column'])
        size = data['size'] if 'size' in data else 5
        prompt = data['prompt'] if 'prompt' in data else ''
        

        if field_type == 'IntegerField':
            value += '<input name="' + data['column'] + '" type="text" inputmode="numeric" pattern="[0-9]*" value="' + str(val) + f'" size="{size}" placeholder="{prompt}"/>'
            
        elif field_type == 'CharField' or field_type == 'TextField':
            value += '<input name="' + data['column'] + '" type="text" value="' + val + f'" size="{size}" placeholder="{prompt}"/>'
            
        elif field_type == 'BooleanField' and val:
            value += '<input name="' + data['column'] + '" type="checkbox" checked="checked"/>'
            
        elif field_type == 'BooleanField':
            value += '<input name="' + data['column'] + '" type="checkbox"/>'


    html = '<tr><td>{name}</td><td>{value}</td></tr>\n'        
    html = html.replace('{name}', name)
    html = html.replace('{value}', value)
    return html





"""
Used internally to fill out an HTML snippet. Exactly as interpolate, but it will insert a widget rather than just the value.
Followng UK Gov advice, this does not use number input type. https://technology.blog.gov.uk/2020/02/24/why-the-gov-uk-design-system-team-changed-the-input-type-for-numbers/
"""
def widget_row(col, obj):
    name = col['heading']
    if 'explanation' in col:
        name += ' [' + col['explanation'] + ']'
    value = ''
    field_type = get_field_type(obj, col['column'])
    val = getattr(obj, col['column'])
    if not val:
        val = ''
    html = '<tr><td>{name}</td><td>{value}</td></tr>\n'        

    #print(col)

    if field_type == 'TextField' and 'textfield' not in col:
        value = '<textarea cols="80" rows="8" name="' + col['column'] + '">' + val + '</textarea>'
        html = '<tr><td colspan="2">{name}'
        if 'quick_text' in col:
            html += ' <span onclick="addText(\'' + col['column'] + '\', \''
            html += col['quick_text'](obj)
            html += '\')" class="link" id="' + col['column'] + '_copy_link">[Quick text]</span>'
        if val == '' and 'copy_from' in col:
            html += ' <span onclick="copyText(\'' + col['column'] + '\', \'' + col['copy_from']
            html += '\')" class="link" id="' + col['column'] + '_copy_link">[Copy]</span>'
        html += '<br/>{value}</td></tr>\n'

    elif 'options' in col:
        # val is the index of the selected value
        value = create_select(col['column'], col['options'], val)
        
    # elif 'options_from_hash' in col:
        # #val is the index of the selected value
        # attribute = col['attribute'] if 'attribute' in col else 'name'
        # options = []
        # for key in col['options_from_hash']:
            # x = col['options_from_hash'][key]
            # options.append(gettr(x, attribute))
        # value = create_select(col['column'], options, val)
        
    elif 'options_from_array' in col:
        # val is the index of the selected value
        attribute = col['attribute'] if 'attribute' in col else 'name'
        options = []
        for el in col['options_from_array']:
            if isinstance(el, str):
                options.append(el)
            else:
                options.append(el[attribute])
        value = create_select(col['column'], options, val)
        
    elif 'options_from_table' in col:
        # val is the index of the selected value
        attribute = col['attribute'] if 'attribute' in col else 'name'
        options = []
        klass = import_string(col['options_from_table'])
        lst = klass.objects.all()
        index = -1
        for i, el in enumerate(lst):
            options.append(getattr(el, attribute))
            if el.id == val:
                index = i
        value = create_select(col['column'], options, index)
        
    elif 'func' in col:
        value = col['func'](obj)  # !!! not sure how to handle this!!!
        
    elif 'link_func' in col:
        pass
        
    elif field_type == 'DateField':
        date = datetime.datetime.now() if not val or val == '' else val
        date_as_str = str(date)[0:10]
        value = '<input name="' + col['column'] + '" type="date" value="' + date_as_str + '"/>'
        
    elif field_type == 'IntegerField' and 'money' in col:
        x = int(val) if val else 0
        value = '<input name="' + col['column'] + '" type="text" inputmode="numeric" pattern="[0-9.]*" value="' + str(x / 100.0) + '" step="0.01"/>'
        
    elif field_type == 'IntegerField':
        value = '<input name="' + col['column'] + '" type="text" inputmode="numeric" pattern="[0-9]*" value="' + str(val) + '"/>'
        
    elif field_type == 'CharField' or field_type == 'TextField':
        value = '<input name="' + col['column'] + '" type="text" value="' + val + '"/>'
        
    elif field_type == 'BooleanField' and val:
        value = '<input name="' + col['column'] + '" type="checkbox" checked="checked"/>'
        
    elif field_type == 'BooleanField':
        value = '<input name="' + col['column'] + '" type="checkbox"/>'
            
    html = html.replace('{name}', name)
    html = html.replace('{value}', value)
    return html


"""
Gives an HTML snippet for a basic drop-down.
The options should be an array, and val an integer, the index ofthe selected value.
If val is outside the range it is ignored.
"""
def create_select(name, options, val):
    html = '<select name="' + name + '">'
    for i in range(len(options)):
        html += '<option'
        if val == i:
            html += ' selected="selected"'
        html += '>' + options[i] + '</option>'
    html += '</select>'
    return html


