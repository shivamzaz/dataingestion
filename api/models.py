# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import URLValidator
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from jsonfield import JSONField, JSONCharField
from django.conf import settings
import urllib2
import BeautifulSoup
from datetime import datetime, timedelta


from django.db.models import F, Q, Min, Max, Sum


import sendgrid
import os
from sendgrid.helpers.mail import *

def send_email(reciever, context, content):
	sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
	from_email = Email(os.environ.get('SENDER_EMAIL'))
	to_email = Email(reciever)
	subject = context
	content = Content("text/plain", content)
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)


class UserTransactionRecord(models.Model):


	CREDIT = 1
	DEBIT = 2
	TRANSACTION_CHOICES = (
		(CREDIT, 'CREDIT'),
		(DEBIT, 'DEBIT')

	)

	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	mail_sent_count = models.IntegerField(null=True, blank=True, default=0)
	transactional_count = models.IntegerField(null=True, blank=True, default=0)
	transaction_money = models.IntegerField(null=True, blank=True, default=0)
	trasaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_CHOICES, default=0)
	trasaction_id = models.CharField(max_length=255, null=True, blank=True)

	added_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'user_mail_Record'

	def __unicode__(self):
		return '%s (id:%s)' % (self.user, self.id)


@receiver(post_save, sender=UserTransactionRecord)
def update_aggregation_fields(sender, instance=None, created=False, **kwargs):
	user_records = UserTransactionRecord.objects.filter(user_id=instance.user.id)

	one_day_before_time = instance.added_on - timedelta(days=1)

	trasaction_count = UserTransactionRecord.objects.filter(user_id=instance.user.id, trasaction_type=UserTransactionRecord.DEBIT).aggregate(Sum('transaction_money'))
	transaction_money = UserTransactionRecord.objects.filter(user_id=instance.user.id, trasaction_type=UserTransactionRecord.DEBIT).filter(added_on__gte=one_day_before_time).filter(added_on__lte=instance.added_on).distinct().aggregate(Sum('transactional_count'))
	
	if transaction_money > 10000:
		context = "Debited Money Details"
		content = str(instance.added_on.strftime("%Y-%m-%d")) + "Your Transactional money(debited) in a day reached more than 10000"
		send_email(instance.user.email, context, content)

	time_now = instance.added_on
	one_hour_before_time = instance.added_on - timedelta(hours=1)
	total_user_records_in_hour = user_records.filter(added_on__gte=one_hour_before_time).filter(added_on__lte=time_now).distinct()
	if total_user_records_in_hour.count()>3:
		context = "Your Trasaction Details"
		content = "You've made more than 3 trasactions in a hour"
		send_email(instance.user.email, context, content)
		




