# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User


from collections import namedtuple
from django.shortcuts import render
from itertools import groupby
from operator import itemgetter

import datetime, json
import math

from datetime import timedelta
from datetime import tzinfo
from dateutil import parser
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.core.urlresolvers import resolve
from django.db.models import Count
from django.db.models import F
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q
from django.db.models import Sum
from django.dispatch import receiver
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from user_agents import parse
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
import re

import urllib

from collections import OrderedDict
from collections import defaultdict


from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

import ast
import copy
import hashlib
import uuid

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.template import Context
from rest_framework import authentication
from rest_framework import generics
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import serializers
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework_extensions.cache.decorators import (cache_response)

from django.views.decorators.cache import cache_page
from models import UserTransactionRecord


class UserExamPostSelectedData(APIView):
	"""	Request for SSCUserTimeTable.
	URL = api/1/add-exams/

	Available methods: `POST`

	Authentication Required: `No`

	Post data: exam_ids """

	# authentication_classes = (
	# 	authentication.TokenAuthentication,
	# 	authentication.SessionAuthentication
	# )

	# permission_classes = [permissions.IsAuthenticated]


	def post(self, request, version, format=None):
		user_data = request.data
		user_data = user_data['data']['data']

		user_email = user_data.get('user_email')

		if not User.objects.filter(email=user_email).exists():
			user = User.objects.create(email=user_email)
		else:
			user = User.objects.filter(email=user_email).last()

		user_record = UserTransactionRecord.objects.create(user=user)

		user_action = user_data.get('action')
		user_amount = user_data.get('amount')

		user_record.transaction_money = user_amount
		if user_action.lower() == 'debit':
			user_record.trasaction_type = UserTransactionRecord.DEBIT
		elif user_action.lower() == 'credit':
			user_record.trasaction_type = UserTransactionRecord.CREDIT

		user_record.trasaction_id = user_data.get('transaction_id')
		
		user.save()
		user_record.save()

		response = {"response": "All Activities are successfully saved!"}

		return Response(response, status=status.HTTP_200_OK)

