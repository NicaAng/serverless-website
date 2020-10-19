## load JSON file from API response
import json

def lambda_handler(event, context):
    ## Initialize variables
    for key in event:
        if 'name' in key:
            CustName = key['name']
        if 'number' in key:
            CustNum = key['number']

## move contact details to S3-JSON file (with lifecycle policies)
## move order details to DynamoDB
## add and move orders to S3-JSON file
## upload S3-JSON file
