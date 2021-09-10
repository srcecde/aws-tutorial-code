"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import boto3
from pprint import pprint


def lambda_handler(event, context):

    comprehend = boto3.client("comprehend")
    paragraph = "Hey, welcome to this tutorial. How are you doing readers and viewers?"

    # Extracting Grammer syntax
    syntax_response = comprehend.detect_syntax(Text=paragraph, LanguageCode="en")
    pprint(syntax_response)

    return "Thanks"
