# -*- coding: utf-8 -*-

@auth.requires_login()
def index():
  response.flash = T("Welcome to web2py!")
  return dict(user_id=auth.user.id)

def event():
    event = db.events(request.args(0))
    return dict(event = event)

def edit_event_pictures():                        #may be changed later to a picture viewer
    event = db.events(request.args(0))
    return dict(event = event)

def add_picture():
    db.picture.id_of_picture_owner.default = request.args(0)
    db.picture.picture_owner_is_student_org.default = False
    form = SQLFORM(db.picture)
    if form.process().accepted:
        redirect(URL('event', args=(request.args(0)) ))
    return dict(form = form)

def delete_picture():
    db(db.picture.id == request.args(1)).delete()
    redirect(URL('default','edit_event_pictures', args = (request.args(0)) ))
    return dict()

def event_edit():
    event = db.events(request.args(0))
    if event is None:
        session.flash = "Invalid request"
        redirect(URL('default', 'index'))
    form = SQLFORM(db.events, record = event)
    if form.process().accepted:
        redirect(URL('default','event', args = (request.args(0)) ))
    return dict(form = form)

def RSVP_change():
    db(db.rsvp.id == request.args(0)).update(rsvp_yes_or_maybe = request.args(1))
    redirect(URL('event', args=(request.args(2)) ))
    return dict()

def delete_post():
    db(db.comments.id == request.args(0)).delete()
    redirect(URL('event', args=(request.args(1)) ))
    return dict()

def event_post():
    db.comments.creation_time.default = request.now
    db.comments.poster_id.default = auth.user_id
    db.comments.event_id.default = request.args(0)
    form = SQLFORM(db.comments)
    if form.process().accepted:
        redirect(URL('event', args=(request.args(0)) ))
    return dict(form = form)

@auth.requires_login()
def rsvp():
  rows = db((db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id)).select()
  print rows
  return dict(user_id=auth.user.id, rows=rows)

def download():
    return response.download(request, db)







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


@auth.requires_signature()
def data():
  """
  http://..../[app]/default/data/tables
  http://..../[app]/default/data/create/[table]
  http://..../[app]/default/data/read/[table]/[id]
  http://..../[app]/default/data/update/[table]/[id]
  http://..../[app]/default/data/delete/[table]/[id]
  http://..../[app]/default/data/select/[table]
  http://..../[app]/default/data/search/[table]
  but URLs must be signed, i.e. linked with
    A('table',_href=URL('data/tables',user_signature=True))
  or with the signed load operator
    LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
  """
  return dict(form=crud())
