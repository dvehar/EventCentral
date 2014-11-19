# -*- coding: utf-8 -*-

from gluon.debug import dbg


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


@auth.requires_login()
def rsvp():
  ### Created by Desmond. Query and return all the events the user is RSVP'd yes or maybe to ###
  rows = db((db.student.student_name == auth.user.id) & (db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id) & (db.student_org.id == db.events.student_org_id)).select()
  #print rows
  return dict(user_id=auth.user.id, rows=rows)


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


#Temporary admin page.
@auth.requires_login()
def admin_page():
    student_org = db(db.student_org.admins==auth.user_id).select(db.student_org.ALL, orderby=~db.student_org.join_date)
    return dict(student_org=student_org,user_id=auth.user_id)


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
