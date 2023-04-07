# Generated by Django 4.1.7 on 2023-04-05 18:40

from django.db import migrations, models
import finpal_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('finpal_app', '0004_portfolio_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=100)),
                ('accuracy', models.CharField(max_length=100)),
                ('model', models.TextField(validators=[finpal_app.models.validate_json])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]