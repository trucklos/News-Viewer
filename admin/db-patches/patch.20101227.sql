/*
SCHEMA CHANGES
to run the patch run this command from the newsviewer/ directory
cat /ABSOLUTE_PATH_HERE/patch.sql | ./manage.py dbshell
*/

-- table: stories_story
-- add unique constraint to story
alter table stories_story modify column url varchar(200) not null unique;

-- allow time_closed to be null
alter table stories_story modify column time_closed datetime null;

-- allow current_position to be null
alter table stories_story modify column current_position int null;

/*
Latest Create Table:

CREATE TABLE `stories_story` (
  `id` int(11) NOT NULL auto_increment,
  `url` varchar(200) NOT NULL,
  `title` varchar(512) NOT NULL,
  `time_created` datetime NOT NULL,
  `time_closed` datetime default NULL,
  `current_position` int(11) default NULL,
  `feed_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `stories_story_153f3bfc` (`feed_id`)
)

*/

/*
DATA MIGRATION
*/

-- first whipe out bogus data
update stories_story set time_closed=null;

-- create migration table
create temporary table stories_patch_time_closed
select 
  s.id
  , update_time as time_closed
from 
  (select 
    s.id
    , s.title
    , current_position
    , max(sh.update_id) max_update 
  from stories_story s 
    join stories_storyhistory sh on sh.story_id=s.id 
  group by 1) s 
  join stories_update su on su.id=max_update+1 
where max_update != (select max(sh.update_id) from stories_story s join stories_storyhistory sh on sh.story_id=s.id );

-- update time_closed and current_position
update stories_story, stories_patch_time_closed set current_position=null, stories_story.time_closed=stories_patch_time_closed.time_closed where stories_story.id=stories_patch_time_closed.id;