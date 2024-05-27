from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # INT IDENTITY
    created_at = models.DateTimeField(auto_now_add=True)  # DateTime
    name = models.CharField(max_length=255)  # VarChar for name
    phone1 = models.IntegerField()  # INT
    phone2 = models.IntegerField(blank=True, null=True)  # INT, allowing it to be blank or null
    street = models.CharField(max_length=255)  # VarChar
    state = models.CharField(max_length=255)  # VarChar
    complete = models.CharField(max_length=255)  # VarChar
    zip = models.CharField(max_length=10)  # VarChar, typically zip codes are short

    def __str__(self):
        return f"{self.name} - {self.state}"