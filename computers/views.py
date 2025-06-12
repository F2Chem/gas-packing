from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from django.contrib.auth.decorators import permission_required

from .models import *
from util.pdf_util import *
#from .secret import *







def index(request):
    return redirect('/computers/computer/')




def static_list(request):
    lst = StaticIpAddress.objects.all()
    context = {
        "lst": lst,
        "obj":StaticIpAddress,
        "meta_data":StaticIpAddress.FIELD_LIST,
        'links':{'klass':StaticIpAddress, 'lst':['Create']},
        'row_links':['Show', 'Edit'],
        'title': 'Listing Static IP Addresses (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_list.html", context)
    

def static_detail(request, obj_id):
    obj = get_object_or_404(StaticIpAddress, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":StaticIpAddress.FIELD_LIST,
        'links':{'klass':StaticIpAddress, 'obj':obj, 'lst':['List', 'Edit']},
        'title': 'Static IP Address',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_detail.html", context)

@permission_required("computers.add_staticipaddress")
def static_create(request):
    obj = StaticIpAddress()
    obj.in_use = True
    obj.operating_system = len(Computer.OS_LIST) - 1
    context = {
        "obj": obj,
        "meta_data":StaticIpAddress.FIELD_LIST,
        'links':{'klass':StaticIpAddress, 'obj':obj, 'lst':['List']},
        'title': 'Creating New Static IP Address',
        'destination':'static_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)

@permission_required("computers.add_staticipaddress")
def static_created(request):
    obj = StaticIpAddress()
    update(request, obj, StaticIpAddress.FIELD_LIST)
    return redirect('/computers/static/' + str(obj.id))


@permission_required("computers.change_staticipaddress")
def static_edit(request, obj_id):
    obj = get_object_or_404(StaticIpAddress, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":StaticIpAddress.FIELD_LIST,
        'links':{'klass':StaticIpAddress, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Static IP Address',
        'destination':'static_edited',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_edit.html", context)

@permission_required("computers.change_staticipaddress")
def static_edited(request, obj_id):
    obj = get_object_or_404(StaticIpAddress, pk=obj_id)
    update(request, obj, StaticIpAddress.FIELD_LIST)
    return redirect('/computers/static/' + str(obj.id))





    






def device_list(request):
    lst = Device.objects.filter(in_use=True)
    context = {
        "lst": lst,
        "obj":Device,
        "meta_data":Device.FIELD_LIST,
        'links':{'klass':Device, 'lst':['Create']},
        'row_links':['Show', 'Edit'],
        'title': 'Listing devices in use(' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_list.html", context)
    
def device_list_all(request):
    lst = Device.objects.all().order_by('id')
    context = {
        "lst": lst,
        "meta_data":Device.FIELD_LIST,
        'options':['show', 'edit'],
        'title': 'Listing all devices (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_list.html", context)
    
    
def device_detail(request, obj_id):
    obj = get_object_or_404(Device, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Device.FIELD_LIST,
        'links':{'klass':Device, 'obj':obj, 'lst':['List', 'Edit']},
        'title': 'device',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_detail.html", context)


@permission_required("computers.add_device")
def device_create(request):
    obj = Device()
    context = {
        "obj": obj,
        "meta_data":Device.FIELD_LIST,
        'title': 'Creating New device',
        'destination':'device_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)


@permission_required("computers.add_device")
def device_created(request):
    obj = Device()
    update(request, obj, Device.FIELD_LIST)
    return redirect('/computers/device/' + str(obj.id))


@permission_required("computers.change_device")
def device_edit(request, obj_id):
    obj = get_object_or_404(Device, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Device.FIELD_LIST,
        'links':{'klass':Device, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'device',
        'destination':'device_edited',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_edit.html", context)

@permission_required("computers.change_device")
def device_edited(request, obj_id):
    obj = get_object_or_404(Device, pk=obj_id)
    update(request, obj, Device.FIELD_LIST)
    return redirect('/computers/device/' + str(obj.id))




    
    
def computer_list(request):
    lst = Computer.objects.filter(in_use=True).order_by('id')
    context = {
        "lst": lst,
        "obj":Computer,
        "meta_data":Computer.FIELD_LIST,
        'row_links':['Show', 'Edit'],
        'links':{'klass':Computer, 'lst':['Create']},
        'title': 'Listing Computers In Use (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
        }
    return render(request, "obj_list.html", context)


def computer_list_all(request):
    lst = Computer.objects.all().order_by('id')
    context = {
        "lst": lst,
        "meta_data":Computer.FIELD_LIST,
        'options':['show', 'edit'],
        'title': 'Listing All Computers (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_list.html", context)
    
    
def computer_detail(request, obj_id):
    obj = get_object_or_404(Computer, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Computer.FIELD_LIST,
        'links':{'klass':Computer, 'obj':obj, 'lst':['List', 'Edit']},
        'title': 'Showing Computer ' + str(obj.id),
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_detail.html", context)


@permission_required("computers.add_computer")
def computer_create(request):
    obj = Computer()
    mx = Computer.objects.all().aggregate(Max('number'))
    obj.number = 1 if not mx['number__max'] else mx['number__max'] + 1
    obj.in_use = True
    context = {
        "obj": obj,
        "meta_data":Computer.FIELD_LIST,
        'title': 'Creating New Computer',
        'destination':'computer_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)


@permission_required("computers.add_computer")
def computer_created(request):
    obj = Computer()
    update(request, obj, Computer.FIELD_LIST)
    return redirect('/computers/computer/' + str(obj.id))


@permission_required("computers.change_computer")
def computer_edit(request, obj_id):
    obj = get_object_or_404(Computer, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":Computer.FIELD_LIST,
        'links':{'klass':Computer, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Editing Computer ' + str(obj.id),
        'destination':'computer_edited',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_edit.html", context)


@permission_required("computers.change_computer")
def computer_edited(request, obj_id):
    obj = get_object_or_404(Computer, pk=obj_id)
    update(request, obj, Computer.FIELD_LIST)
    return redirect('/computers/computer/' + str(obj.id))




# Not tested, under development!!!
def pdf_test(request):
    data = {
        'title':'Cyber Security Risk Assessments',
    
    
    }
    return create_pdf(data)




def cyber_notes(request):
    context = {
        'attack_vectors':CyberRiskAssessment.ATTACK_VECTORS,
        'title':'Cyber Risk Explained',
        'subsections':'computers/subsections.html',
    }
    return render(request, "computers/cyber_notes.html", context)



def target_list(request):
    lst = CyberTarget.objects.order_by('id')
    context = {
        "lst": lst,
        "obj":CyberTarget,
        "meta_data":CyberTarget.FIELD_LIST,
        'row_links':['Show'],
        'links':{'klass':CyberTarget, 'lst':['Create']},
        'title': 'Listing Cyber Targets (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_list.html", context)


    
    
def target_detail(request, obj_id):
    obj = get_object_or_404(CyberTarget, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":CyberTarget.FIELD_LIST,
        'links':{'klass':CyberTarget, 'obj':obj, 'lst':['List', 'Edit']},
        'title': 'Showing CyberTarget ' + str(obj.id),
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_detail.html", context)

@permission_required("computers.add_cybertarget")
def target_create(request):
    obj = CyberTarget()
    context = {
        "obj": obj,
        "meta_data":CyberTarget.FIELD_LIST,
        'title': 'Creating New CyberTarget',
        'destination':'target_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)


@permission_required("computers.add_cybertarget")
def target_created(request):
    obj = CyberTarget()
    update(request, obj, CyberTarget.FIELD_LIST)
    obj.generate_cras()
    return redirect('/computers/target/' + str(obj.id))


@permission_required("computers.change_cybertarget")
def target_edit(request, obj_id):
    obj = get_object_or_404(CyberTarget, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":CyberTarget.FIELD_LIST,
        'links':{'klass':CyberTarget, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Editing CyberTarget ' + str(obj.id),
        'destination':'target_edited',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_edit.html", context)


@permission_required("computers.change_cybertarget")
def target_edited(request, obj_id):
    obj = get_object_or_404(CyberTarget, pk=obj_id)
    update(request, obj, CyberTarget.FIELD_LIST)
    return redirect('/computers/target/' + str(obj.id))






    
    
    
def cra_list(request):
    lst = CyberRiskAssessment.objects.all()
    context = {
        "lst": lst,
        "obj":CyberRiskAssessment,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'row_links':['Show', 'Edit'],
        'links':{'klass':CyberRiskAssessment, 'lst':['Create', 'PDF']},
        'title': 'Listing Cybersecurity Risk Assessments (' + str(len(lst)) + ')',
        'subsections':'computers/subsections.html',
        }
    return render(request, "obj_list.html", context)


# Not tested, under development!!!
def cra_pdf(request):
    lst = CyberRiskAssessment.objects.all()
    context = {
        "lst": lst,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'title': 'Listing Cybersecurity Risk Assessments (' + str(len(lst)) + ')',
        }
    return render_pdf_list(context)


    
    
def cra_detail(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'links':{'klass':CyberRiskAssessment, 'obj':obj, 'lst':['List', 'Edit', 'Clone', 'Next', 'Edit next']},
        'title': 'Showing CyberRiskAssessment ' + str(obj.id),
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_detail.html", context)


@permission_required("computers.add_cyberriskassessment")
def cra_create(request):
    obj = CyberRiskAssessment()
    context = {
        "obj": obj,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'title': 'Creating New CyberRiskAssessment',
        'destination':'cra_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)


@permission_required("computers.add_cyberriskassessment")
def cra_created(request):
    obj = CyberRiskAssessment()
    update(request, obj, CyberRiskAssessment.FIELD_LIST)
    return redirect('/computers/cra/' + str(obj.id))


@permission_required("computers.change_cyberriskassessment")
def cra_edit(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    context = {
        "obj": obj,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'links':{'klass':CyberRiskAssessment, 'obj':obj, 'lst':['List', 'Detail']},
        'title': 'Editing CyberRiskAssessment ' + str(obj.id),
        'destination':'cra_edited',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_edit.html", context)


@permission_required("computers.change_cyberriskassessment")
def cra_edited(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    update(request, obj, CyberRiskAssessment.FIELD_LIST)
    return redirect('/computers/cra/' + str(obj.id))






@permission_required("computers.add_cyberriskassessment")
def cra_clone(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    new_obj = obj.clone()
    
    context = {
        "obj": new_obj,
        "meta_data":CyberRiskAssessment.FIELD_LIST,
        'title': 'Creating New CyberRiskAssessment From existing CyberRiskAssessment ' + str(obj.id),
        'destination':'cra_created',
        'subsections':'computers/subsections.html',
    }
    return render(request, "obj_create.html", context)
    

def cra_next(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    obj2 = obj.next()
    if obj2:
        return redirect('/computers/cra/' + str(obj2.id))
    else:
        return redirect('/computers/cra/')

def cra_edit_next(request, obj_id):
    obj = get_object_or_404(CyberRiskAssessment, pk=obj_id)
    obj2 = obj.next()
    if obj2:
        return redirect('/computers/cra/' + str(obj2.id) + '/edit')
    else:
        return redirect('/computers/cra/')

"""
@permission_required("computers.add_cyberriskassessment")
def cra_interpolate(request):
    CyberRiskAssessment.interpolate()

    return redirect('/computers/cra/')
"""






