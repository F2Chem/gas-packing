import re
import datetime

from django.utils.module_loading import import_string
from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model


from util.util import *



User = get_user_model()


"""
Utilities that makes simple testing of views much easier

Your test case can inherit from F2TestCase rather than TestCase and it will get a bunch of default tests
automatically covering the usual set of views.
NOTE: You MUST call set_regime in the SetUp method

Example, showing how further tests can be added:

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
        
        
The test_data is used when testing edited and created. A full set of attributes is created from that and the fields for the model, using _populate_POST_data. This means the values you set must what will be sent from the form.

For "options", "options_from_table" and "options_from_array" this should be the value, not the index. In the example above, target_id is from a table, and the value is the name of the object.

You can skip tests by using self.ignore(action), where action is one of 'create', 'create_anon' (if creation is allowed by anyone) or 'edit'.

"""

class F2TestCase(TestCase):
    
    def __init__(self, args):
        super().__init__(args)
        self.ignore_list = []
    
    def set_regime(self, class_reference):
        self.test_regime = Util4Tests(self, class_reference)
        if not hasattr(class_reference, 'FIELD_LIST'):
            raise Exception('Class ' + class_reference.__name__ + ' has no FIELD_LIST set')
        if not hasattr(class_reference, 'URL_NAME'):
            raise Exception('Class ' + class_reference.__name__ + ' has no URL_NAME set')
        
    def ignore(self, action):
        self.ignore_list.append(action)
    
    # Python identifies these as tests and will attempt to run them as methods of
    # F2TestCase in addition to its subclasses - and they will fail as test_regime
    # is not set. Each one therefore first checks if this is this class rather than a subclass
    # and bails if it is.    
    def test_list(self):
        if not self.__class__.__name__ == 'F2TestCase':
            self.test_regime.allow_anonymous(self.base_url, 'obj_list.html')

    def test_details(self):
        if not self.__class__.__name__ == 'F2TestCase':
            self.test_regime.allow_anonymous(self.base_url + str(self.row.id), 'obj_detail.html')
    
    def test_create_deny_anonymous(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'create' in self.ignore_list and not 'create_anon' in self.ignore_list:
            self.test_regime.deny_anonymous(self.base_url + 'create')

    def test_create_deny_unauthorised_user(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'create' in self.ignore_list and not 'create_anon' in self.ignore_list:
            self.test_regime.deny_unauthorised_user(self.base_url + 'create')

    def test_create(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'create' in self.ignore_list:
            self.test_regime.allow_user(self.base_url + 'create', 'obj_create.html')

    def test_created(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'create' in self.ignore_list:
            self.test_regime.created(self.base_url + 'created', self.test_data)

    def test_edit_deny_anonymous(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'edit' in self.ignore_list:
            self.test_regime.deny_anonymous(self.base_url + str(self.row.id) + '/edit')

    def test_edit(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'edit' in self.ignore_list:
            self.test_regime.allow_user(self.base_url + str(self.row.id) + '/edit', 'obj_edit.html')

    def test_edited(self):
        if not self.__class__.__name__ == 'F2TestCase' and not 'edit' in self.ignore_list:
            self.test_regime.edited(self.base_url + str(self.row.id) + '/edited', self.test_data)







class Util4Tests:
    PASSWORD = 'Some password' # Just for testing, does not need to be secure!
    
    
    """
    Create the test regime in your test case setUp method.
    self.test_regime = Util4Tests(self, Computer)
    Among other things, it creates two users, "testuser" and "notalloweduser".
    The former has "add" and "change" permissions, the latter no permissions.
    """
    def __init__(self, test_case, class_reference):
        self.test_case = test_case
        self.class_reference = class_reference
        class_name = class_reference.__name__.lower()
        self.auth_user = Util4Tests._createUser('testuser', ["add_" + class_name, "change_" + class_name])
        self.unauth_user = Util4Tests._createUser('notalloweduser', [])
    
    
    def _underscore(s):
         return re.sub('([a-z])([A-Z])', r'\1_\2', s).lower()
    
    
    """
    Create a user for testing views, for example like this:
    Util4Tests.createUser('testuser', ["add_device", "change_device"])
    Used internally; may be useful to do elsewhere?
    """
    def _createUser(name, permissions=[]):
        user = User.objects.create(username=name)
        user.set_password(Util4Tests.PASSWORD)
        for el in permissions:
            try:
                perm = Permission.objects.get(codename=el)
                user.user_permissions.add(perm)
            except:
                s = 'Failed to find a permission object called ' + str(el)
                result = list(map(lambda x: x.codename, Permission.objects.all()))
                s += '\nPermissions available: ' + ', '.join(result)
                raise Exception(s)
        user.save()
        return user
    
    
    def get_name_with_underscores(str):
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", str).lower()
    
    
    
    # When creating a new instance of the model in a test, you need to populate
    # the POST data. This will fill in default values for most types.
    # Returns a dictionary that uses but is not the same as data
    def _populate_POST_data(class_reference, data):
        new_data = {}
        for el in class_reference.FIELD_LIST:
            if not 'column' in el:
                continue
            if el['column'] in data:
                new_data[el['column']] = data[el['column']]
                continue
               
            if 'options' in el:
                new_data[el['column']] = el['options'][0]
                continue
               
            if 'options_from_array' in el:
                if isinstance(el['options_from_array'][0], str):
                    new_data[el['column']] = el['options_from_array'][0]
                else:
                    attribute = el['attribute'] if 'attribute' in el else 'name'
                    new_data[el['column']] = el['options_from_array'][0][attribute]
                continue
               
            if 'options_from_table' in el:
                new_data[el['column']] = 1
                continue
                
                
            match class_reference._meta.get_field(el['column']).get_internal_type():
                case 'CharField':
                    new_data[el['column']] = ''
                case 'TextField':
                    new_data[el['column']] = ''
                case 'IntegerField':
                    new_data[el['column']] = 1
                case 'BooleanField':
                    new_data[el['column']] = False
                case 'DateField':
                    new_data[el['column']] = datetime.date.today()
                case 'DecimalField':
                    new_data[el['column']] = 0.0
                case 'ForeignKey':
                    print('ERROR: Found a ForeignKey foeld, but no "options_from_table" set: ' + el['column'])
                case _:
                    print('ERROR: Did not recognise field type: ' + class_reference._meta.get_field(el['column']).get_internal_type())
        return new_data
    
    """
    Tests that the given web page will NOT be accessible if not signed in
    """
    def deny_anonymous(self, url):
        redirected_url = '/accounts/login/?next=' + url
        response = self.test_case.client.get(url, follow=True)
        self.test_case.assertRedirects(response, redirected_url)
        response = self.test_case.client.post(url, follow=True)
        self.test_case.assertRedirects(response, redirected_url)

    """
    Tests that the given web page will NOT be accessible if signed in but not authorised
    """
    def deny_unauthorised_user(self, url):
        self.test_case.client.login(username=self.unauth_user.username, password=Util4Tests.PASSWORD)
        redirected_url = '/accounts/login/?next=' + url
        response = self.test_case.client.get(url, follow=True)
        self.test_case.assertRedirects(response, redirected_url)
        response = self.test_case.client.post(url, follow=True)
        self.test_case.assertRedirects(response, redirected_url)
  
    """
    Tests that the given web page IS accessible if not signed in
    """
    def allow_anonymous(self, url, template):
        response = self.test_case.client.get(url)
        self.test_case.assertEqual(response.status_code, 200)
        self.test_case.assertTemplateUsed(response, template)
        
    """
    Tests that the given web page IS accessible if signed in and authorised
    """
    def allow_user(self, url, template):
        self.test_case.client.login(username=self.auth_user.username, password=Util4Tests.PASSWORD)
        response = self.test_case.client.get(url, follow=True)
        if response.redirect_chain and "accounts/login" in response.redirect_chain[0][0]:
            self.test_case.assertTrue(False, "Looks like there is an issue with permissions trying to go to " + url)
        #self.test_case.assertEqual(response.redirect_chain, [], 'Not expecting to be redirected!')
        self.test_case.assertEqual(response.status_code, 200)
        self.test_case.assertTemplateUsed(response, template)
        

    """
    Tests that the given web page gives a redirect to the other given web page
    """
    def redirect(self, url, redirected_url):
        response = self.test_case.client.get(url, follow=True)
        #print(response.redirect_chain)
        self.test_case.assertRedirects(response, redirected_url)
  
    """
    Tests that the given web page gives a redirect to the other given web page
    """
    def redirect_user(self, url, redirected_url):
        self.test_case.client.login(username=self.auth_user.username, password=Util4Tests.PASSWORD)
        response = self.test_case.client.get(url, follow=True)
        self.test_case.assertRedirects(response, redirected_url)
  


    """
    Tests that a new record is created if signed in and authorised
    """
    def created(self, url, data):
        full_data = Util4Tests._populate_POST_data(self.class_reference, data)
        count = self.class_reference.objects.all().count()        
        self.test_case.client.login(username=self.auth_user.username, password=Util4Tests.PASSWORD)
        response = self.test_case.client.post(url, full_data)
        self.test_case.assertEqual(response.status_code, 302)
        self.test_case.assertEqual(self.class_reference.objects.all().count(), count + 1)

    """
    Tests that a new record is NOT created if signed in but not authorised
    """
    def created_failed(self, url, data):
        full_data = Util4Tests._populate_POST_data(self.class_reference, data)
        count = self.class_reference.objects.all().count()        
        self.test_case.client.login(username=self.unauth_user.username, password=Util4Tests.PASSWORD)
        response = self.test_case.client.post(url, full_data)
        self.test_case.assertEqual(response.status_code, 302)
        self.test_case.assertEqual(self.class_reference.objects.all().count(), count)


    """
    Tests that a record is edited if signed in and authorised
    """
    # This is likely to struggle with fields that are options etc.
    # options - use the index if read_only or the string otherwise
    # options_from_array - should work???
    # Also may be issues with fields that are falsy in data
    def edited(self, url, data):
        full_data = Util4Tests._populate_POST_data(self.class_reference, data)
        self.test_case.client.login(username=self.auth_user.username, password=Util4Tests.PASSWORD)
        response = self.test_case.client.post(url, full_data, follow=True)
        self.test_case.assertTrue(response.redirect_chain)
        # We expect a redirect, but not to the login page
        if response.redirect_chain and "accounts/login" in response.redirect_chain[0][0]:
            self.test_case.assertTrue(False, "Looks like there is an issue with permissions trying to go to " + url)
            
            
        row = self.class_reference.objects.get(id=self.test_case.row.id)
        for key in data:
            value = getattr(row, key)
            meta_data = next((x for x in self.class_reference.FIELD_LIST if 'column' in x and x['column'] == key), None)
            if meta_data:
                if 'options' in meta_data: # and not 'read_only' in meta_data:
                    value = meta_data['options'][value]
                    if value != data[key]:
                        print("In F2TestCase.edited with a field with 'options' and hit a failure")
                        print("In the edited record I have: " + str(value))
                        print("     But that should now be: " + str(data[key]))
                   
                if 'options_from_array' in meta_data: # and not 'read_only' in meta_data:
                    if isinstance(meta_data['options_from_array'][value], str):
                        value = meta_data['options_from_array'][value]
                    else:
                        attribute = meta_data['attribute'] if 'attribute' in meta_data else 'name'
                        value = meta_data['options_from_array'][value][attribute]
                    if value != data[key]:
                        print("In F2TestCase.edited, with a field with 'options_from_array' and hit a failure")
                        print("In the edited record I have: " + str(value))
                        print("     But that should now be: " + str(data[key]))
            
                if 'options_from_table' in meta_data: # and not 'read_only' in meta_data:
                    attribute = meta_data['attribute'] if 'attribute' in meta_data else 'name'
                    klass = import_string(meta_data['options_from_table'])
                    record = klass.objects.get(id=value)
                    value = getattr(record, attribute)
                    if value != data[key]:
                        print("In F2TestCase.edited, with a field with 'options_from_table' and hit a failure")
                        print("In the edited record I have: " + str(value))
                        print("     But that should now be: " + str(data[key]))
            
            self.test_case.assertEqual(value, data[key], 'Issue with ' + key)



