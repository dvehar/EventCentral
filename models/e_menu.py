# -*- coding: utf-8 -*-

import json 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('EventCentral'),XML('&trade;&nbsp;'),
                  _class="brand",_href=URL('default','index'))
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
  (T('Home'), False, URL('default', 'index'), [])
]

response.menu.append((T('RSVP'), False, URL('default', 'rsvp')))
response.menu.append((T('Search'), False, URL('default', 'search')))
response.menu.append((T('Admin'), False, URL('default', 'org_admin')))

# query and check if there are any notifications
notification_items = []
if (auth.user): # must be logged in
  # query that ensures the logged in user is in the student table and then grabs all the info from the notifications table related to that student.
  active_notifications = db( (db.notifications.user_to_notify==auth.user.id) ).select(db.notifications.ALL, orderby=~db.notifications.time_created)
  # construct the list items from the query
  for row in active_notifications:
    callback_str = "var data = {notification_id:" + str(row.id) + "}; var msg = \"msg=\" + JSON.stringify(data); $.post(\"" + str(URL('remove_notification_callback')) + "\", msg, function(jdata) { console.log(\"Im in the callback response recieved function\"); });"
    if row.content_link == '':
      notification_items.append(['unused', False, DIV(TAG.BUTTON("X", _style="display:inline", _onclick=callback_str), P(row.description, _style="display:inline"))])
    else:
      notification_items.append(['unused', False, DIV(TAG.BUTTON("X", _style="display:inline", _onclick=callback_str), A(row.description, _style="display:inline", _href=row.content_link))])    
  if (len(active_notifications) == 0):
    notification_items.append( ['unused', False, B(I('You have no notifications'), _style='white-space:nowrap')] )
response.menu.append((SPAN('Notifications'), False, '', notification_items))
