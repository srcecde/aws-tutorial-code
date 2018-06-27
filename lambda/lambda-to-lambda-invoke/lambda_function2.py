"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
def lambda_handler(event, context):
    #this will print the payload from the source function if supplied
    print(event)
    return "Thanks"
