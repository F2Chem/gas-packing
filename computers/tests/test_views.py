from computers.models import *
from util.util4units import *






class StaticIpAddressViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(StaticIpAddress)
        self.row = StaticIpAddress(identity='Server', address=3)
        self.row.save()
        self.base_url = '/computers/static/'
        self.test_data = {
            'identity':'Backup Server',
            'address':4,
        }



class DeviceViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(Device)
        self.row = Device(model='USB stick', device_type=3)
        self.row.save()
        self.base_url = '/computers/device/'
        self.test_data = {
            'model':'Netgear switch',
            'device_type':'Network switch',
        }



class ComputerViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(Computer)
        self.row = Computer(owner='Test', number=3)
        self.row.save()
        self.base_url = '/computers/computer/'
        self.test_data = {
            'model':'HP laptop',
            'owner':'Test',
            'number':3,
        }


class CyberTargetViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(CyberTarget)
        self.row = CyberTarget(name='Server', target_type=1)
        self.row.save()
        self.base_url = '/computers/target/'
        self.test_data = {
            'name':'BU Server',
            'target_type':'computer',
        }




class CyberRiskAssessmentViewsTests(F2TestCase):
    def setUp(self):
        self.set_regime(CyberRiskAssessment)

        t1 = CyberTarget(name='Router1', description='Netgear Router', target_type=0)
        t1.save()
        t2 = CyberTarget(name='Router2', description='Netgear Router', target_type=0)
        t2.save()

        self.row = CyberRiskAssessment(name='Server hacked', target_id=t1.id, attack_vector=2)
        self.row.save()
        self.base_url = '/computers/cra/'
        self.test_data = {
            'name':'Server destroyed in fire',
            'target_id':t2.name,
            'attack_vector':CyberRiskAssessment.ATTACK_VECTORS[4],
        }


    def test_clone(self):
        self.test_regime.allow_user(self.base_url + str(self.row.id) + '/clone', 'obj_create.html')

    def test_next(self):
        t1 = CyberTarget.objects.get(name='Router1')
        obj = CyberRiskAssessment(name='Server fails', target_id=t1.id, attack_vector=3)
        obj.save()
        self.test_regime.redirect(self.base_url + str(self.row.id) + '/next', self.base_url + str(obj.id))

    def test_next_end(self):
        t1 = CyberTarget.objects.get(name='Router1')
        obj = CyberRiskAssessment(name='Server fails', target_id=t1.id, attack_vector=1)
        obj.save()
        self.test_regime.redirect(self.base_url + str(self.row.id) + '/next', self.base_url)

    def test_edit_next(self):
        t1 = CyberTarget.objects.get(name='Router1')
        obj = CyberRiskAssessment(name='Server fails', target_id=t1.id, attack_vector=3)
        obj.save()
        self.test_regime.redirect_user(self.base_url + str(self.row.id) + '/edit_next', self.base_url + str(obj.id) + '/edit')


