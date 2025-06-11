from django import forms

class SelectionForm(forms.Form):

    TIME_SPANS = [
        ("1 day", "1 day"),
        ("1 week", "1 week"),
        ("2 weeks", "2 weeks"),
        ("3 weeks", "3 weeks"),
        ("1 month", "1 month"),
        ("3 months", "3 months"),
        ("6 months", "6 months"),
        ("1 year", "1 year"),
    ]


    DEVICES = [
        ('meter19pd28saltcorridor', 'Meter 19 PD28 Salt Corridor'),
        ('meter17slaveharmonicsfilter', 'Meter 17 Slave Harmonics Filter'),
        ('meter36hwheatingcontrolpanel', 'Meter 36 HW Heating Control Panel'),
        ('meter18cell9', 'Meter 18 Cell 9'),
        ('meter35rectifiercell8', 'Meter 35 Rectifier Cell 8'),
        ('meter34dbpd7', 'Meter 34 DBPD 7'),
        ('meter33rectifiercell1', 'Meter 33 Rectifier Cell 1'),
        ('meter32dhfblockchiller', 'Meter 32 DHF Block Chiller'),
        ('meter31rectifiercell4', 'Meter 31 Rectifier Cell 4'),
        ('meter28pfcs_n460752_2', 'Meter 28 PFC S/N460752/2'),
        ('meter27rectifiercell7', 'Meter 27 Rectifier Cell 7'),
        ('meter10pd1packingdepartment', 'Meter 10 PD1 Packing Department'),
        ('meter26pfcunitdoorwall', 'Meter 26 PFC Unit Door Wall'),
        ('meter11rectifiercell6', 'Meter 11 Rectifier Cell 6'),
        ('meter2572kwoilheater_r05pure', 'Meter 2572 KW Oil Heater (r05 Pure)'),
        ('meter37pp30', 'Meter 37 PP 30'),
        ('meter24rectifiercell2', 'Meter 24 Rectifier Cell 2'),
        ('meter38pfcunit466752_1', 'Meter 38 PFC Unit 466752/1'),
        ('meter13harmonicsfilter', 'Meter 13 Harmonics Filter'),
        ('meter23rectifiercell3', 'Meter 23 Rectifier Cell 3'),
        ('meter39fluorinemcc', 'Meter 39 Fluorine MCC'),
        ('meter14carbwashchiller', 'Meter 14 Carb Wash Chiller'),
        ('meter22rectifiercell5', 'Meter 22 Rectifier Cell 5'),
        ('meter40flutecmezzfloor', 'Meter 40 Flute CMEZZ Floor'),
        ('meter15dbpd2_fluorine', 'Meter 15 DBPD2 (Fluorine)'),
        ('meter21db31_db32portacabin_offices', 'Meter 21 DB31/DB32 Port a Cabin Offices'),
        ('meter16pd13_flutec', 'Meter 16 PD13 (FluteC)'),
        ('meter20pd3_s', 'Meter 20 PD3 (S)'),
    ]


    INTERVALS = [
    ("10min", "Every 10 minutes"),
    ("1h", "Every 1 hour"),
    ("6h", "Every 6 hours"),
    ("1d", "Every 1 day"),
    ]


    time_span = forms.ChoiceField(choices=TIME_SPANS, label="Time Span")
    devices = forms.MultipleChoiceField(
        choices=DEVICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Devices"
    )
    difference = forms.BooleanField(required=False, label="Difference")
    interval = forms.ChoiceField(choices=INTERVALS, label="Interval")
    show_graph = forms.BooleanField(required=False, label="Show Graph")

