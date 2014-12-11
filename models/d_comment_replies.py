# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

db.define_table('comment_replies',
                Field('comment_id', 'integer'),
                Field('comment_type', 'integer'), #0=?(event reply), #1 =(picture reply)
                Field('contents', 'text'),
                Field('creation_time', 'datetime'),
                Field('poster_id', 'reference auth_user'),
                )

db.comment_replies.comment_id.writable   = db.comment_replies.comment_id.readable = False
db.comment_replies.poster_id.writable    = db.comment_replies.poster_id.readable = False
db.comment_replies.comment_type.writable = db.comment_replies.comment_type.readable = False
