from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=128)

class AIService(models.Model):
    id_service = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    monthly_price = models.IntegerField(default = 30)
    yearly_price = models.IntegerField(default = 365)
    enterprise_price_per_request = models.IntegerField(default=1)
    url = models.CharField(max_length=500, unique = True, null = False)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(AIService, on_delete=models.CASCADE)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(null=True)
    active = models.CharField(max_length=100, choices=[('Pending','Pending'),('Approved', 'Approved'),('Cancelled','Cancelled')])
    type = models.CharField(null = True, max_length=50, choices=[('Monthly','Monthly'),('Yearly','Yearly'),('Enterprise','Enterprise')])
    def __str__(self):
        return f"{self.user.username} - {self.service.name}"
    
    def update_active_status(self):
        if self.date_ended and timezone.now() > self.date_ended:
            self.active = 'Cancelled'
            self.save()
            
    def set_date_ended(self):
        if self.type == 'Monthly' or self.type == "monthly":
            self.date_ended = timezone.now() + timedelta(days=30)  # Assuming 30 days in a month
        elif self.type == 'Yearly'  or self.type == "yearly":
            self.date_ended = timezone.now() + timedelta(days=364)  # Assuming 365 days in a year
        elif self.type == 'Enterprise':
            # Implement your own logic for enterprise type, e.g., based on specific rules
            pass
        self.save()

class Billing(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    service = models.ForeignKey(AIService, on_delete=models.CASCADE)

class RequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(AIService, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete = models.CASCADE, null=True)
    request_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)  # e.g., 'Success', 'Failed'
    processing_time = models.FloatField(help_text="Time in seconds to process the request")

    def __str__(self):
        return f"{self.user.username} {self.status} on {self.request_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
#dashboard: tong request, tong tien, bieu do ti le thanh cong, bieu do so luong requestn theo ngay
#service_detail: so luong request, tong chi phi, request history

