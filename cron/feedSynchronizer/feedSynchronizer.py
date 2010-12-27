#!/usr/bin/env python

# Import the Django settings and Models we'll need
import os, sys

#nv_carlos_ag = '/Users/carlos/Documents/django/News-Viewer/www/nv.carlos.ag/application/'
 nv_carlos_ag = '/srv/www/nv.carlos.ag/application/'
nv = nv_carlos_ag + 'newsviewer/'
sys.path.append(nv_carlos_ag) # the root of the site (for settings)
sys.path.append(nv) # the project
sys.path.append(nv + 'stories') # the app

os.environ['DJANGO_SETTINGS_MODULE'] = 'newsviewer.settings'

from stories.models import Feed, Story, Update, StoryHistory

import feedparser
import datetime

def main():
    # this is the single Update object for this run
    # assume success, and save, so that other inserts
    # won't fail at the SQL level.
    # We will re-save again if anything fails
    update = Update(success=True)
    update.save()
    
    # get all the feeds
    feeds = Feed.objects.all()
    
    # for each feed:
    for feed in feeds:
        # get the RSS
        rssUrl = feed.url
        
        # parse the RSS
        parsedFeed = feedparser.parse(rssUrl)
        
        debug(parsedFeed)

        currentStoryIds = []
        # for each story in the RSS:
        items = parsedFeed['items']
        for i in range(len(items)):
            item = items[i]
            
            storyId = saveItemIfPositionChanged(i, item, feed, update)
            currentStoryIds.append(storyId)
            success = bool(storyId)
            if not success:
                update.success = False
                update.save()

                print "Error"
                debug(item)

        #close stories: check for stories that are still active (time_closed is null) but were not in this update.
        for s in Story.objects.filter(time_closed=None):
            if s.id not in currentStoryIds:
                s.time_closed = datetime.datetime.now()
                s.current_position = None
                s.save()
                # todo_los we still need a way to terminate, maybe add a -1 update?
        

def saveItemIfPositionChanged(pos, item, feed, update):
    url = item['link']
    
    newItem = False
    
    try:
        # try to find this item in Django
        s = Story.objects.get(url=url)
    except Story.DoesNotExist:
        # story does not exist, so create one now
        title = item['title']
        
        # active stories will have null time_closed values: this will make it easy to filter for open stories.
        time_closed = None
        s = Story(url=url, title=title, current_position=pos, time_closed=time_closed, feed=feed)
        s.save()
        
        newItem = True
    except Story.MultipleObjectsReturned:
        # todo_sam: this should never happen
        # error("MultipleObjectsReturned for url='%s'" % url)
        return False
    
    # at this point s will be a valid Story object, either new or old
    currPos = s.current_position
    story_closed = bool(s.time_closed)
    if newItem or currPos != pos:
        # the position changed,
        # create a story history...
        sh = StoryHistory(position = pos, story = s, update = update)
        sh.save()

    # if the position doesn't match or the story has been closed we will need to save the story
    if currPos != pos or story_closed:
        # update the cached pos
        s.current_position = pos
        s.time_closed = None
        s.save()
    
    # True: we succeeded in saving the pos, return the story's id
    return s.id

dbgObjs = []
def debug(obj):
    global dbgObjs
    dbgObjs.append(obj)

if __name__ == '__main__':
    main()

