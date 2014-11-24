# -*- coding: utf-8 -*-

from gluon.debug import dbg

@auth.requires_login()
def index():
  response.flash = T("Welcome to web2py!")
  return dict(user_id=auth.user.id)

@auth.requires_login()
def is_admin(event_id):
    event = db.events(event_id)
    student = db(db.student.student_name == auth.user.id).select().first()
    if db( (db.admin_pool.student_org_id == event.student_org_id) & (db.admin_pool.student_id == student) ).select():
        return True
    else:
        return False

def event():
    event = db.events(request.args(0))
    return dict(event = event)

@auth.requires_login()
def edit_event_pictures():
    if is_admin(request.args(0)):
        event = db.events(request.args(0))
        return dict(event = event)
    else:
        redirect(URL('event', args=[ request.args(0) ]))

def view_picture():
    pic = db.picture(request.args(0))
    if pic is None:
        session.flash = "Invalid request"
        redirect(URL('default', 'index'))
    return dict(pic = pic)

@auth.requires_login()
def add_picture():
    if is_admin(request.args(0)):
        db.picture.id_of_picture_owner.default = request.args(0)
        db.picture.picture_owner_is_student_org.default = False
        form = SQLFORM(db.picture)
        if form.process().accepted:
            redirect(URL('event', args=(request.args(0)) ))
        return dict(form = form)
    else:
        redirect(URL('event', args=(request.args(0))))

@auth.requires_login()
def delete_picture():
    picture = db.picture(request.args(1))
    if (picture.picture_owner_is_student_org == False) & is_admin(db.events(picture.id_of_picture_owner).id):
        db(db.picture.id == request.args(1)).delete()
    redirect(URL('default','edit_event_pictures', args = (request.args(0)) ))
    return dict()

@auth.requires_login()
def delete_event():
    if is_admin(request.args(0)):
        db(db.events.id == request.args(0)).delete()
    redirect(URL('default','index') )
    return dict()

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
        redirect(URL('default','event', args = [request.args(0)] ))
    return dict(form = form)

@auth.requires_login()
def RSVP_action():
    studnt = db.student(request.args(1))
    if (studnt.student_name.id == auth.user.id):
        db.rsvp.insert(event_id = request.args(0),
                       student_id =  request.args(1),
                       rsvp_yes_or_maybe = request.args(2))
    redirect(URL('default', 'event', args = [request.args(0)]) )
    return dict()

@auth.requires_login()
def RSVP_change():
    student = db.rsvp(request.args(0)).student_id
    if (student.student_name.id == auth.user.id):
        db(db.rsvp.id == request.args(0)).update(rsvp_yes_or_maybe = request.args(1))
    redirect(URL('event', args=[request.args(2)] ))
    return dict()

@auth.requires_login()
def unRSVP_action():
    student = db.rsvp(request.args(0)).student_id
    if (student.student_name.id == auth.user.id):
        db(db.rsvp.id == request.args(0)).delete()
    redirect(URL('event', args=[request.args(1)] ))
    return dict()

@auth.requires_login()
def delete_post():
    if is_admin(db.comments(request.args(1)).event_id):
        db(db.comments.id == request.args(1)).delete()
    redirect(URL('event', args=(request.args(0)) ))
    return dict()

@auth.requires_login()
def delete_pic_post():
    picture = db.pic_comments(request.args(1)).picid
    if (picture.picture_owner_is_student_org == False) & is_admin(picture.id_of_picture_owner):
        db(db.pic_comments.id == request.args(1)).delete()
    redirect(URL('view_picture', args=(request.args(0)) ))
    return dict()

@auth.requires_login()
def event_post():
    db.comments.creation_time.default = request.now
    db.comments.poster_id.default = auth.user_id
    db.comments.event_id.default = request.args(0)
    db.comments.comment_type.default = request.args(2)
    form = SQLFORM(db.comments)
    if form.process().accepted:
            redirect(URL('event', args=(request.args(0)) ))
    return dict(form = form)

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
def rsvp():
  ### Created by Desmond. Query and return all the events the user is RSVP'd yes or maybe to ###
  rows = db((db.student.student_name == auth.user.id) & (db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id) & (db.student_org.id == db.events.student_org_id)).select()
  #print rows
  return dict(user_id=auth.user.id, rows=rows)


def download():
    return response.download(request, db)

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


#This is off of chapter 3 in the manual
def callback():
    #returns a <url> of links to events
    query = db.events.name.contains(request.vars.keyword)
    events = db(query).select(orderby=db.events.name)
    links = [A(e.name, _href=URL('show',args=e.id)) for e in events]
    return UL(*links)


def user():
  """
  exposes:
  http://..../[app]/default/user/login
  http://..../[app]/default/user/logout
  http://..../[app]/default/user/register
  http://..../[app]/default/user/profile
  http://..../[app]/default/user/retrieve_password
  http://..../[app]/default/user/change_password
  http://..../[app]/default/user/manage_users (requires membership in
  use @auth.requires_login()
      @auth.requires_membership('group name')
      @auth.requires_permission('read','table name',record_id)
  to decorate functions that need access control
  """
  return dict(form=auth())


@cache.action()
def download():
  """
  allows downloading of uploaded files
  http://..../[app]/default/download/[filename]
  """
  return response.download(request, db)


def call():
  """
  exposes services. for example:
  http://..../[app]/default/call/jsonrpc
  decorate with @services.jsonrpc the functions to expose
  supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
  """
  return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
