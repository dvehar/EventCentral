# -*- coding: utf-8 -*-

db.define_table('rsvp',
                Field('event_id', 'reference events'),
                Field('student_id', 'reference student'),
                Field('rsvp_yes_or_maybe', 'boolean') # true = 'yes', false = 'maybe'
               )

db.rsvp.event_id.writable = db.rsvp.event_id.readable = False
db.rsvp.student_id.writable = db.rsvp.student_id.readable = False
