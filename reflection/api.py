import json

import requests
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest
from keen.client import KeenClient

from settings import (
    KEEN_PROJECT_ID,
    KEEN_WRITE_KEY,
    KEEN_READ_KEY,
    KEEN_MASTER_KEY,
    FB_ACCESS_TOKEN
)
from models import UserToken


keen = KeenClient(
    project_id=KEEN_PROJECT_ID,
    write_key=KEEN_WRITE_KEY,
    read_key=KEEN_READ_KEY,
    master_key=KEEN_MASTER_KEY
)

ACCEPTED_FEELS = frozenset({'safe', 'unsafe', 'satisfied', 'unsatisfied', 'connected', 'lonely'})


def authenticate_fb_user(token_to_inspect):
    formatted_url = 'https://graph.facebook.com/debug_token'
    return requests.get(
        formatted_url, params={'input_token': token_to_inspect, 'access_token': FB_ACCESS_TOKEN}
    )


def get_user_from_access_token(access_token):
    # search the database for the user associated with the access_token
    try:
        user_token = UserToken.objects.get(fb_access_token=access_token)
    except:
        # if the access_token isn't associated with any user in the database, check if it's valid
        valid_token = authenticate_fb_user(access_token)
        # if the token is valid, search for the user by the user_id facebook returns
        if valid_token:
            user_token = UserToken.objects.get(fb_user_id=valid_token['user_id'])
            # if the user_id returns a valid user, update the corresponding token
            if user_token:
                user_token = UserToken.objects.update(fb_access_token=access_token)
            # if the user_id doesn't exist, create a new user with the user_id and access_token
            else:
                user_token = UserToken.objects.create_user(
                    fb_user_id=valid_token['user_id'], fb_access_token=access_token
                )
    return user_token.user


def record_event(request):
    data = json.loads(request.body)
    try:
        access_token = data['access_token']
        feeling = data['feeling']
    except KeyError:
        raise HttpResponseBadRequest

    # if the feeling is not in the accepted feels list, something went wrong. sound the alarm.
    if feeling not in ACCEPTED_FEELS:
        raise Exception('Our emotional vocab is limited. %s is not a recognized feeling :(' % feeling)

    # check that the request has a valid access token
    user = get_user_from_access_token(access_token)
    response = keen.add_event('reflections', {'user_id': user.id, 'rating': feeling})
    return JsonResponse(response)
