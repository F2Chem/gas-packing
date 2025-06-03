import datetime
import re

from django.test import TestCase
from django.urls import reverse

from computers.models import *
from util.util import *
from templatetags.helpers import *



class CyberTargetTests(TestCase):
    def setUp(self):
        CyberTarget(name='Router1', description='Netgear Router', target_type=0).save()
        CyberTarget(name='Router2', description='Netgear Router', target_type=0).save()


    def test_generate_cras(self):
        target = CyberTarget.objects.first()
        count = CyberRiskAssessment.objects.all().count()
        target.generate_cras()
        self.assertEqual(CyberRiskAssessment.objects.all().count(), count + len(CyberRiskAssessment.ATTACK_VECTORS))
        





class CyberRiskAssessmentTests(TestCase):
    def setUp(self):
        CyberTarget(name='Router1', description='Netgear Router', target_type=0).save()
        CyberTarget(name='Router2', description='Netgear Router', target_type=0).save()
        target = CyberTarget(name='Firewall', description='SonicWall Firewall', target_type=0)
        target.save()
        CyberTarget(name='Router3', description='Netgear Router', target_type=0).save()
        self.row = CyberRiskAssessment(name='Test CRA', target_id=target.id, attack_vector=2)


    def test_outcome_all(self):
        outcome = self.row.outcome_all()
        self.assertEqual(outcome, '')
        
        self.row.network_disruption = True
        self.row.save()
        outcome = self.row.outcome_all()
        self.assertEqual(outcome, 'Could result in disruption to network. ')
        
        self.row.data_breach = True
        self.row.save()
        outcome = self.row.outcome_all()
        self.assertEqual(outcome, 'Could result in data breach (access to files). Could result in disruption to network. ')
        
        self.row.outcome = 'Bad stuff!'
        self.row.save()
        outcome = self.row.outcome_all()
        self.assertEqual(outcome, 'Could result in data breach (access to files). Could result in disruption to network. Bad stuff!')
        
        


    def test_next(self):
        target = CyberTarget.objects.first()
        cra1 = CyberRiskAssessment(name='Test CRA 1', target_id=target.id, attack_vector=0)
        cra1.save()
        cra2 = CyberRiskAssessment(name='Test CRA 2', target_id=target.id, attack_vector=1)
        cra2.save()
        cra3 = CyberRiskAssessment(name='Test CRA 3', target_id=target.id, attack_vector=2)
        cra3.save()
        
        self.assertEqual(cra1.next(), cra2)
        self.assertEqual(cra2.next(), cra3)
        self.assertEqual(cra3.next(), None)


    def test_risk_as_html(self):
        risk = self.row.risk_as_html()
        self.assertRegex(risk, re.compile('Not determined'))
        self.assertEqual(self.row.risk_as_str(), 'not determined')
        
        self.row.not_relevant = True
        self.row.save()
        risk = self.row.risk_as_html()
        self.assertRegex(risk, re.compile('Not relevant'))
        self.assertEqual(self.row.risk_as_str(), 'not relevant')

        self.row.not_relevant = False
        self.row.likelihood = 1
        self.row.consequences = 1
        self.row.save()
        risk = self.row.risk_as_html()
        self.assertRegex(risk, re.compile('Acceptable'))
        self.assertEqual(self.row.risk_as_str(), 'acceptable')

        self.row.not_relevant = False
        self.row.likelihood = 10
        self.row.consequences = 10
        self.row.save()
        risk = self.row.risk_as_html()
        self.assertRegex(risk, re.compile('Unacceptable'))
        self.assertEqual(self.row.risk_as_str(), 'unacceptable')


    def test_clone(self):
        clone = self.row.clone()
        self.assertEqual(clone.name, self.row.name + ' (additional)')
        

