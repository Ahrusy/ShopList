# Generated manually to fix incorrect name fields added by migration 0015

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_alter_category_name_alter_product_description_and_more'),
    ]

    operations = [
        # Remove the incorrect name field from Category table
        # (it should only exist in the translation table)
        migrations.RunSQL(
            "ALTER TABLE products_category DROP COLUMN name;",
            reverse_sql="ALTER TABLE products_category ADD COLUMN name VARCHAR(100);"
        ),
        
        # Remove the incorrect name field from Product table
        # (it should only exist in the translation table)
        migrations.RunSQL(
            "ALTER TABLE products_product DROP COLUMN name;",
            reverse_sql="ALTER TABLE products_product ADD COLUMN name VARCHAR(255);"
        ),
        
        # Remove the incorrect description field from Product table
        # (it should only exist in the translation table)
        migrations.RunSQL(
            "ALTER TABLE products_product DROP COLUMN description;",
            reverse_sql="ALTER TABLE products_product ADD COLUMN description TEXT;"
        ),
        
        # Remove the incorrect name field from Tag table
        # (it should only exist in the translation table)
        migrations.RunSQL(
            "ALTER TABLE products_tag DROP COLUMN name;",
            reverse_sql="ALTER TABLE products_tag ADD COLUMN name VARCHAR(50);"
        ),
        
        # Remove the incorrect fields from Shop table
        # (they should only exist in the translation table)
        migrations.RunSQL(
            "ALTER TABLE products_shop DROP COLUMN name;",
            reverse_sql="ALTER TABLE products_shop ADD COLUMN name VARCHAR(255);"
        ),
        migrations.RunSQL(
            "ALTER TABLE products_shop DROP COLUMN address;",
            reverse_sql="ALTER TABLE products_shop ADD COLUMN address TEXT;"
        ),
        migrations.RunSQL(
            "ALTER TABLE products_shop DROP COLUMN city;",
            reverse_sql="ALTER TABLE products_shop ADD COLUMN city VARCHAR(100);"
        ),
    ]