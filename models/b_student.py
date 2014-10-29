# -*- coding: utf-8 -*-

db.define_table('student',
    Field('student_name', 'reference auth_user', default=auth.user_id), # bad field name?
    )
