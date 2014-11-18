# -*- coding: utf-8 -*-

db.define_table('admin_pool',
                Field('student_org_id', 'reference student_org'),
                Field('student_id', 'reference student'),
                Field('title', 'string') # the title the member has
                )

db.admin_pool.student_org_id.writable = db.admin_pool.student_org_id.readable = False
db.admin_pool.student_id.writable = db.admin_pool.student_id.readable = False
