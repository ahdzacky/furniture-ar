import pymysql
pymysql.version_info = (2, 2, 8, "final", 0)
pymysql.install_as_MySQLdb()

# Nonaktifkan RETURNING karena MariaDB versi lama tidak mendukungnya (Django 5/6 akan mencoba menggunakan ini).
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = False
