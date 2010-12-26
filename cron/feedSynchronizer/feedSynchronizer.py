#!/usr/bin/env python

# Import the Django settings and Models we'll need
import os, sys

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
        
        # for each story in the RSS:
        items = parsedFeed['items']
        for i in range(len(items)):
            item = items[i]
            
            success = saveItemIfPositionChanged(i, item, feed, update)
            
            if success != True:
                update.success = False
                update.save()
                
                print "Error"
                debug(item)
                
def saveItemIfPositionChanged(pos, item, feed, update):
    url = item['link']
    
    newItem = False
    
    try:
        # try to find this item in Django
        s = Story.objects.get(url=url)
    except Story.DoesNotExist:
        # story does not exist, so create one now
        title = item['title']
        
        # todo_los: what was your intention with 'Story.time_closed'?
        time_closed = datetime.datetime(1985, 12, 31)
        s = Story(url=url, title=title, current_position=pos, time_closed=time_closed, feed=feed)
        s.save()
        
        newItem = True
    except Story.MultipleObjectsReturned:
        # todo_sam: this should never happen
        # error("MultipleObjectsReturned for url='%s'" % url)
        return False
    
    # at this point s will be a valid Story object, either new or old
    currPos = s.current_position
    if newItem or currPos != pos:
        # the position changed,
        # create a story history...
        sh = StoryHistory(position = pos, story = s, update = update)
        sh.save()
        
        # ...and be sure to update the cached pos
        s.current_position = pos
        s.save()
    
    # True: we succeeded in saving the pos, if we should have
    return True

dbgObjs = []
def debug(obj):
    global dbgObjs
    dbgObjs.append(obj)

if __name__ == '__main__':
    main()
    