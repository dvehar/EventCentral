# -*- coding: utf-8 -*-

from datetime import datetime

class IS_AFTER_START_TIME():
    def __init__(self, error_message='must be greater than start_time'):
        self.error_message = error_message
    def __call__(self, value):
        if datetime(value) >= end_time:
            return (datetime(value), None)
        else:
            return (value, self.error_message)
    def formatter(self, value):
        return str(value)

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
#TODO force start time to be before end_time