# -*- coding: utf-8 -*-

from gluon.debug import dbg
import json 
from operator import itemgetter



###########################################################################################################################################################################################
#################################################################################   VIEW   ################################################################################################
###########################################################################################################################################################################################


@auth.requires_login()
def index():
  response.flash = T("Welcome to web2py!")
  return dict(user_id=auth.user.id)


#This is off of chpater 3 in the manual
def show():
    #shows an event page
    this_event = db.events(request.args(0, cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.events).process()
    return dict(events=this_event, form=form)


#This page lets you view the student org profiles.
@auth.requires_login()
def view_student_org():
    student_orgs = db.student_org(request.args[0]) or redirect(URL('index'))
    return dict(student_orgs=student_orgs, user_id = auth.user_id)


###########################################################################################################################################################################################
#################################################################################   RVSP   ################################################################################################
###########################################################################################################################################################################################

#checks if a user is an admin of the given event
@auth.requires_login()
def is_admin(event_id):
    event = db.events(event_id)
    student = db(db.student.student_name == auth.user.id).select().first()
    if db( (db.admin_pool.student_org_id == event.student_org_id) & (db.admin_pool.student_id == student) ).select():
        return True
    else:
        return False

#views an event
def view_event():
    event = db.events(request.args(0))
    return dict(event = event)

#allows an admin to delete and add pictures
@auth.requires_login()
def edit_event_pictures():
    if is_admin(request.args(0)):
        event = db.events(request.args(0))
        return dict(event = event)
    else:
        redirect(URL('view_event', args=[ request.args(0) ]))

#shows the picture and its comments
def view_picture():
    pic = db.picture(request.args(0))
    if pic is None:
        session.flash = "Invalid request"
        redirect(URL('default', 'index'))
    return dict(pic = pic)

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

#deletes a picture from an event
@auth.requires_login()
def delete_event_picture():
    picture = db.picture(request.args(1))
    if ((picture.picture_owner_is_student_org == False) & is_admin(db.events(picture.id_of_picture_owner).id)):
        db(db.picture.id == request.args(1)).delete()
    redirect(URL('default','edit_event_pictures', args = (request.args(0)) ))
    return dict()

#deletes an entire event
@auth.requires_login()
def delete_event():
    if is_admin(request.args(0)):
        db(db.events.id == request.args(0)).delete()
    redirect(URL('default','index') )
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

#RSVPs a user to an event
@auth.requires_login()
def RSVP_action():
    studnt = db.student(request.args(1))
    if (studnt.student_name.id == auth.user.id):
        db.rsvp.insert(event_id = request.args(0),
                       student_id =  request.args(1),
                       rsvp_yes_or_maybe = request.args(2))
    redirect(URL('default', 'view_event', args = [request.args(0)]) )
    return dict()

#alters an RSVP from yes to maybe or vice versa
@auth.requires_login()
def RSVP_change():
    student = db.rsvp(request.args(0)).student_id
    if (student.student_name.id == auth.user.id):
        db(db.rsvp.id == request.args(0)).update(rsvp_yes_or_maybe = request.args(1))
    redirect(URL('view_event', args=[request.args(2)] ))
    return dict()

#removes an RSVP from the database
@auth.requires_login()
def unRSVP_action():
    student = db.rsvp(request.args(0)).student_id
    if (student.student_name.id == auth.user.id):
        db(db.rsvp.id == request.args(0)).delete()
    redirect(URL('view_event', args=[request.args(1)] ))
    return dict()

#allows an admin to delete a post from an event
@auth.requires_login()
def delete_post():
    if is_admin(db.comments(request.args(1)).event_id):
        db(db.comments.id == request.args(1)).delete()
    redirect(URL('view_event', args=(request.args(0)) ))
    return dict()

#allows an admin to delete a post from a picture
@auth.requires_login()
def delete_pic_post():
    picture = db.pic_comments(request.args(1)).picid
    if (picture.picture_owner_is_student_org == False) & is_admin(picture.id_of_picture_owner):
        db(db.pic_comments.id == request.args(1)).delete()
    redirect(URL('view_picture', args=(request.args(0)) ))
    return dict()

#@auth.requires_login()
#def delete_reply_post():
#    if 
#    return dict()

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
#################################################################################   SEARCH   ##############################################################################################
###########################################################################################################################################################################################


#This is off of chapter 3 in the manual
def search():
     return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                                 _onkeyup="ajax('callback', ['keyword'], 'target');")),
                                 target_div=DIV(_id='target'))


#This is off of chapter 3 in the manual
def callback():
    #returns a <url> of links to events
    query = db.events.name.contains(request.vars.keyword)
    events = db(query).select(orderby=db.events.name)
    links = [A(e.name, _href=URL('show',args=e.id)) for e in events]
    return UL(*links)


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
    #if auth.user_id != student_orgs.admins:
    #    session.flash = T("Authorization error")
    #    redirect(URL('index'))
    form = SQLFORM.factory()
    if form.process().accepted:
        db(db.student_org.id == request.args[0]).delete()
        session.flash = T(student_orgs.name + ' was deleted')
        redirect(URL('index'))
    return dict(form=form, student_orgs=student_orgs)#, user=auth.user)
#This is off of chpater 3 in the manual
def show():
    #shows an event page
    this_event = db.events(request.args(0, cast=int)) or redirect(URL('index'))
    #dbg.set_trace() ####BREAKPOINT###
    form = SQLFORM(db.events).process()
    #dbg.set_trace() ####BREAKPOINT###
    return dict(events=this_event, form=form)


#This is off of chapter 3 in the manual
def search():
     return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                                 _onkeyup="ajax('callback', ['keyword'], 'target');")),
                                 target_div=DIV(_id='target'))

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
    return dict(form=form, student_orgs=student_orgs)#, user=auth.user)

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
        
#This page lets you view the student org profiles.
@auth.requires_login()
def view_student_org():
    student_orgs = db.student_org(request.args[0]) or redirect(URL('index'))
    return dict(student_orgs=student_orgs, user_id = auth.user_id)

@auth.requires_login()
def is_student_org_admin(student_org_id):
    student_orgs = db.student_org(student_org_id)
    student = db(db.student.student_name == auth.user.id).select().first()
    if db( (db.admin_pool.student_org_id == student_orgs.id) & (db.admin_pool.student_id == student) ).select():
        return True
    else:
        return False

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
