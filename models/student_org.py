# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('student_org',
    Field('name', 'reference auth_user', default=auth.user_id),
    Field('join_date', 'datetime', default=request.now),
    Field('acronym', 'string', requires=IS_NOT_EMPTY()),
    Field('website', 'string', requires=IS_NOT_EMPTY()),
    Field('description', 'text', requires=IS_NOT_EMPTY()),
    )

db.notes.name.writable = db.notes.author.readable = False
db.notes.join_date.writable = db.notes.join_date.readable = False
