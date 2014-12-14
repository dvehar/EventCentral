# -*- coding: utf-8 -*-

from datetime import datetime

class IS_DATETIME():
    def __init__(self, error_message='must be a datetime value'):
        self.error_message = error_message
    def __call__(self, value):
        try:
          vv = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
          return (vv, None)
        except ValueError:
          return (value, self.error_message)
    def formatter(self, value):
        return str(value)

db.define_table('events',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('student_org_id', 'reference student_org', requires=IS_NOT_EMPTY()),
                Field('place', 'string', requires=IS_NOT_EMPTY()),
                Field('start_time', 'datetime', requires=[IS_NOT_EMPTY(), IS_DATETIME()]),
                Field('end_time', 'datetime', requires=[IS_NOT_EMPTY(), IS_DATETIME()]),
                Field('create_time', 'datetime', default=request.now)
                )

db.events.student_org_id.writable = db.events.student_org_id.readable = False
db.events.create_time.writable = False
#TODO force start time to be before end_time
