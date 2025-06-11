from django.db import models

class TimePoint(models.Model):
    time = models.DateTimeField(primary_key=True)

    meter19pd28saltcorridor = models.BigIntegerField()
    meter17slaveharmonicsfilter = models.BigIntegerField()
    meter36hwheatingcontrolpanel = models.BigIntegerField()
    meter18cell9 = models.BigIntegerField()
    meter35rectifiercell8 = models.BigIntegerField()
    meter34dbpd7 = models.BigIntegerField()
    meter33rectifiercell1 = models.BigIntegerField()
    meter32dhfblockchiller = models.BigIntegerField()
    meter31rectifiercell4 = models.BigIntegerField()
    meter28pfcs_n460752_2 = models.BigIntegerField(db_column='meter28pfcs/n460752/2')
    meter27rectifiercell7 = models.BigIntegerField()
    meter10pd1packingdepartment = models.BigIntegerField()
    meter26pfcunitdoorwall = models.BigIntegerField()
    meter11rectifiercell6 = models.BigIntegerField()
    meter2572kwoilheater_r05pure = models.BigIntegerField(db_column='meter2572kwoilheater(r05pure)')
    meter37pp30 = models.BigIntegerField()
    meter24rectifiercell2 = models.BigIntegerField()
    meter38pfcunit466752_1 = models.BigIntegerField(db_column='meter38pfcunit466752/1')
    meter13harmonicsfilter = models.BigIntegerField()
    meter23rectifiercell3 = models.BigIntegerField()
    meter39fluorinemcc = models.BigIntegerField()
    meter14carbwashchiller = models.BigIntegerField()
    meter22rectifiercell5 = models.BigIntegerField()
    meter40flutecmezzfloor = models.BigIntegerField()
    meter15dbpd2_fluorine = models.BigIntegerField(db_column='meter15dbpd2(fluorine)')
    meter21db31_db32portacabin_offices = models.BigIntegerField(db_column='meter21db31/db32portacabin/offices')
    meter16pd13_flutec = models.BigIntegerField(db_column='meter16pd13(flutec)')
    meter20pd3_s = models.BigIntegerField(db_column='meter20pd3(s)')


    class Meta:
        db_table = 'powermeterreadings'
