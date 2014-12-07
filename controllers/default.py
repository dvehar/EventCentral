# -*- coding: utf-8 -*-

from gluon.debug import dbg


######################################################################
##############################   VIEW   ##############################
######################################################################


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
def view_event():
    this_event = db.events(request.args(0, cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.events).process()
    return dict(events=this_event, form=form)


######################################################################
##############################   ADMIN   #############################
######################################################################


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
  curr_org_info = curr_org_info[0]['student_org']
  curr_id = request.args(0)
  org_acronyms_ids=[] #acronyms of all the orgs user is an admin of (used for buttons)   #[(row['student_org'].acronym,row['student_org'].id)]
  # get all the orgs the user is an admin of:
  rows = db((db.admin_pool.student_id == db.student.student_name == auth.user.id) & (db.admin_pool.student_org_id == db.student_org.id)).select(db.student_org.acronym,db.student_org.id,orderby=db.student_org.acronym)
  for idx in range(len(rows)):
    #print idx
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


######################################################################
##############################   RVSP   ##############################
######################################################################


@auth.requires_login()
def rsvp():
  ### Created by Desmond. Query and return all the events the user is RSVP'd yes or maybe to ###
  rows = db((db.student.student_name == auth.user.id) & (db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id) & (db.student_org.id == db.events.student_org_id)).select(orderby=db.events.start_time|db.rsvp.rsvp_yes_or_maybe)
  #print rows
  return dict(user_id=auth.user.id, rows=rows)


######################################################################
#############################   SEARCH   #############################
######################################################################


#form for the search function
def search():
     return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                                 _onkeyup="ajax('eventCallback', ['keyword'], 'target');")),
                                 target_div=DIV(_id='target'))


def view_all_events():
    events = db(db.events.id >0).select(orderby=db.events.name)
    links = [A(e.name, _href=URL('view_event',args=e.id)) for e in events]
    return dict(target_div=UL(*links))


#function called by search, calls other query functions and generates list with links
#currently only displays event links, working on getting
def eventCallback():
    #returns links to events in relation to search input

    ### events ###
    query = db.events.name.contains(request.vars.keyword)                                #query events

    ### student organizations  ###
      #query student orgnaization names and acronym
    oquery = db(db.student_org.name.contains(request.vars.keyword) | db.student_org.acronym.contains(request.vars.keyword)).select()
    for o in oquery:
        if o:
            oequery = db.events.student_org_id == o.id                                   #query for events by student org
            query = query | oequery                                                      #add to original query leaving out copies

    ###  students  ###

    ### tags ###
    tquery = db(db.tag.name.contains(request.vars.keyword)).select()                     #query tag
    for t in tquery:
        if t:

            ### event tags
            etquery = db(db.event_tags.tag_id == t.id).select()                          #query event_tags that contain tag
            if etquery:
                for e in etquery:
                    etquery2 = db.events.id == e.event_id                                #query events that match event_id of event_tags
                    query = query | etquery2                                             #add to original query leaving out copies

            ### student organization tags
            soquery = db(db.student_org_tags.tag_id == t.id).select()
            if soquery:
                for s in soquery:
                    soquery2 = db.events.student_org_id == s.student_org_id
                    query = query | soquery2

            ### student tags

    events = db(query).select(orderby=db.events.name)
    links = [A(e.name, _href=URL('view_event', args=e.id)) for e in events]
    return UL(*links)


def studentOrgCallback():
    #returns links of student org pages in relation to search input

    ###  student orgs  ###
    query = db.student_orgs.name.contains(request.vars.keyword)

    ###  tags  ###
    tquery = db(db.tag.name.contains(request.vars.keyword)).select()               #get all tags which name matchins seach input
    for t in tquery:
        if t:

            ### event tags
            etquery = db(db.event_tags.tag_id == t.id).select()                    #get all event_tags that match tag
            if etquery:
                for e in etquery:
                    etquery2 = db.events.id == e.event_id                          #get all events that event_tags
                    if equery2:
                        for i in equery2:
                            etquery3 = db.student_org == i.student_ort_id          #get student_org that created event
                            query = query | etquery

            ### student organization tags
            squery = db(db.student_org_tags.tag_id == t.id).select()               #get all student_org_tags that match tag
            if squery:
                for s in squery:
                    squery2 = db.student_org == s.student_org.id                   #get all student_orgs that match student_org_tag
                    query = query | squery2

            ### student tags

    orgs = db(query).select(orderby=db.student_orgs.name)
    links = [A(o.name, _href=URL('view_student_org', args.o.id)) for o in orgs]
    return dict()


######################################################################
#############################   WEB2PY   #############################
######################################################################


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
