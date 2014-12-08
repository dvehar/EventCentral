# -*- coding: utf-8 -*-

from datetime import datetime

db.define_table('notifications',
                Field('user_to_notify', 'reference auth_user'), # person who should see the notification
                Field('description', 'string'), # what the notification should say
                Field('time_created', 'datetime', default=request.now), # when the notification was created
                Field('content_link', 'string') # a link to what the notification is about
                )

# todo add validators and stuff...