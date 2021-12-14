# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

def lambda_handler(event, context):
    if event:
        messages_to_reprocess = []
        batch_failure_response = {}
        for record in event["Records"]:
            try:
                body = record["body"]
                # process message
            except Exception as e:
                messages_to_reprocess.append({"itemIdentifier": record['messageId']})
        
        batch_failure_response["batchItemFailures"] = messages_to_reprocess
        return batch_failure_response
