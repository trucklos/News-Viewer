from django.db import models

class Feed(models.Model):
        url  = models.URLField(unique=True)
        title = models.CharField(max_length=512)
        def __unicode__(self):
                return self.title

class Story(models.Model):
        url  = models.URLField()
        title = models.CharField(max_length=512)
        time_created = models.DateTimeField(auto_now_add=True)
        time_closed = models.DateTimeField(null=True)
        current_position = models.IntegerField(null=True)
        feed = models.ForeignKey(Feed)
        def __unicode__(self):
                return self.title

class Update(models.Model):
        update_time = models.DateTimeField(auto_now_add=True)
        success = models.BooleanField()

class StoryHistory(models.Model):
        story = models.ForeignKey(Story)
        position = models.IntegerField()
        update = models.ForeignKey(Update)
