# -*- coding: utf-8 -*-


db.define_table('pic_comments',
                Field('picid', 'reference picture'),
                Field('comment_type', 'integer'), #0=?(normal comment), 1=?(question), 2=?(awnser)
                Field('contents', 'text'),
                Field('creation_time', 'datetime'),
                Field('poster_id', 'reference student'),
                )

db.pic_comments.picid.writable       = db.pic_comments.picid.readable = False
db.pic_comments.poster_id.writable    = db.pic_comments.poster_id.readable = False
db.pic_comments.comment_type.writable = db.pic_comments.comment_type.readable = False
