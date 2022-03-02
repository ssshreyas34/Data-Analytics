from django.db import models

# Create your models here.
class Registration(models.Model):
    username=models.CharField(max_length=100000,primary_key=True,verbose_name="Enter username")
    password=models.CharField(max_length=20,verbose_name="Enter Password")
    def __str__(self):
        return self.username

class Hash_key(models.Model):
    hash_username=models.OneToOneField(Registration,on_delete=models.CASCADE,primary_key=True)
    user_key=models.CharField(max_length=256)
    def __str__(self):
        return self.hash_username

class Uni_analysis(models.Model):
    data=models.CharField(max_length=10000000000000000000)
    name=models.CharField(max_length=10000000000000000000)
    def __str__(self):
        return self.name
