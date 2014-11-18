# -*- coding: utf-8 -*-

db.define_table('event_tags',
                Field('event_id', 'reference events'),
                Field('tag_id', 'reference tag')
                )
