from ..models import *
from util.util4units import *






class ZoneViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(Zone)
        self.row = Zone(name='EU')
        self.row.save()
        self.base_url = '/sales/zone/'
        self.test_data = {
            'name':'US',
        }
        self.ignore('edit')
        self.ignore('create')



class CustomerViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(Customer)
        zone = Zone(name='EU')
        zone.save()
        zone2 = Zone(name='US')
        zone2.save()
        self.row = Customer(name='GetFromWarehouse', zone=zone)
        self.row.save()
        self.base_url = '/sales/customer/'
        self.test_data = {
            'name':'TakeToPlant',
            'zone_id':zone2.name,
        }

