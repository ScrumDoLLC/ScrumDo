import datetime
from haystack.indexes import *
from haystack import site
from projects.models import Story
import traceback
import logging

logger = logging.getLogger(__name__)

class StoryIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    project_id = IntegerField( model_attr='project_id' )
    iteration_id = IntegerField( model_attr='iteration_id' )
    local_id = IntegerField( model_attr='local_id' )
    user_id = IntegerField( model_attr='assignee_id' , null=True)
    numeric_points = IntegerField( model_attr='points_value' )
    created = DateField(model_attr='created')
    status = IntegerField(model_attr='status')
    rank = IntegerField(model_attr='rank')
    tags = CharField(model_attr='tags')
    category = CharField(model_attr='category', null=True)
    def prepare(self, object):
        try:
            self.prepared_data = super(StoryIndex, self).prepare(object)
        except Exception as e:
            logger.error("Story Index super failed to run! %s" % e)
            traceback.print_exc()


        fields = ('user_id','category','status','numeric_points','tags')
        for field in fields:
            if not field in self.prepared_data:
                self.prepared_data[field] = ""

        return self.prepared_data

site.register(Story, StoryIndex)
