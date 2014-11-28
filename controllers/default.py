# -*- coding: utf-8 -*-

from gluon.debug import dbg
import json 

# vars for RSVP
sorting_on_column = "Time"
sort_accsending = True
  
@auth.requires_login()
def index():
  response.flash = T("Welcome to web2py!")
  return dict(user_id=auth.user.id)


# RSVP code begin   ################################################
@auth.requires_login()
def rsvp():
  ### Created by Desmond. Query and return all the events the user is RSVP'd yes or maybe to ###
  rows = db((db.student.student_name == auth.user.id) & (db.rsvp.student_id==auth.user.id) & (db.rsvp.event_id == db.events.id) & (db.student_org.id == db.events.student_org_id)).select(orderby=db.events.start_time|db.rsvp.rsvp_yes_or_maybe)
  #print rows
  column_sorting_ajax_url = URL('update_rsvp_column_sort')
  return dict(user_id=auth.user.id, rows=rows, column_sorting_ajax_url=column_sorting_ajax_url)
  
def update_rsvp_column_sort():
  ### Created by Desmond. A ajax callback function that will determine which button should be selected and the order of the data ###
  print "in update_rsvp_column_sort"
  v = request.vars.msg or ''
  if (v != ''):
    print "@@@" + str(v)
    v = json.loads(v)
    print "worked"
    print "sorting_on_column: %s" % (v['sorting_on_column'])
    print "sort_accsending: %s" % (v['sort_accsending'])
    print "selected: %s" % (v['selected'])
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
  
  print request.vars
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
  
  print cmd
  return cmd
# RSVP code end   ##################################################
  
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


    
    
    
    
    
    
    
# BOILERPLATE is below....    
    
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
