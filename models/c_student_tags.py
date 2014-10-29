# -*- coding: utf-8 -*-

db.define_table('student_tags',
                Field('student_id', 'reference student'),
                Field('tag_id', 'reference tag')
                )

db.student_tags.student_id.writable = db.student_tags.student_id.readable = False
