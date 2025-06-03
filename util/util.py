import datetime
import io
import re
import sys

from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.utils import timezone
from django.utils.module_loading import import_string
from django.urls import path
from django.http import HttpResponse
from django import forms
from django.db import models




def create_url(s):
    if 'runserver' in sys.argv:
        return 'http://andyj:8000/' + s
    else:
        return 'http://f2-app01:9990/' + s








class TimeStampMixin(models.Model):
    # Allow null to allow this to be applied to existing tables
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True





def month_and_year(date):
    return date.strftime('%b/%y')

def day_month_year(date):
    return date.strftime('%d/%b/%y')




def update(request, obj, meta_data):
    create = not obj.created_at
    
    for col in meta_data:
        if 'column' not in col:
            continue
        if col['column'] == 'created_at' or col['column'] == 'updated_at' :
            continue   # These are handled differently - modified automatically for every table
        #if 'read_only' in col:
        #    continue
            
        # This is something we want to handle - but we need to convert to the right type
        #print(col)
        field_type = get_field_type(obj, col['column'])

        if field_type == 'BooleanField':
            # For a Boolean, not present indicates False, so deal with that first
            setattr(obj, col['column'], col['column'] in request.POST)

        else:
            #!!! consider handling None
            try:
                value = request.POST[col['column']]
            except MultiValueDictKeyError:
                print('ERROR: Got a MultiValueDictKeyError when trying to find the key: "' + col['column'] + '"')
                print('This is while trying to process POST data:')
                print(request.POST)
                return  # !!! want to notify user somehow !!!
                
            #print(value)
            if 'options_from_array' in col:
                attribute = col['attribute'] if 'attribute' in col else 'name'
                for i, el in enumerate(col['options_from_array']):
                    if isinstance(el, str):
                        if el == value:
                            setattr(obj, col['column'], i)
                    else:
                        if el[attribute] == value:
                            setattr(obj, col['column'], i)

            elif 'options_from_table' in col:
                attribute = col['attribute'] if 'attribute' in col else 'name'
                options = []
                klass = import_string(col['options_from_table'])
                lst = klass.objects.all()
                for el in lst:
                    if getattr(el, attribute) == value:
                        setattr(obj, col['column'], el.id)

            elif 'options' in col:
                # If the field is read_only, the form will have a hidden widget with the value as a number
                # otherwise the widget will be a dropdown, and the value will be a string
                #if 'read_only' in col:
                #    setattr(obj, col['column'], int(value))
                #else:
                    setattr(obj, col['column'], col['options'].index(value))

            elif value == '':
                setattr(obj, col['column'], None)
            
            elif field_type == 'TextField' or field_type == 'CharField':
                setattr(obj, col['column'], value)
            
            elif field_type == 'IntegerField' and 'money' in col:
                setattr(obj, col['column'], int(float(value) * 100))
    
            elif field_type == 'IntegerField':
                setattr(obj, col['column'], int(value))
    
            elif field_type == 'DecimalField':
                setattr(obj, col['column'], float(value))
    
            elif field_type == 'DateField':
                date = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(obj, col['column'], date)
    
    obj.updated_at = timezone.now()
    if create:
        obj.created_at = timezone.now()
    obj.save()
    messages.add_message(request, messages.SUCCESS, "Record created." if create else "Record updated.")


# Gets the type for the given field, as a string CharFirld, IntegerField, etc.
# For an attribute that is not a database field, will try to fake it.
# Unit tested
def get_field_type(o, attr):    
    
    # Seems to be no way to just ask if the attribute is a field, so search through the list
    for el in o._meta.get_fields():
        if el.name == attr:
            return o._meta.get_field(attr).get_internal_type()
            
    # If it is not a database field and has no value, we cannot tell what it should be so return None
    if not hasattr(o, attr) or getattr(o, attr) == None:
        return None

    # If we were sent the class rather than an instance, we cannot tell what it should be so return None
    if str(type(o)) == "<class 'django.db.models.base.ModelBase'>":
       return None

    # Not a database field, so we fake it!
    if isinstance(getattr(o, attr), str):
        return 'CharField'
    if isinstance(getattr(o, attr), float):
        return 'FloatField'
    if isinstance(getattr(o, attr), int):
        return 'IntegerField'
    raise Exception(f'Failed to match a type for attribute {attr}')



# Unit tested
def search(ary, f):
    for i, el in enumerate(ary):
        if f(el):
            return (i, el)
    return None




# Quick way to add up to the seven standard URLs for a bunch of tables in urls.py
#
# urlpatterns = []
# add_std_to_paths(urlpatterns, views, [
#     'location',
#     'cylinder_event_meta_datum',
#     'cylinder', 
#     ('cylinder_event', '.RU.')
# ])
#
# The lst should be an array of strings oand tuples. If it is a string, URLs for create, read and update are created.
# For a tuple, the first value is the string as before, the second value a four character string.
# Start from "CRUD" and replace any action you do not want with a full stop (as example above).
def add_std_to_paths(urlpatterns, views, lst):    
    urlpatterns.append(path("", views.index, name="index"))

    for el in lst:
        _add_std_to_paths(urlpatterns, views, el)



def _add_std_to_paths(urlpatterns, views, data):    
    base = data
    options = 'CRU.'
    if isinstance(data, tuple):
        base = data[0]
        options = data[1]
    urlpatterns.append(path(base + "/", getattr(views, base + "_list"), name=base))
    if options[1] == 'R':
        urlpatterns.append(path(base + "/<int:obj_id>", getattr(views, base + "_detail"), name=base + "_detail"))
    if options[0] == 'C':
        urlpatterns.append(path(base + "/create", getattr(views, base + "_create"), name=base + "_create"))
        urlpatterns.append(path(base + "/created", getattr(views, base + "_created"), name=base + "_created"))
    if options[2] == 'U':
        urlpatterns.append(path(base + "/<int:obj_id>/edit", getattr(views, base + "_edit"), name=base + "_edit"))
        urlpatterns.append(path(base + "/<int:obj_id>/edited", getattr(views, base + "_edited"), name=base + "_edited"))
    if options[3] == 'D':
        urlpatterns.append(path(base + "/<int:obj_id>/delete", getattr(views, base + "_delete"), name=base + "_delete"))
    #print(urlpatterns)




# See below
def c_to_id(c):
    if c in [' ', '-', '_']:
        return '_'
    if c.isalnum():
        return c.lower()
    return ''
    
# Convert a string to another string suitable to use as an ID, i.e., containing only lowercase
# letters, numbers and underscores
def s_to_id(s):
    return ''.join(map(lambda c: c_to_id(c), s))
    
    
    
# Fills out the given field.
# It is assumed that the record has this field set from its meta-datum,
# and that text includes tags to be filled out. Tags are surrounded by
# dollar signs.
def fill_out_field(o, column, username = ''):
    s = getattr(o, column)
    if not s:
        s = ''

    if username:
        s = s.replace('$user$', username) 
    s = s.replace('$number$', o.batch_number())
    s = s.replace('$batch$', o.batch_number())

    md = re.match(r'\$(\w+)\$', s)
    while md:
        value = getattr(o, md[1].to_sym)
        if value:
            s.replace("$#{md[1]}$", str(value)) 
        md = re.match(r'\$(\w+)\$', s)

    if '$' in s:
        raise "Errant dollar in <" + s + ">" 
    setattr(o, column, s)




class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()





# Creates a PNG file as an HttpResponse
# Data should be a list of floats, size a tuple, and y_max a number
# Used for metals analyses
# I think you need PIL/Pillow installed 
def draw_graph(data, size, y_max):
    from PIL import Image, ImageDraw   

    # Define some useful values
    x_offset = 50                # x=0 is this number of pixels to the right
    x_gap = (size[0] - x_offset - 20) / (len(data) - 1)  # How many pixels along x-axis between points
    y_offset = size[1] - 20      # y=0 is this number of pixels down
    y_gap = (size[1] - 40) / 4   # Number of pixels between horizontal graph lines
    y_interval = y_max / 4            # For the scale on the y axis
    y_scale = (size[1] - 40) / y_max

    black = (0,0,0)
    blue = (0,0,128)
    green = (0,128,0)
    silver = (200, 200, 200)
    
    # Setting up
    # 0,0 is top left  
    image = Image.new('RGB', size) # create the image  
    draw = ImageDraw.Draw(image)   # create a drawing object that is used to draw on the new image  

    # Create the black graph
    rect = [(2, 2), (size[0]-2, size[1]-2)]
    draw.rectangle(rect, silver)
    for i in range(5):
        text_pos = (5, y_offset - y_gap * i - 4)
        text = str(i * y_interval)
        draw.text(text_pos, text, fill=black)  
        line = [(x_offset, y_offset - y_gap * i), (x_offset + size[0] - x_offset - 20, y_offset - y_gap * i)]
        draw.line(line, black)
    
    # Add the data
    last_point = None
    for i, val in enumerate(data):
        new_point = (x_offset + i * x_gap, y_offset - val * y_scale)
        #print(new_point, last_point)
        draw.circle(new_point, 2, blue)
        if last_point:
            draw.line([last_point, new_point], green)
        last_point = new_point
        
    # House keeping
    del draw
    response = HttpResponse()  
    response['Content-Type'] = 'image/png'
    image.save(response, 'PNG')  
    return response # and we're done!  