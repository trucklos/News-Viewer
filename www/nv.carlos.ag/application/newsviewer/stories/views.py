from django.shortcuts import render_to_response

from stories.models import Feed, Story, Update, StoryHistory

def index(request):
    # compose the relevant models into the object the
    # template expects
    context = {'feeds': []}
    
    allFeeds = Feed.objects.all()
    for feed in allFeeds:
        storyList = []
        
        allStories = Story.objects.filter(feed__id=feed.id)
        for story in allStories:
            allPositions = StoryHistory.objects.filter(story__id=story.id)
            posList = [int(p.position) for p in allPositions]
            
            storyDict = {
                'url': story.url,
                'title': story.title,
                'positions': posList
            }
            storyList.append(storyDict)
        
        feedDict = {
            'url': feed.url,
            'title': feed.title,
            'stories': storyList
        }
        
        context['feeds'].append(feedDict)
    
    return render_to_response('index.html', context)