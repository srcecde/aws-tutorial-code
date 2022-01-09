"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import os
import logging
import jwt
from jwt import PyJWKClient

try:
    region = os.environ["AWS_REGION"]
    userPoolId = os.environ["USER_POOL_ID"]
    url = (
        f"https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json"
    )
    app_client = os.environ["APP_CLIENT_ID"]

    # fetching jwks
    jwks_client = PyJWKClient(url)
except Exception as e:
    logging.error(e)
    raise ("Unable to download JWKS")


def return_response(isAuthorized, other_params={}):
    return {"isAuthorized": isAuthorized, "context": other_params}


def lambda_handler(event, context):

    try:
        # fetching access token from event
        token = event["headers"]["authorization"]

        # check token structure
        if len(token.split(".")) != 3:
            return return_response(isAuthorized=False, other_params={})
    except Exception as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})

    try:
        # get unverified headers
        headers = jwt.get_unverified_header(token)
        # get signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        # validating exp, iat, signature, iss
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=[headers.get("alg")],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": False,
            },
        )
    except jwt.InvalidTokenError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except jwt.DecodeError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except jwt.InvalidSignatureError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except jwt.ExpiredSignatureError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except jwt.InvalidIssuerError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except jwt.InvalidIssuedAtError as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})
    except Exception as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})

    try:
        # verifying audience...use data['client_id'] if verifying an access token else data['aud']
        if app_client != data.get("client_id"):
            return return_response(isAuthorized=False, other_params={})
    except Exception as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})

    try:
        # token_use check
        if data.get("token_use") != "access":
            return return_response(isAuthorized=False, other_params={})
    except Exception as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})

    try:
        # scope check
        if "openid" not in data.get("scope").split(" "):
            return return_response(isAuthorized=False, other_params={})
    except Exception as e:
        logging.error(e)
        return return_response(isAuthorized=False, other_params={})

    return return_response(isAuthorized=True, other_params={})
