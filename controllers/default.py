# -*- coding: utf-8 -*-

### Imports ###
from gluon.debug import dbg
import json 
from operator import itemgetter


###########################################################################################################################################################################################
#################################################################################   VIEW   ################################################################################################
###########################################################################################################################################################################################


@auth.requires_login()
def index():
  response.flash = T("Welcome to EventCentral!")
  admin = db((request.args(0) == db.admin_pool.student_id)).select()
  return dict(user_id=auth.user.id, admin=admin)


#This page lets you view the student org profiles.
@auth.requires_login()
def view_student_org():
    student_orgs = db.student_org(request.args[0]) or redirect(URL('index'))
    return dict(student_orgs=student_orgs, user_id = auth.user_id)


#This page lets you view the event page
@auth.requires_login()
def view_event():
    this_event = db.events(request.args(0, cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.events).process()
    # todo query for stuff
    rsvp_row = db( (db.student.student_name == auth.user.id) & (auth.user.id == db.student.student_name) & (db.rsvp.student_id == auth.user.id) & (db.rsvp.event_id == request.args(0, cast=int)) ).select(db.rsvp.ALL).first()
    if (rsvp_row == None):
      rsvp_type = ''
      rsvp_id = -1
    else:
      rsvp_type = rsvp_row['rsvp_yes_or_maybe']
      rsvp_id = rsvp_row['id']
    rsvp_change_callback = URL('rsvp_action_callback')
    rsvp_remove_callback = URL('un_rsvp_action_callback')
    return dict(events=this_event, form=form, rsvp_type=rsvp_type, rsvp_id=rsvp_id, user_id=auth.user.id, rsvp_change_callback=rsvp_change_callback, rsvp_remove_callback=rsvp_remove_callback)


def view_all():
    events = db(db.events.id >0).select(orderby=db.events.name)
    links = [A(e.name, _href=URL('view_event',args=e.id)) for e in events]
    orgs = db(db.student_org.id >0).select(orderby=db.student_org.name)
    links2 = [A(o.name, _href=URL('view_student_org', args=o.id)) for o in orgs]
    return dict(target_div=UL(*links), target_div2=UL(*links2))


#shows the picture and its comments
def view_picture():
    pic = db.picture(request.args(0))
    if pic is None:
        session.flash = "Invalid request"
        redirect(URL('default', 'index'))
    return dict(pic = pic)


###########################################################################################################################################################################################
#################################################################################   NOTIFICATIONS   #######################################################################################
###########################################################################################################################################################################################


def remove_notification_callback():
  ### Created by Desmond. A ajax callback function that will remove the notification from the database ###
  v = request.vars.msg or ''
  if (v != ''):
    v = json.loads(v)
    notification_id = v['notification_id']
    db(db.notifications.id==notification_id).delete()

    return response.json(dict(errors=""))
  else:
    return response.json(dict(errors="failed to delete"))


###########################################################################################################################################################################################
#################################################################################   RVSP   ################################################################################################
###########################################################################################################################################################################################

def event_add_tag():
    ta = request.vars.msg or ''
    if (ta != ''):
        ta = json.loads(ta)
        tag_name = ta['tag']
        event_id = ta['event_id']
        dbtag = db(db.tag.name == tag_name).select(db.tag.ALL)
        if (len(dbtag) == 0):
            get_tag = db.tag.insert(name=tag_name)
            db.event_tags.insert(tag_id = get_tag.id, event_id = event_id)
        else:
            get_tag = dbtag[0]
            dbevent_tags = db((db.event_tags.tag_id == get_tag.id)& (db.event_tags.event_id == event_id)).select(db.event_tags.ALL)
            if(len(dbevent_tags)==0):
                db.event_tags.insert(tag_id = get_tag.id, event_id = event_id)
        return response.json(dict(errors=""))
    return response.json(dict(errors = "error in event_add_tag"))


def un_rsvp_action_callback():
  ### rsvp no: delete the rsvp entry - Desmond ###
  v = request.vars.msg or ''
  if (v != ''):
    v = json.loads(v)
    rsvp_id = v['rsvp_id']
    db(db.rsvp.id == rsvp_id).delete()
    return response.json(dict(errors=""))
        
  return response.json(dict(errors="there were errors"))
    
def rsvp_action_callback():
  ### rsvp yes or maybe. can be used to update a rsvp type as well. to cancel an rsvp use the other callback -Desmond ###
  v = request.vars.msg or ''
  
  if (v != ''):
    v = json.loads(v)
    user_id = v['user_id']
    rsvp_type = v['rsvp_type']
    event_id = v['event_id']
    if (rsvp_type == "Yes" or rsvp_type == "Maybe"):
      print "77   " + str(auth.user)
      # try to fetch the event rsvp. query where student is in auth table and rsvp table. and the event id matches the rsvp event id.
      current_rsvp = db( (db.student.student_name == user_id) & (auth.user.id == db.student.student_name) & (db.rsvp.student_id == user_id) & (db.rsvp.event_id == event_id) ).select(db.rsvp.ALL)
      if (len(current_rsvp) == 0):
        # create a new rsvp
        db.rsvp.insert(event_id=event_id, student_id=user_id, rsvp_yes_or_maybe=(rsvp_type == "Yes"))
      else: # len should be 1
        # update the current_rsvp
        new_rsvp_type_value = (rsvp_type == "Yes")
        if current_rsvp.first()['rsvp_yes_or_maybe'] != new_rsvp_type_value:        
          current_rsvp.first().update_record(rsvp_yes_or_maybe=new_rsvp_type_value)
      
      return response.json(dict(errors=""))
      
  return response.json(dict(errors="there were errors"))
  
@auth.requires_login()
def rsvp():
  ### Created by Desmond. Query and return all the events the user is RSVP'd yes or maybe to ###
  rows = db((db.student.student_name == auth.user.id) & (db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id) & (db.student_org.id == db.events.student_org_id)).select(orderby=db.events.start_time|db.rsvp.rsvp_yes_or_maybe)
  #print rows
  column_sorting_ajax_url = URL('update_rsvp_column_sort')
  return dict(user_id=auth.user.id, rows=rows, column_sorting_ajax_url=column_sorting_ajax_url)


def update_rsvp_column_sort():
  ### Created by Desmond. A ajax callback function that will determine which button should be selected and the order of the data ###
  v = request.vars.msg or ''
  if (v != ''):
    v = json.loads(v)
    sorting_on_column = v['sorting_on_column']
    sort_accsending = (v['sort_accsending'] == "True")
    selected = v['selected']

    cmd = "" # when run this command will update the styel of the of the programs approperatly
    # switch off the old
    cmd = "jQuery('#" + sorting_on_column + "').css('text-decoration','');"
    # if the clicked the current coloumn change the sorting order
    if sorting_on_column == selected:
      sort_accsending = not sort_accsending
    # add a underline or an overline to the new column
    style_type = "'text-decoration','" + ("underline" if sort_accsending else "overline") + "'"
    cmd += "jQuery('#%s').css(%s);" % (selected, style_type)
    # update the variable
    sorting_on_column = selected
    bb = dict(cmd=cmd, sorting_on_column=sorting_on_column, sort_accsending=(str(sort_accsending)))
    print bb

    return response.json(bb)
  else:
    return response.json(dict(cmd=""))

  # switch off the old
  cmd = "jQuery('#%s').css(%s);" % (sorting_on_column, "'text-decoration',''")

  # if the clicked the current coloumn change the sorting order
  if sorting_on_column == request.vars.column_to_sort_on:
    sort_accsending != sort_accsending

  # add a underline or an overline to the new column
  style_type = "'text-decoration','" + ("underline" if sort_accsending else "underline") + "'"
  cmd += "jQuery('#%s').css(%s);" % (request.vars.column_to_sort_on, style_type)

  # update the variable
  sorting_on_column = request.vars.column_to_sort_on

  return cmd


###########################################################################################################################################################################################
#################################################################################   ADMIN   ###############################################################################################
###########################################################################################################################################################################################


@auth.requires_login()
def org_admin():
  ### Created by Desmond. Allows a user who is an admin of one or more student orgs to manage their orgs. Currently not complete and will be replaced by Brian's code ###
  # get info for the org id (in request) for which you are a leader. if we can't then flash and return home
  curr_org_info = db((request.args(0) == db.admin_pool.student_org_id) & (request.args(0) == db.student_org.id) & (auth.user.id == db.student.student_name) & (db.admin_pool.student_id == auth.user.id)).select()
  if (len(curr_org_info) == 0):
    session.flash = "Invalid request"
    redirect(URL('default','index'))
  #print "+++" + str(curr_org_info) + "+++" + str(request.args(0))
  curr_org_info = curr_org_info[0]['student_org']
  curr_id = request.args(0)
  org_acronyms_ids=[]#[(row['student_org'].acronym,row['student_org'].id)]
  rows = db((db.admin_pool.student_id == db.student.student_name == auth.user.id) & (db.admin_pool.student_org_id == db.student_org.id)).select(db.student_org.acronym,db.student_org.id,orderby=db.student_org.acronym)
  for idx in range(len(rows)):
    print idx
    org_acronyms_ids.append((rows[idx]['acronym'],rows[idx]['id']))
  return dict(curr_id=curr_id,org_acronyms_ids=org_acronyms_ids,curr_org_info=curr_org_info)


#checks if a user is an admin of the given event
@auth.requires_login()
def is_admin(event_id):
    event = db.events(event_id)
    student = db(db.student.student_name == auth.user.id).select().first()
    if db( (db.admin_pool.student_org_id == event.student_org_id) & (db.admin_pool.student_id == student) ).select():
        return True
    else:
        return False


@auth.requires_login()
def is_student_org_admin(student_org_id):
    student_orgs = db.student_org(student_org_id)
    student = db(db.student.student_name == auth.user.id).select().first()
    if db( (db.admin_pool.student_org_id == student_orgs.id) & (db.admin_pool.student_id == student) ).select():
        return True
    else:
        return False


#This is the page where you add a student org.
@auth.requires_login()
def add_student_org():
    form = SQLFORM(db.student_org, upload=URL('download'))
    if form.process().accepted:
        #session.flash displays a message after redirection
        session.flash = T('New student organization successfully created!')
        redirect(URL('index'))
    return dict(form=form)


#This page allows you to edit a student org.
@auth.requires_login()
def edit_student_org():
     student_orgs = db.student_org(request.args(0,cast=int)) or redirect(URL('index'))
     form = SQLFORM(db.student_org, student_orgs).process(
         next = URL('view_student_org',args=request.args))
     return dict(form=form)


#This page allows you to delete a student org.
@auth.requires_login()
def delete_student_org():
    student_orgs = db.student_org(request.args[0]) or redirect(URL('index'))
    form = SQLFORM.factory()
    if form.process().accepted:
        db(db.student_org.id == request.args[0]).delete()
        session.flash = T(student_orgs.name + ' was deleted')
        redirect(URL('index'))
    return dict(form=form, student_orgs=student_orgs)


@auth.requires_login()
def add_student_org_picture():
    if is_student_org_admin(request.args(0)):
        db.picture.id_of_picture_owner.default = request.args(0)
        db.picture.picture_owner_is_student_org.default = True
        form = SQLFORM(db.picture)
        if form.process().accepted:
            redirect(URL('view_student_org', args=(request.args(0)) ))
        return dict(form = form)
    else:
        redirect(URL('view_student_org', args=(request.args(0))))


#adds a picture to an event
@auth.requires_login()
def add_event_picture():
    if is_admin(request.args(0)):
        db.picture.id_of_picture_owner.default = request.args(0)
        db.picture.picture_owner_is_student_org.default = False
        form = SQLFORM(db.picture)
        if form.process().accepted:
            redirect(URL('view_event', args=(request.args(0)) ))
        return dict(form = form)
    else:
        redirect(URL('event', args=(request.args(0))))


#allows an admin to delete and add pictures
@auth.requires_login()
def edit_event_pictures():
    if is_admin(request.args(0)):
        event = db.events(request.args(0))
        return dict(event = event)
    else:
        redirect(URL('view_event', args=[ request.args(0) ]))


#deletes a picture from an event
@auth.requires_login()
def delete_event_picture():
    picture = db.picture(request.args(1))
    if ((picture.picture_owner_is_student_org == False) & is_admin(db.events(picture.id_of_picture_owner).id)):
        db(db.picture.id == request.args(1)).delete()
    redirect(URL('default','edit_event_pictures', args = (request.args(0)) ))
    return dict()


#allows an admin to edit the details of an event
@auth.requires_login()
def event_edit():
    if is_admin(request.args(0)) is False:
        redirect(URL('default', 'event', args=[request.args(0)]))
    event = db.events(request.args(0))
    if event is None:
        session.flash = "Invalid request"
        redirect(URL('default', 'index'))
    form = SQLFORM(db.events, record = event)
    if form.process().accepted:
        redirect(URL('default','view_event', args = [request.args(0)] ))
    return dict(form = form)


#deletes an entire event
@auth.requires_login()
def delete_event():
    if is_admin(request.args(0)):
        db(db.events.id == request.args(0)).delete()
    redirect(URL('default','index') )
    return dict()


#allows an admin to delete a post from an event
@auth.requires_login()
def delete_post():
    if is_admin(db.comments(request.args(1)).event_id):
        db(db.comments.id == request.args(1)).delete()
    redirect(URL('view_event', args=(request.args(0)) ))
    return dict()

@auth.requires_login()
def delete_event_tag():
    tag = db.event_tags(request.args(0))
    event_id = tag.event_id
    if is_admin(tag.event_id):
        db(db.event_tags.id == tag.id).delete()
    redirect(URL('view_event', args=[event_id]))

#posts a comment on an event
@auth.requires_login()
def event_post():
    db.comments.creation_time.default = request.now
    db.comments.poster_id.default = auth.user_id
    db.comments.event_id.default = request.args(0)
    db.comments.comment_type.default = request.args(2)
    form = SQLFORM(db.comments)
    if form.process().accepted:
        redirect(URL('view_event', args=(request.args(0)) ))
    return dict(form = form)


#posts a comment on a picture
@auth.requires_login()
def pic_post():
    db.pic_comments.creation_time.default = request.now
    db.pic_comments.poster_id.default = auth.user_id
    db.pic_comments.picid.default = request.args(0)
    db.pic_comments.comment_type.default = request.args(2)
    form = SQLFORM(db.pic_comments)
    if form.process().accepted:
            redirect(URL('view_picture', args=(request.args(0)) ))
    return dict(form = form)


#allows an admin to delete a post from a picture
@auth.requires_login()
def delete_pic_post():
    picture = db.pic_comments(request.args(1)).picid
    if (picture.picture_owner_is_student_org == False) & is_admin(picture.id_of_picture_owner):
        db(db.pic_comments.id == request.args(1)).delete()
    redirect(URL('view_picture', args=(request.args(0)) ))
    return dict()

@auth.requires_login()
def reply_post():
    db.comment_replies.creation_time.default = request.now
    db.comment_replies.poster_id.default = auth.user_id
    db.comment_replies.comment_id.default = request.args(1)
    db.comment_replies.comment_type.default = request.args(2)
    form = SQLFORM(db.comment_replies)
    if form.process().accepted:
        if (request.args(2) =='0'):
            redirect(URL('view_event', args=(request.args(0))))
        if (request.args(2) =='1'):
            redirect(URL('view_picture', args=(request.args(3))))
    return dict(form = form)

@auth.requires_login()
def delete_reply():
    reply = db.comment_replies(request.args(0))
    if (reply.comment_type==0):
        base = db.comments(reply.comment_id)
        if is_admin(base.event_id):
            db(db.comment_replies.id == reply.id).delete()
        redirect(URL('view_event', args = base.event_id))
    if (reply.comment_type==1):
        base = db.pic_comments(reply.comment_id)
        picture = base.picid
        if (picture.picture_owner_is_student_org == False) & is_admin(picture.id_of_picture_owner):
            db(db.comment_replies.id == reply.id).delete()
        redirect(URL('view_picture', args = base.picid))
    session.flash = "Invalid request"
    redirect(URL('index'))
###########################################################################################################################################################################################
#################################################################################   SEARCH   ##############################################################################################
###########################################################################################################################################################################################


#form for the search function
def search():
     return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                                 _onkeyup="ajax('eventCallback', ['keyword'], 'target');"),
                                 _onkeyup="ajax('studentOrgCallback', ['keyword'], 'target2');"),
                                 target_div=DIV(_id='target'),
                                 target_div2=DIV(_id='target2'))


#function called by search - generates list with links
def eventCallback():
    #returns links to events in relation to search input

    ### events ###
    query = db.events.name.contains(request.vars.keyword)                                #query events

    ### student organizations  ###
      #query student orgnaization names and acronym
    oquery = db(db.student_org.name.contains(request.vars.keyword) | db.student_org.acronym.contains(request.vars.keyword)).select()
    for o in oquery:
        if o:
            query = query | (db.events.student_org_id == o.id)                           #query for events by student orgadd to original query leaving out copies

    ###  students  ###

    ### tags ###
    tquery = db(db.tag.name.contains(request.vars.keyword)).select()                     #query tag
    for t in tquery:
        if t:

            ### event tags
            etquery = db(db.event_tags.tag_id == t.id).select()                          #query event_tags that contain tag
            if etquery:
                for e in etquery:
                    query = query | (db.events.id == e.event_id)                         #query events that match event_id of event_tags add to original query leaving out copies

            ### student organization tags
            soquery = db(db.student_org_tags.tag_id == t.id).select()
            if soquery:
                for s in soquery:
                    query = query | (db.events.student_org_id == s.student_org_id)

            ### student tags

    events = db(query).select(orderby=db.events.name)

    if (len(events) == 0):
        return P("No Events Found")
    else:
        links = [A(e.name, _href=URL('view_event', args=e.id)) for e in events]
        return UL(*links)

def studentOrgCallback():
    #returns links of student org pages in relation to search input

    ###  student orgs  ###
    query = db.student_org.name.contains(request.vars.keyword) | db.student_org.acronym.contains(request.vars.keyword)

    ### events ###
    equery = db(db.events.name.contains(request.vars.keyword)).select()
    for e in equery:
        if e:
            query = query | (db.student_org.id == e.student_org_id)

    ###  tags  ###
    tquery = db(db.tag.name.contains(request.vars.keyword)).select()               #get all tags which name matchins seach input
    for t in tquery:
        if t:
            ### event tags
            etquery = db(db.event_tags.tag_id == t.id).select()                    #get all event_tags that match tag
            if etquery:
                for e in etquery:
                    etquery2 = db(db.events.id == e.event_id).select()             #get all events that event_tags
                    if etquery2:
                        for i in etquery2:
                            query = query | (db.student_org.id == i.student_org_id)#get student_org that created event

            ### student organization tags
            squery = db(db.student_org_tags.tag_id == t.id).select()               #get all student_org_tags that match tag
            if squery:
                for s in squery:
                    query = query | (db.student_org.id == s.student_org_id)        #get all student_orgs that match student_org_tag

            ### student tags

    orgs = db(query).select(orderby=db.student_org.name)

    if (len(orgs) == 0):
        return P("No Orgs Found")
    else:
        links = [A(o.name, _href=URL('view_student_org', args=o.id)) for o in orgs]
        return UL(*links)


###########################################################################################################################################################################################
#####################################################################################   web2py   ##########################################################################################
###########################################################################################################################################################################################


def user():
  return dict(form=auth())


@cache.action()
def download():
  return response.download(request, db)


def call():
  return service()


@auth.requires_login()
def api():
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
