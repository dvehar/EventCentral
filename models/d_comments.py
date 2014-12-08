# -*- coding: utf-8 -*-

#comments on an event
db.define_table('comments',                              #will probably be modified later to include type of post and whatever else
                Field('event_id', 'reference events'),   #also used for picture ids
                Field('comment_type', 'integer'),        #0=?(normal comment), 1=?(question), 2=?(awnser)
                Field('contents', 'text'),
                Field('creation_time', 'datetime'),
                Field('poster_id', 'reference student'), # use controller logic to check if the student who posted is a admin of the student org
                )

db.comments.event_id.writable = db.comments.event_id.readable = False
db.comments.poster_id.writable = db.comments.poster_id.readable = False
db.comments.comment_type.writable = db.comments.comment_type.readable = False
