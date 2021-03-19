"""Register user"""
import json
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseServerError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login_user(request):
    '''Handles the authentication of a user

    Method arguments:
      request -- The full HTTP request object
    '''

    body = request.body.decode('utf-8')
    req_body = json.loads(body)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        name = req_body['username']
        pass_word = req_body['password']
        authenticated_user = authenticate(username=name, password=pass_word)

        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            data = json.dumps({"valid": True, "token": token.key, "id": authenticated_user.id})
            return HttpResponse(data, content_type='application/json', status=status.HTTP_202_ACCEPTED )

        else:
            # Bad login details were provided. So we can't log the user in.
            data = json.dumps({"valid": False})
            return HttpResponse(data, content_type='application/json')

    return HttpResponseNotAllowed(permitted_methods=['POST'])


@csrf_exempt
def register_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    req_body = json.loads(request.body.decode())

    user = User.objects.create_user(
        first_name=req_body['firstName'],
        last_name=req_body['lastName'],
        username=req_body['username'],
        email=req_body['email'],
        password=req_body['password']
    )


    user.save()

    token = Token.objects.create(user=user)

    data = json.dumps({"token": token.key})
    return HttpResponse(data, content_type='application/json', status=status.HTTP_201_CREATED)