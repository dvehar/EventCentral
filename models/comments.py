# -*- coding: utf-8 -*-
db.define_table('Comments',                            #will probably be modified later to include
                Field('Event_Id', integer),            #    type of post and whatever else
                Field('Comment_Type', integer),
                Field('Text', text),
                Field('Creation_Time', datetime),
                Field('Poster_Id', integer),
                Field('Admin_Post', boolean)
                )
