from django.shortcuts import render_to_response, get_object_or_404
from projects.models import SiteStats
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime, date
import time
import json


def stats_data(request):
  stats = SiteStats.objects.all();
  user_data = []
  user_stats = { "label":"Users", "data":user_data}
  project_data = []
  project_stats = { "label":"Projects", "data":project_data}
  story_data = []
  story_stats = { "label":"Stories", "data":story_data, "yaxis": 2}
  for stat in stats:
    stat_time = int((time.mktime(stat.date.timetuple()) - time.timezone)*1000)
    user_data.append( [stat_time, stat.user_count] );
    project_data.append( [stat_time, stat.project_count] );
    story_data.append( [stat_time, stat.story_count] );        

  json_serializer = serializers.get_serializer("json")()
  result = json.dumps([user_stats,project_stats,story_stats])
  return HttpResponse(result) #, mimetype='application/json'