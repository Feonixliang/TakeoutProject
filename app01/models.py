# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    accounttype = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'account'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Customer(models.Model):
    cid = models.OneToOneField(Account, models.DO_NOTHING, db_column='CId', primary_key=True)  # Field name made lowercase.
    cname = models.CharField(db_column='CName', unique=True, max_length=50)  # Field name made lowercase.
    cphone = models.CharField(db_column='CPhone', unique=True, max_length=30)  # Field name made lowercase.
    caddress = models.CharField(db_column='CAddress', max_length=200)  # Field name made lowercase.
    cbalance = models.DecimalField(db_column='CBalance', max_digits=10, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer'


class Dishes(models.Model):
    did = models.AutoField(db_column='DId', primary_key=True)  # Field name made lowercase.
    dname = models.CharField(db_column='DName', max_length=100)  # Field name made lowercase.
    dprice = models.DecimalField(db_column='DPrice', max_digits=10, decimal_places=2)  # Field name made lowercase.
    dcategory = models.CharField(db_column='DCategory', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dishes'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Merchant(models.Model):
    mid = models.OneToOneField(Account, models.DO_NOTHING, db_column='MId', primary_key=True)  # Field name made lowercase.
    mname = models.CharField(db_column='MName', max_length=100)  # Field name made lowercase.
    mphone = models.CharField(db_column='MPhone', unique=True, max_length=30)  # Field name made lowercase.
    maddress = models.CharField(db_column='MAddress', max_length=200)  # Field name made lowercase.
    mbalance = models.DecimalField(db_column='MBalance', max_digits=10, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'merchant'


class Merchantdishes(models.Model):
    did = models.OneToOneField(Dishes, models.DO_NOTHING, db_column='DId', primary_key=True)  # Field name made lowercase. The composite primary key (DId, MId) found, that is not supported. The first column is selected.
    mid = models.ForeignKey(Merchant, models.DO_NOTHING, db_column='MId', related_name='dishes')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'merchantdishes'
        unique_together = (('did', 'mid'),)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待接单'),
        ('active', '配送中'),
        ('completed', '已完成'),
        ('canceled', '已取消')
    )
    oid = models.AutoField(db_column='OId', primary_key=True)  # Field name made lowercase.
    cid = models.ForeignKey(Customer, models.DO_NOTHING, db_column='CId', default=-1)  # Field name made lowercase.
    mid = models.ForeignKey(Merchant, models.DO_NOTHING, db_column='MId')  # Field name made lowercase.2
    rid = models.ForeignKey('Rider', models.DO_NOTHING, db_column='RId', blank=True, null=True)  # Field name made lowercase.
    totalprice = models.DecimalField(db_column='TotalPrice', max_digits=10, decimal_places=2)  # Field name made lowercase.
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,  # 添加这行
        default='pending'
    )

    class Meta:
        managed = True
        db_table = 'order'


class Orderdishes(models.Model):
    oid = models.ForeignKey(Order, models.DO_NOTHING, db_column='OId')
    did = models.ForeignKey(Dishes, models.DO_NOTHING, db_column='DId')
    quantity = models.IntegerField(db_column='Quantity')

    class Meta:
        managed = False
        db_table = 'orderdishes'
        unique_together = (('oid', 'did'),)  # 联合唯一约束


class Rider(models.Model):
    rid = models.OneToOneField(Account, models.DO_NOTHING, db_column='RId', primary_key=True)  # Field name made lowercase.
    rname = models.CharField(db_column='RName', unique=True, max_length=20)  # Field name made lowercase.
    rphone = models.CharField(db_column='RPhone', unique=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rider'
