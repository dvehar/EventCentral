# -*- coding: utf-8 -*-

db.define_table('tag',
    Field('tag_name', 'string', requires=IS_NOT_EMPTY()),
    )
