# Generated manually to create django-parler translation tables

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_remove_incorrect_name_fields'),
    ]

    operations = [
        # Create CategoryTranslation table
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='products.category')),
            ],
            options={
                'verbose_name': 'category Translation',
                'db_table': 'products_category_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        
        # Create ProductTranslation table
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='products.product')),
            ],
            options={
                'verbose_name': 'product Translation',
                'db_table': 'products_product_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        
        # Create ShopTranslation table
        migrations.CreateModel(
            name='ShopTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('city', models.CharField(max_length=100, verbose_name='Город')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='products.shop')),
            ],
            options={
                'verbose_name': 'shop Translation',
                'db_table': 'products_shop_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        
        # Create TagTranslation table
        migrations.CreateModel(
            name='TagTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='products.tag')),
            ],
            options={
                'verbose_name': 'tag Translation',
                'db_table': 'products_tag_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='categorytranslation',
            unique_together={('language_code', 'master')},
        ),
        migrations.AlterUniqueTogether(
            name='producttranslation',
            unique_together={('language_code', 'master')},
        ),
        migrations.AlterUniqueTogether(
            name='shoptranslation',
            unique_together={('language_code', 'master')},
        ),
        migrations.AlterUniqueTogether(
            name='tagtranslation',
            unique_together={('language_code', 'master')},
        ),
    ]