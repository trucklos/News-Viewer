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