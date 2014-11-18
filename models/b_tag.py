# -*- coding: utf-8 -*-

db.define_table('tag',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                )
