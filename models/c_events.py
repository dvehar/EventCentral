# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('events',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('student_org_id', 'reference student_org', requires=IS_NOT_EMPTY()),
                Field('place', 'string', requires=IS_NOT_EMPTY()),
                Field('start_time', 'datetime', requires=IS_NOT_EMPTY()),
                Field('end_time', 'datetime', requires=IS_NOT_EMPTY()),
                Field('create_time', 'datetime', default=request.now)
                )

db.events.student_org_id.writable = db.events.student_org_id.readable = False
db.events.create_time.writable = False
