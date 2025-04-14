from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=255, default='')
    role = models.CharField(default='普通用户', max_length=10)
    token = models.CharField(max_length=255, verbose_name='token', default='')
    phone_number = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')


class UserRecord(models.Model):
    name = models.CharField(max_length=255, default='')
    time = models.CharField(max_length=255, default='')
    language = models.CharField(max_length=255, default='')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    pdf_status = models.IntegerField(default=0)
    code_status = models.IntegerField(default=0)
    introduce_status = models.IntegerField(default=0)
    register_status = models.IntegerField(default=0)
    pdf_download = models.CharField(max_length=255, default='')
    code_download = models.CharField(max_length=255, default='')
    introduce_download = models.CharField(max_length=255, default='')
    register_download = models.CharField(max_length=255, default='')