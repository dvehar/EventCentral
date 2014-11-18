# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('student_org_tags',
                Field('student_org_id', 'reference student_org'),
		        Field('tag_id', 'reference tag')
		        )

db.student_org_tags.student_org_id.writable = db.student_org_tags.student_org_id.readable = False
