from django.db import migrations, models

def move_order_to_orderline(apps, schema_editor):
    Filling = apps.get_model('gas_filling', 'Filling')
    OrderLine = apps.get_model('gas_filling', 'OrderLine')

    for filling in Filling.objects.all():
        if filling.order_id:
            orderline = OrderLine.objects.filter(order_id=filling.order_id).first()
            if orderline:
                filling.order_line_id = orderline.id
                filling.save()

class Migration(migrations.Migration):

    dependencies = [
        ('gas_filling', '0009_filling_heel_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='filling',
            name='order_line',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='fillings',
                null=True,
                blank=True,
                to='gas_filling.OrderLine',
            ),
        ),
        migrations.RunPython(move_order_to_orderline),
        migrations.RemoveField(
            model_name='filling',
            name='order',
        ),
    ]
