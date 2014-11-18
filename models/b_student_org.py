# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('student_org',
                Field('join_date', 'datetime', default=request.now),
	            Field('name', 'string', unique=True),
                Field('acronym', 'string', requires=IS_NOT_EMPTY()),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('website', 'string', requires=IS_NOT_EMPTY()),
	            Field('meeting_times', 'string', requires=IS_NOT_EMPTY())
                )

db.student_org.join_date.writable = db.student_org.join_date.readable = False
