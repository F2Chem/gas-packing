from django.db import models
from django.conf import settings
from django.utils.html import strip_tags

from util.util import *




class StaticIpAddress(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    identity = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.IntegerField(blank=True, null=True)

    URL_NAME = 'static'
    FIELD_LIST = [
        {"heading": "Name", "column": "identity"},
        {"heading": "Network", "column": "name"},
        {"heading": "Address", "func": lambda o: '10.0.0.' + str(o.address), 'no_edit':True},
        {"heading": "Address: 10.0.0.", "column": "address", 'edit_only':True},
        {"heading": "Link", "ex_link_func": lambda o: 'http://10.0.0.' + str(o.address), 'no_edit':True},
    ]

    class Meta:
        managed = True
        db_table = 'computer_log_static_ip_addresses'
        ordering = ('address', 'id')
        verbose_name = 'Static IP address'
        verbose_name_plural = 'Static IP addresses'



class Device(TimeStampMixin):
    DEVICE_TYPE_LIST = ['Printer', 'Network switch', 'Wifi hub', 'USB stick', 'UPS', 'Other']

    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.IntegerField()
    #number = models.IntegerField()

    original_owner = models.CharField(max_length=16, blank=True, null=True)
    owner = models.CharField(max_length=16, blank=True, null=True)
    in_use = models.BooleanField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    wifi_name = models.CharField(max_length=50, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    URL_NAME = 'device'
    FIELD_LIST = [
        {"heading": "Model", "column": "model"},
        {"heading": "Serial no", "column": "serial_number"},
        {"heading": "Type", "column": "device_type", "options":DEVICE_TYPE_LIST},
        {"heading": "Location", "column": "location",},
        {"heading": "Wi-fi name", "column": "wifi_name",},
        {"heading": "In use", "column": "in_use"},
        {"heading": "Notes", "column": "notes", "no_list":True},
    ]

    class Meta:
        managed = True
        db_table = 'devices'
        ordering = ('device_type', 'id')
        
     

  



class Computer(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField(blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    monitor_serial_number = models.CharField(max_length=255, blank=True, null=True)
    pc = models.IntegerField(blank=True, null=True)
    monitor = models.IntegerField(blank=True, null=True)
    original_owner = models.CharField(max_length=255, blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)
    in_use = models.BooleanField(blank=True, null=True)
    processor = models.IntegerField(blank=True, null=True)
    ram = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    network_name = models.CharField(max_length=255, blank=True, null=True)
    operating_system = models.IntegerField(blank=True, null=True)
    sp = models.CharField(max_length=255, blank=True, null=True)
    product_key = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    browser = models.CharField(max_length=255, blank=True, null=True)
    location = models.IntegerField(blank=True, null=True)
    office_version = models.IntegerField(blank=True, null=True)
    office_key = models.CharField(max_length=255, blank=True, null=True)
    second_office_key = models.CharField(blank=True, null=True)

    LOCATION_LIST = ["Finance", "Commercial", "CEO", "GMP", "Labs", "Plant", "ModuleOffices", "Spare", "Other"]

    OFFICE_VERSION_LIST = [
        'Not installed',
        'Standard Edition 97 Upgrade',
        'Standard Edition 2000',
        'Basic Edition 2003',
        'Standard Edition 2003',
        'Small Business Edition 2003', #  5
        'Small Business Edition 2003 OEM',
        'Small Business Edition 2007',
        'Standard Edition 2007',
        'Home and Business 2010',
        'Home and Business 2013',      # 10
        'Home and Business 2016',
        'Home and Business 2019',
        '365',
        'Home and Business 2021',
    ]

    # Known operating systems
    OS_LIST = ["Unknown", "Apple", "Unix", "Win3.1", "Win3.11", "WinNT4", "Win95", "Win98", "Win98SE", "Win2000", "WinME", "WinXPHome", "WinXPPro", "WinServer2003", "WinVistaHome", "WinVistaBus", "Win7Home", "Win7Pro", "Win7Pro64bit", "WinServer2011", "Win8Home", "Win8Pro", "Win8Home64bit", "Win8Pro64bit", "Win10Pro64Bit", "Win11Pro64Bit"]

    URL_NAME = 'computer'
    FIELD_LIST = [
        {"heading": "#", "column": "number", "read_only": True},
        {"heading": "Model", "column": "model"},
        {"heading": "Original owner", "column": "original_owner"},
        {"heading": "Owner", "column": "owner"},
        {"heading": "Location", "column": "location", "options":LOCATION_LIST},
        {"heading": "In use", "column": "in_use"},
        #{"heading": "Processor", "column": "processor"},
        #{"heading": "RAM", "column": "ram"},
        {"heading": "Network name", "column": "network_name"},
        {"heading": "Operating system", "column": "operating_system", "options":OS_LIST},
        {"heading": "Office", "column": "office_version", "options":OFFICE_VERSION_LIST},
        {"heading": "Comments", "column": "notes"},
    ]

    class Meta:
        managed = True
        db_table = 'computers'
        

    def greyed_out(self):
        return not self.in_use




    
    
    
class CyberTarget(TimeStampMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_type = models.IntegerField()

    TARGET_TYPES = [
        {'name':"n/w device", 'desc':"A network switch, router or firewall"},
        {'name':"headless", 'desc':"A computer that has no monitor, keyboard or mouse attached"},
        {'name':"computer", 'desc':"A normal computer that is on the corporate LAN"},
        {'name':"off-site", 'desc':"A computer that is off-site"},
        {'name':"device", 'desc':"Something on the corporate LAN and not in another category"},
        {'name':"isolated", 'desc':"A device at F2 not connectedto the internet in any way"},
        {'name':"website", 'desc':"The F2 website"},
        {'name':"email", 'desc':"Cloud email system"},
    ]

    URL_NAME = 'target'
    FIELD_LIST = [
        {"heading": "Name", "column": "name"},
        {"heading": "Type", "column": "target_type", "options_from_array":TARGET_TYPES},
        {"heading": "Description", "column": "description"},
    ]


    def __str__(self):
        return self.name


    # Used in views when a new target is created to generate the associated assessments
    def generate_cras(self):
        for j in range(len(CyberRiskAssessment.ATTACK_VECTORS)):
            s = CyberRiskAssessment.ATTACK_VECTORS[j].split(':')[0]
            cra = CyberRiskAssessment(target_id=self.id, attack_vector=j, status=0)
            cra.name = s + ': ' + self.name
            cra.save()







class CyberRiskAssessment(TimeStampMixin):
    MAX_ACCEPTABLE_BUT = 7
    MAX_ACCEPTABLE = 6
    
    ATTACK_VECTORS = [
        # Unauthorised physical / logical access to corporate assets by unauthorised employee:
        "TS1: F2 employee physically accessing a target device he or she is not authorised to use – could be malicious or well-meaning",

        # Unauthorised physical / logical access to corporate assets by authorised employee:
        "TS2: F2 employee physically accessing a target device he or she is authorised to use, but doing something he or she should not – could be malicious or well-meaning",
        
        # Unauthorised physical / logical access to corporate assets by authorised third party, e.g. vendor, integrator etc.: 
        "TS3: Third party logically accessing the device to do something they should not – could be malicious or well-meaning",
        
        # Unauthorised physical / logical access to corporate assets by external party: 
        "TS4(p): Malicious outsider physically accessing a target device",
        
        # Unauthorised physical / logical access to corporate assets by external party.
        "TS4(l): Malicious outside logically accessing a target device",
        
        # Equipment Loss, theft etc.: 
        "TS10: Device is not usable due to destruction or loss; could be malicious, act of nature, etc.",
    ]

    CONSEQUENCES = [
        {
            'code':'None:',
            'description':'Not set',
            'severity':'Not set',
        },
        {
            'code':'CQ1:',
            'description':'Minor disruption',
            'severity':'Minimal significance (eg employee loss of IT access >24 hr)',
        },
        {
            'code':'CQ2',
            'description':'Some disruption / inconvenience but largely unaffected; Legal actio below £1,000',
            'severity':'Minor significance (eg company-wide loss of IT access >24 hr)',
        },
        {
            'code':'CQ3',
            'description':'Significant disruption / inconvenience but activities continue; Legal action £1,000 to £5,000; Some damage, remedial actions required costing up to £5,000',
            'severity':'Medium significance (eg data breach)',
        },
        {
            'code':'CQ4',
            'description':'Activities suspended;Loss of critical assets but replaceable;Significant loss of intellectual property;Loss of strategic customer / business details;Loss of personal information;Legal action £5,000 to £10,000;Damage or remedial actions required costing over £5,000 up to £10,000;Negative consequences for reputation, significant loss of business',
            'severity':'High significance (eg illegal access to DCS)',
        },
        {
            'code':'CQ5',
            'description':'Major Accident; Loss of critical assets and not replaceable (or difficult to replace); Legal action over £10,000; Damage or remedial actions required costing over £10,000',
            'severity':'Very High significance',
        },
    ]

    LIKELIHOOD = [
        {
            'code':'None:',
            'description':'Not set',
            'frequency':'Not set',
        },
        {
            'code':'LH1',
            'description':'Extremely Low',
            'frequency':'Less than once every 50 years',
        },
        {
            'code':'LH2',
            'description':'Very Low',
            'frequency':'Between once every 20 years and once every 50 years',
        },
        {
            'code':'LH3',
            'description':'Quite Low',
            'frequency':'Between once every 5 years and once every 20 years',
        },
        {
            'code':'LH4',
            'description':'Low',
            'frequency':'Between once a year and once every 5 years',
        },
        {
            'code':'LH5',
            'description':'Medium',
            'frequency':'Once a year',
        },
        {
            'code':'LH6',
            'description':'High',
            'frequency':'Up to 5 times a year',
        },
        {
            'code':'LH7',
            'description':'Very High',
            'frequency':'More than 5 times a year',
        },
    ]
    
    VULNERABILITIES = [
        "VL1: Software bugs",
        "VL2: Hardware failures",
        "VL3: Cybersecurity countermeasure degradation",
        "VL4: Credential reuse",
        "VL5: Confidential information release",
        "VL6: Systematic errors leading to misconfiguration",
        "VL7: Lack of training and awareness",
        "VL8: General Viruses",
        "VL9: Unintentional Deactivation of a Cybersecurity Countermeasure",
        "VL10: Disgruntled employee/contractor",
        "VL11: Deficient portable media controls",
        "VL12: Designed security bombs",
        "VL13: Deficient access control",
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    target_id = models.IntegerField()
    attack_vector = models.IntegerField()
    scenario = models.TextField(blank=True, null=True)
    safeguards = models.TextField(blank=True, null=True)
    outcome = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    actions = models.TextField(blank=True, null=True)
    likelihood = models.IntegerField(blank=True, null=True)
    consequences = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    not_relevant = models.BooleanField(blank=True, null=True)

    malware_in_network = models.BooleanField(blank=True, null=True)
    scan_traffic = models.BooleanField(blank=True, null=True)
    data_breach = models.BooleanField(blank=True, null=True)
    network_disruption = models.BooleanField(blank=True, null=True)
    internet_disruption = models.BooleanField(blank=True, null=True)
    access_to_control = models.BooleanField(blank=True, null=True)
    ransomware = models.BooleanField(blank=True, null=True)

    URL_NAME = 'cra'
    FIELD_LIST = [
        {"heading": "Name", "column": "name", 'size':2},
        {"heading": "Target", "column": "target_id", "options_from_table":'computers.models.CyberTarget', 'read_only':True, 'no_list':True},
        {"heading": "Attack vector", "column": "attack_vector", "options":ATTACK_VECTORS, 'read_only':True, 'size':2},
        {"heading": "Likelihood", "column": "likelihood", "options_from_array":LIKELIHOOD, 'attribute':'frequency'},
        {"heading": "Consequences", "column": "consequences", "options_from_array":CONSEQUENCES, 'attribute':'severity'},
        {"heading": "Risk", "func": lambda o: o.risk_as_html(), "no_edit":True},
        {"heading": "Not relevant?", "column": "not_relevant", 'no_list':True},
        {"heading": "Scenario", "column": "scenario", "explanation":"describe a reasonable scenario that could happen at F2"},
        {"heading": "Safeguards", "column": "safeguards", "explanation":"what is in place to prevent or mitigate"},
        
        {'flag':True, 'edit_only':True, "heading": "Could result in data breach (access to files)?", "column": "data_breach"},
        {'flag':True, 'edit_only':True, "heading": "Could result in traffic being scanned?", "column": "scan_traffic"},
        {'flag':True, 'edit_only':True, "heading": "Could result in disruption to network?", "column": "network_disruption"},
        {'flag':True, 'edit_only':True, "heading": "Could result in disruption to internet connect?", "column": "internet_disruption"},
        {'flag':True, 'edit_only':True, "heading": "Could result in malware in network?", "column": "malware_in_network"},
        {'flag':True, 'edit_only':True, "heading": "Could result in ransomware attack?", "column": "ransomware"},
        {'flag':True, 'edit_only':True, "heading": "Could result in access to control n/w?", "column": "access_to_control"},
        { 'edit_only':True,"heading": "Other potential outcomes", "column": "outcome", "explanation":"describe how the worst case scenario will impact the company beyond those ticked above"},
        {"heading": "Potential outcomes", "func":lambda o: o.outcome_all(), 'no_edit':True, 'size':4},
        
        {"heading": "Notes", "column": "notes", "explanation":"explain why it is not relevant, etc.", 'size':3},
        {"heading": "Actions", "column": "actions", 'size':3},
    ]

    class Meta:
        ordering = ('target_id', 'attack_vector', 'id')



    """
    # methods used to create newentries, but unlikely to ever be needed again,
    
    def generate():
        CyberRiskAssessment.objects.all().delete()
        CyberTarget.objects.all().delete()
        for i in range(len(CyberRiskAssessment.TARGETS)):
            target = CyberTarget(name=CyberRiskAssessment.TARGETS[i])
            target.save()
            for j in range(len(CyberRiskAssessment.ATTACK_VECTORS)):
                s = CyberRiskAssessment.ATTACK_VECTORS[j].split(':')[0]
                cra = CyberRiskAssessment(target_id=target.id, attack_vector=j, status=0)
                cra.name = s + ': ' + CyberRiskAssessment.TARGETS[i]
                cra.save()
        print(CyberRiskAssessment.objects.all().count())
        
    def interpolate():
        ras = CyberRiskAssessment.objects.all()
        last = None
        for ra in ras:
            print('===============')
            print(ra.name)
            print(ra.target().name)
            if ra.likelihood or ra.not_relevant:
                print('good!')
                continue
            else:
                last = CyberRiskAssessment.find_completed(ra)
                if last:
                    ra.scenario = last.scenario
                    ra.outcome = last.outcome
                    ra.notes = last.notes
                    ra.actions = last.actions
                    ra.safeguards = last.safeguards
                    ra.save()
                else:
                    print('Failed to find match for:', ra)

    def find_completed(self):
        # need to find ra with same attack_vector, same type of target
        
        target_target_type = self.target().target_type
        
        # get all with same AV
        ras = CyberRiskAssessment.objects.filter(attack_vector=self.attack_vector)
        # and go through them
        for ra in ras:
            # ignore if it is this one
            if ra.target_id == self.target_id:
                continue
            # does it have the same target type?
            if ra.target().target_type == target_target_type:
                if ra.likelihood or ra.not_relevant:
                    return ra
        return None
    """
    

    def __str__(self):
        return self.name + ' (' + self.risk_as_str() + ')'

    # There are a bunch of general loutcomes in the field list, identified by "flag" being true. These are in addition to the "outcome" field.
    # This functon combines them all into one text summary for this record; any of the generic ones that are set to True in the database are listed
    # plus the contents of the outcome itself.
    # Unit tested
    def outcome_all(self):
        s = ''
        for el in CyberRiskAssessment.FIELD_LIST:
            if 'flag' in el:
                if getattr(self, el['column']):
                    s += el['heading'][:-1]
                    s += '. '
        if self.outcome:
            s += self.outcome
        return s
    
    # Gets the next one
    # Unit tested
    def next(self):
        lst = CyberRiskAssessment.objects.all()
        index, el = search(lst, lambda x: x.id == self.id)
        index += 1
        if index >= len(lst):
            return None
        return lst[index]
        
    def target(self):
        return CyberTarget.objects.get(id=self.target_id)
        
        
    # This is used to generate the risk matrix, so is broken out of risk_as_html
    # These three methods are all unit tested in test_risk_as_html
    def risk_as_html_generic(likelihood, consequences):
        if not likelihood or not consequences:
            return '<span style="background-color:black; color:white; padding:2px">Not determined</span>'
        if likelihood + consequences > CyberRiskAssessment.MAX_ACCEPTABLE_BUT:
            return '<span style="background-color:#b00; color:white; padding:2px">Unacceptable</span>'
        if likelihood + consequences > CyberRiskAssessment.MAX_ACCEPTABLE:
            return '<span style="background-color:yellow; color:black; padding:2px">Acceptable, but...</span>'
        return '<span style="background-color:#32CD32; color:white; padding:2px">Acceptable</span>'
        
    def risk_as_html(self):
        if self.not_relevant:
            return '<span style="background-color:silver; color:grey; padding:2px">Not relevant</span>'
        return CyberRiskAssessment.risk_as_html_generic(self.likelihood, self.consequences)
        
    def risk_as_str(self):
        return strip_tags(self.risk_as_html()).lower()
        

    # unit tested
    def clone(self):
        cra = CyberRiskAssessment()
        cra.name = self.name + ' (additional)'
        cra.target_id = self.target_id
        cra.attack_vector = self.attack_vector
        cra.scenario = self.scenario
        cra.safeguards = self.safeguards
        cra.outcome = self.outcome
        cra.notes = self.notes
        return cra
        
        
        

