# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('picture',
                Field('image', 'upload', requires=IS_NOT_EMPTY()),
                Field('id_of_picture_owner', 'integer', requires=IS_NOT_EMPTY()), # it is really a id for a record int the 'student_org' or 'events' table
                Field('picture_ownder_is_student_org', 'boolean', requires=IS_NOT_EMPTY())
                )

db.picture.id_of_picture_owner.writable = db.picture.id_of_picture_owner.readable = False
db.picture.picture_ownder_is_student_org.writable = db.picture.picture_ownder_is_student_org.readable = False

# todo how to enforce id being in 'student_org' or 'events' table based on picture_ownder_is_student_org
