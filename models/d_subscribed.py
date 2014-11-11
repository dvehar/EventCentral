# -*- coding: utf-8 -*-

db.define_table('subscribed',
                Field('student_id', 'reference student'),
                Field('student_org_id', 'reference student_org')
                )
