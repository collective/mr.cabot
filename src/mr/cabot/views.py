import pyramid.httpexceptions as exc
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
import transaction

from mr.cabot.models import (
    DBSession,
    Contributor,
    Identity,
    Activity
    )

BADGES = [
    {'name': 'beginner_commit',
     'commit': 5},
    {'name': 'expert_commit',
     'commit': 100},
    {'name': 'beginner_question',
     'question': 1},
    {'name': 'expert_question',
     'question': 10},
     
    {'name': 'beginner_answer',
     'answer': 10},
    {'name': 'expert_answer',
     'answer': 100},
]

@view_config(route_name='view_user', renderer='templates/view.pt')
def view_user(request):
    contributor = request.matchdict['user']
    contributor = DBSession.query(Contributor).get(contributor)

    awards = []
    commit = 0
    question = 0
    answer = 0
    issue = 0
    for identity in contributor.identities:
        if 'so' in identity.uri:
            import pdb; pdb.set_trace( )
        issue += DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='issue').count()
        commit += DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='commit').count()
        question += DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='question').count()
        answer += DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='answer').count()
    for badge in BADGES:
        if 'commit' in badge:
            if commit > badge['commit']:
                awards.append(badge['name'])
        if 'question' in badge:
            if question > badge['question']:
                awards.append(badge['name'])
        if 'answer' in badge:
            if answer > badge['answer']:
                awards.append(badge['name'])
    return {'awards': awards, 'num_commits':commit, 'num_answers':answer, 'num_questions':question, 'num_issues':issue}

@view_config(route_name='edit_user', renderer='templates/edit.pt')
def edit_user(request):
    contributor = request.matchdict['user']
    contributor = DBSession.query(Contributor).get(contributor)
    identities = DBSession.query(Identity).filter(Identity.contributor_id==None).order_by(Identity.uri)
    return {'contributor': contributor, "available":identities}

@view_config(route_name='edit_user', request_method="POST", renderer='templates/edit.pt')
def edit_user_do(request):
    contributor = request.matchdict['user']
    contributor = DBSession.query(Contributor).get(contributor)

    new_ident = DBSession.query(Identity).filter(Identity.uri==request.POST['to_add']).one()
    new_ident.contributor_id = contributor.id
    DBSession.add(new_ident)
    return edit_user(request)

@view_config(route_name='new_user')
def new_user(request):
    contrib = Contributor()
    DBSession.add(contrib)
    DBSession.flush()
    return exc.HTTPFound(request.route_url("edit_user", user=contrib.id))
    