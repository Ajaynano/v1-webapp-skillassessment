import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # CORS headers for all responses
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,Origin,Referer',
        'Access-Control-Max-Age': '86400'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers
        }
    
    try:
        print(f"Raw event: {json.dumps(event)}")
        
        # Handle both direct Lambda invocation and API Gateway formats
        if 'body' in event:
            # API Gateway format - body is a JSON string
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct Lambda invocation - event is the body
            body = event
        
        print(f"Parsed body: {json.dumps(body)}")
        
        # Check if operation is in the body
        operation = body.get('operation')
        
        print(f"Processing operation: {operation}")
        
        if operation == 'list':
            response = table.scan()
            items = response['Items']
            print(f"List operation returning {len(items)} items: {json.dumps(items, default=decimal_default)}")
            
            # Transform data to ensure consistent field names for frontend
            transformed_items = []
            for item in items:
                transformed_items.append({
                    'SkillAssessmentId': item.get('SkillAssessmentId', ''),
                    'Employee': item.get('Employee', ''),
                    'Skill': item.get('Skill', ''),
                    'Current': item.get('Current', ''),
                    'Target': item.get('Target', '')
                })
            
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Skill-Assessments': transformed_items}, default=decimal_default)}
        
        elif operation == 'read':
            response = table.get_item(Key={'SkillAssessmentId': body['SkillAssessmentId']})
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps(response.get('Item', {}), default=decimal_default)}
        
        elif operation == 'create':
            import uuid
            skill_id = body.get('SkillAssessmentId', str(uuid.uuid4()))
            table.put_item(Item={
                'SkillAssessmentId': skill_id,
                'Employee': body['Employee'],
                'Skill': body['Skill'],
                'Current': body['Current'],
                'Target': body['Target']
            })
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Created', 'SkillAssessmentId': skill_id})}
        
        elif operation == 'update':
            table.put_item(Item={
                'SkillAssessmentId': body['SkillAssessmentId'],
                'Employee': body['Employee'],
                'Skill': body['Skill'],
                'Current': body['Current'],
                'Target': body['Target']
            })
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Updated'})}
        
        elif operation == 'delete':
            table.delete_item(Key={'SkillAssessmentId': body['SkillAssessmentId']})
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Deleted'})}
        
        else:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'error': 'Missing operation'})}
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'error': str(e)})}