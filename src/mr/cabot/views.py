from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from mr.cabot.models import (
    DBSession,
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

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    awards = {}
    for badge in BADGES:
        awards[badge['name']] = []
    uri = request.GET.get('uri')
    for identity in DBSession.query(Identity).filter(Identity.uri == uri):
        for badge in BADGES:
            if 'commit' in badge:
                if DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='commit').count() > badge['commit']:
                    awards[badge['name']].append(identity)
            if 'question' in badge:
                if DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='question').count() > badge['question']:
                    awards[badge['name']].append(identity)
            if 'answer' in badge:
                if DBSession.query(Activity).filter(Activity.identity_id==identity.id, Activity.type=='answer').count() > badge['answer']:
                    awards[badge['name']].append(identity)
    return {'awards': awards, 'project': 'mr.cabot'}

