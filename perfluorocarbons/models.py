from django.db import models
from django.conf import settings
#from django.utils.html import strip_tags

from util.util import *


  # The density of air in g/l @ 20degC
# http://hypertextbook.com/facts/2000/RachelChu.shtml
DENSITY_OF_AIR = 1.2929






class Perfluorocarbon(models.Model):
    id = models.AutoField(primary_key=True)
    bp = models.FloatField(blank=True, null=True)
    conc = models.FloatField(blank=True, null=True)
    d = models.FloatField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    hvap = models.FloatField(blank=True, null=True)
    ltc = models.FloatField(blank=True, null=True)
    mp = models.FloatField(blank=True, null=True)
    ri = models.FloatField(blank=True, null=True)
    sheat = models.FloatField(blank=True, null=True)
    st = models.FloatField(blank=True, null=True)
    tcrit = models.FloatField(blank=True, null=True)
    tpress = models.FloatField(blank=True, null=True)
    v = models.FloatField(blank=True, null=True)
    vapvisc = models.FloatField(blank=True, null=True)
    vp = models.FloatField(blank=True, null=True)
    vd = models.FloatField(blank=True, null=True)
    vdensity = models.FloatField(blank=True, null=True)
    visc = models.FloatField(blank=True, null=True)
    c = models.IntegerField(blank=True, null=True)
    f = models.IntegerField(blank=True, null=True)
    un = models.IntegerField(blank=True, null=True)
    cas = models.CharField(max_length=255, blank=True, null=True)
    einecs = models.CharField(max_length=255, blank=True, null=True)
    trans = models.CharField(max_length=255, blank=True, null=True)
    uses = models.CharField(max_length=255, blank=True, null=True)
    mpcomment = models.CharField(max_length=255, blank=True, null=True)
    precip = models.CharField(max_length=255, blank=True, null=True)
    comp = models.CharField(max_length=255, blank=True, null=True)
    template = models.CharField(max_length=255, blank=True, null=True)
    pp_file = models.CharField(max_length=255, blank=True, null=True)
    pp_value = models.CharField(max_length=255, blank=True, null=True)
    pc_file = models.CharField(max_length=255, blank=True, null=True)
    pc_value = models.CharField(max_length=255, blank=True, null=True)
    name_file = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    tg_file = models.CharField(max_length=255, blank=True, null=True)
    tg_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    iupac = models.CharField(max_length=255, blank=True, null=True)
    reach = models.CharField(max_length=255, blank=True, null=True)
    reach_name = models.CharField(max_length=255, blank=True, null=True)
    vp50 = models.FloatField(blank=True, null=True)
    hp_file = models.CharField(max_length=255, blank=True, null=True)
    hp_value = models.CharField(max_length=255, blank=True, null=True)
    marine = models.CharField(max_length=255, blank=True, null=True)
    vdensity_s = models.CharField(max_length=255, blank=True, null=True)
    smiles = models.CharField(max_length=255, blank=True, null=True)
    cas_name = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    toxicity = models.CharField(max_length=255, blank=True, null=True)
    iuclid = models.CharField(max_length=255, blank=True, null=True)
    pc = models.FloatField(blank=True, null=True)
    analysis = models.TextField(blank=True, null=True)
    resist = models.CharField(max_length=255, blank=True, null=True)
    dielec = models.IntegerField(blank=True, null=True)
    sound = models.IntegerField(blank=True, null=True)
    tsca = models.IntegerField(blank=True, null=True)
    f_gas = models.BooleanField(blank=True, null=True)
    miti = models.IntegerField(blank=True, null=True)
    regulatory_notes = models.TextField(blank=True, null=True)
    inci = models.CharField(blank=True, null=True)
    stockcode = models.CharField(blank=True, null=True)
    customs_tariff_id = models.IntegerField(blank=True, null=True)
    discontinued = models.BooleanField(blank=True, null=True)
    inchi = models.CharField(blank=True, null=True)
    inchi_key = models.CharField(blank=True, null=True)
    uk_reach = models.CharField(blank=True, null=True)
    uk_reach_name = models.CharField(blank=True, null=True)

    URL_NAME = 'perfluorocarbon'
    
    FIELD_LIST = [
        { 'column':'name', 'heading':'Chemical Name', 'topic':'Identification', 'exclude':['pp', 'pc', 'tg', 'hp'], 'list_name':'Name' },
        { 'column':'pp_value', 'heading':'Electronic Grade', 'units':'&trade;', 'topic':'Identification', 'exclude':['cn', 'pc', 'tg', 'hp'], 'list_name':'PP name' },
        #{ 'column':'pc_value', 'heading':'Cosmetic Grade', 'units':'&trade;', 'topic':'Identification', 'exclude':['cn', 'pp', 'tg', 'hp'], 'list_name':'column' },
        { 'column':'tg_value', 'heading':'Tracer Grade', 'units':'&trade;', 'topic':'Identification', 'exclude':['cn', 'pp', 'pc', 'hp'], 'list_name':'Tracer name' },
        { 'column':'hp_value', 'heading':'High Purity Grade', 'units':'&trade;', 'topic':'Identification', 'exclude':['cn', 'pp', 'pc', 'tg'], 'list_name':'HP name' },
        { 'column':'formula', 'heading':'Formula', 'topic':'Identification', 'exclude':['pp', 'pc', 'tg', 'hp'] },
        { 'column':'mol_wt', 'heading':'Molecular Wt.', 'topic':'Identification', 'no_list':True },
        { 'column':'cas', 'heading':'CAS Number', 'topic':'Identification', 'list_name':'CAS RN' },
        { 'column':'cas_name', 'heading':'CAS Registry Name', 'topic':'Identification', 'exclude':['pp', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'iupac', 'heading':'IUPAC Name', 'topic':'Identification', 'exclude':['pp', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'smiles', 'heading':'SMILES', 'exclude':['pp', 'pc'], 'topic':'Identification', 'no_list':True },
        { 'column':'inchi', 'heading':'InChI', 'exclude':['pp', 'pc'], 'topic':'Identification', 'no_list':True },
        { 'column':'inchi_key', 'heading':'InChI key', 'exclude':['pp', 'pc'], 'topic':'Identification', 'no_list':True },
        { 'column':'discontinued', 'heading':'Discontinued', 'exclude':['cn', 'pp', 'pc', 'tg', 'hp'], 'no_list':True },

        { 'column':'einecs', 'heading':'EC Number', 'topic':'Regulatory' },
        { 'column':'inci', 'heading':'INCI name', 'topic':'Regulatory', 'exclude':['cn', 'pp', 'tg', 'hp'], 'no_list':True },
        { 'column':'reach', 'heading':'EU REACH Registration', 'topic':'Regulatory', 'no_list':True },
        { 'column':'reach_name', 'heading':'EU REACH Name', 'topic':'Regulatory', 'exclude':['pp', 'pc', 'tg'], 'no_list':True },
        { 'column':'uk_reach', 'heading':'UK REACH Registration', 'topic':'Regulatory', 'no_list':True },
        { 'column':'uk_reach_name', 'heading':'UK REACH Name', 'topic':'Regulatory', 'exclude':['pp', 'pc', 'tg'], 'no_list':True },
        { 'column':'tsca', 'heading':'TSCA ID', 'topic':'Regulatory', 'no_list':True },
        #{ 'column':'tsca_comment', 'heading':'TSCA Comment', 'topic':'Regulatory', 'exclude':['cn', 'pc', 'tg', 'hp', 'pp'] },
        #{ 'column':'f_gas_comment', 'heading':'Covered by F-Gas?', 'topic':'Regulatory', 'exclude':['cn', 'pc', 'tg', 'hp', 'pp'] },
        #{ 'column':'regulatory_notes', 'heading':'Regulatory notes', 'topic':'Regulatory' },
        { 'column':'un', 'heading':'UN Number', 'topic':'Regulatory', 'no_list':True },
        { 'column':'trans', 'heading':'Transport Name', 'topic':'Regulatory', 'no_list':True },
        { 'column':'marine', 'heading':'Transport Name for IMDG', 'topic':'Regulatory', 'no_list':True },

        { 'column':'bp', 'heading':'Boiling Point', 'units':'&deg;C', 'decimal_places':1, 'topic':'Liquid properties', 'no_list':True },
        { 'column':'mp', 'heading':'Melting Point', 'units':'&deg;C', 'decimal_places':1, 'topic':'Liquid properties', 'no_list':True },
        { 'column':'mpcomment', 'heading':'Note', 'topic':'Liquid properties', 'exclude':['cn', 'pp', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'precip', 'heading':'Note', 'topic':'Liquid properties', 'exclude':['cn', 'pp', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'pc', 'heading':'Partition Coefficient (log Kow)', 'units':' (calculated)', 'topic':'Liquid properties', 'exclude':['pp'], 'no_list':True },
        { 'column':'density', 'heading':'Density', 'units':' g/ml', 'decimal_places':3, 'topic':'Liquid properties', 'no_list':True },
        { 'column':'ri', 'heading':'Refractive Index', 'decimal_places':4, 'topic':'Liquid properties', 'exclude':['pp', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'sound', 'heading':'Speed of sound', 'units':' m/s', 'topic':'Liquid properties', 'exclude':['cn', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'visc', 'heading':'Viscosity', 'units':' mPa s', 'decimal_places':2, 'topic':'Liquid properties', 'no_list':True, 'no_list':True },
        { 'column':'k_visc', 'heading':'Kinematic Viscosity', 'units':' mm<sup>2</sup>/s', 'decimal_places':2, 'topic':'Liquid properties', 'no_list':True },
        { 'column':'st', 'heading':'Surface Tension', 'units':' mN/m', 'decimal_places':1, 'topic':'Liquid properties', 'no_list':True, 'no_list':True },

        { 'column':'hvap', 'heading':'Heat of Vaporisation', 'units':' kJ/kg @ bp', 'decimal_places':1, 'topic':'Thermal properties', 'exclude':['pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'ltc', 'heading':'Liquid Thermal Conductivity', 'units':' mW/m/K', 'decimal_places':1, 'topic':'Thermal properties', 'exclude':['cn', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'sheat', 'heading':'Specific Heat', 'units':' kJ/kg/K', 'decimal_places':2, 'topic':'Thermal properties', 'exclude':['pc', 'tg', 'hp'], 'no_list':True },

        { 'column':'tcrit', 'heading':'Critical Temperature', 'units':' K', 'decimal_places':1, 'exclude':['pc', 'tg', 'hp'], 'topic':'Critical properties', 'no_list':True },
        { 'column':'tcrit_c', 'heading':'Critical Temperature', 'units':'&deg;C', 'decimal_places':1 , 'exclude':['pc', 'tg', 'hp'], 'topic':'Critical properties', 'no_list':True },
        { 'column':'tpress', 'heading':'Critical Pressure', 'units':' bar', 'decimal_places':2 , 'exclude':['pc', 'tg', 'hp'], 'topic':'Critical properties', 'no_list':True },

        { 'column':'vp_kpa', 'heading':'Vapour Pressure', 'units':' kPa', 'decimal_places':1, 'topic':'Vapour properties', 'no_list':True },
        { 'column':'henry', 'heading':'Henry\'s law constant', 'units':' x10<sup>6</sup> Pa m<sup>3</sup>/mol', 'decimal_places':1, 'topic':'Vapour properties', 'no_list':True },
        { 'column':'vapvisc', 'heading':'Vapour Viscosity', 'units':' &mu;Pa s', 'decimal_places':1, 'topic':'Vapour properties', 'exclude':['pc', 'hp'], 'no_list':True },
        { 'column':'rel_vap_density', 'heading':'Relative Vapour Density', 'units':' (air=1)', 'decimal_places':1, 'topic':'Vapour properties', 'exclude':['pp', 'pc', 'hp'], 'no_list':True },

        { 'column':'dielec', 'heading':'Dielectric strength', 'units':' kV', 'topic':'Electrical properties', 'exclude':['cn', 'pc', 'tg', 'hp'], 'no_list':True },
        { 'column':'resist', 'heading':'Resistivity', 'units':' &ohm; cm', 'topic':'Electrical properties', 'exclude':['cn', 'pc', 'tg', 'hp'], 'no_list':True },
    ]

    class Meta:
        managed = True
        db_table = 'perfluorocarbons'

        
    @property
    def is_cyclic(self):
        return (self.f < (self.c * 2 + 2))
        
    @property
    def is_gas(self):
        return (self.bp < 10)
        
    @property
    def formula(self):
        return f"C<sub>{self.c}</sub>F<sub>{self.f}</sub>" if self.c > 1 else f"CF<sub>{self.f}</sub>"
        
    @property
    def formula_plain(self):
        return f"C{self.c}F#{self.f}" if self.c > 1 else f"CF{self.f}"
        
    @property
    def mol_wt(self):
        return 12 * self.c + 19 * self.f
        
    @property
    def k_visc(self):
        return round(self.visc / self.density, -2) if  self.visc and self.density else None
        
    @property
    def vp_kpa(self):
        return round(self.vp * 0.1, -2) if  self.vp else None
        
    @property
    def vp_kpa50(self):
        return round(self.vp50 * 0.1, -2) if  self.vp50 else None
        
    @property
    def water_sol(self):
        return 0.01 / self.mol_wt   # in mol/m^3
        
    # Henry's law constant in mg/l/kPa... or in x10^6 Pa m^3/mol???
    # Assumes water solubility is 0.01 mg/l, which is pretty much a guess, and likely going to change across the range
    @property
    def henry(self):
        return round(self.vp_kpa / self.water_sol /1000, -2) if self.vp else None  

    # Critical temperature in degC
    @property
    def tcrit_c(self):
        return round(self.tcrit - 273.15, 1) if self.tcrit else ''

    # Vapour density relative to air
    @property
    def vap_density(self):
        if self.vdensity_s:
            return self.vdensity_s
        return round(self.vdensity, 3) if self.vdensity else None

    # Vapour density relative to air
    @property
    def rel_vap_density(self):
        if self.vdensity:
            return round(self.vdensity / DENSITY_OF_AIR * 1000, 2)
        return None

    """    
      # The name for the grade specified by "type", with TM as for RTF
      #def name_rtf type
      #  name type, "\\loch\\af1\\dbch\\af13\\hich\\f1 \\\'99"
      #end

      NAME_MAPPINGS = {
        "Cosmetic Grade" => "pc",
        "Electronic Grade" => "pp",
        "Tracer Grade" => "tg",
        "Chemical Name" => "name",
        "High Purity Grade" => "hp",
      }

      # The name for the grade specified by "type", with TM as given
      # Unit tested.
    self.grade_name type, tm = ''
        s = send "#{NAME_MAPPINGS[type]}_value".to_sym
        "#{s}#{type == "Chemical Name" ? '' : tm}"

      # The filename for the grade specified by "type"
      # Unit tested.
    self.file type
        send "#{NAME_MAPPINGS[type]}_file".to_sym

      # The name of the solvent (or None if n/a)
      # Unit tested.
    self.solvent
        return None if template == 'liquid template' || template == 'gas template'
        Perfluorocarbon.cas(cas)[0].name
    """

    # The name for shipping (marine if found, trans otherwise
    # Unit tested
    @property
    def imdg(self):
        return self.marine or self.trans

    # Guesses the name of the GIF
    @property
    def image2d(self):
        return "/images/2d/{self.name}.gif"

    # Guesses the name of the JPG
    @property
    def image3d(self):
        return "/images/3d/{self.name}.jpg"



        

    def list_products(type):
        if type == 'PP':
            lst = Perfluorocarbon.objects.exclude(pp_value__isnull=True).order_by('bp')
            return [x.pp_value for x in lst]
            
        if type == 'PC':
            lst = Perfluorocarbon.objects.exclude(pc_value__isnull=True).order_by('bp')
            return [x.pc_value for x in lst]
            
        if type == 'HC':
            lst = Perfluorocarbon.objects.exclude(hc_value__isnull=True).order_by('bp')
            return [x.hc_value for x in lst]
            
        if type == 'TG':
            lst = Perfluorocarbon.objects.exclude(tg_value__isnull=True).order_by('bp')
            return [x.tg_value for x in lst]
            
        if type == 'CN':
            lst = Perfluorocarbon.objects.exclude(stockcode__isnull=True).order_by('bp')
            return [x.name for x in lst]
            
        