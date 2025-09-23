import json
import boto3
import os
from decimal import Decimal
import uuid

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_recommendations(skill, current_level, target_level):
    recommendations = {
        'ai': {
            ('beginner', 'basic'): [
                {'name': 'Introduction to Artificial Intelligence', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/learn/introduction-to-ai'},
                {'name': 'AI Fundamentals', 'source': 'edX', 'duration': '3 weeks', 'url': 'https://edx.org/course/artificial-intelligence'}
            ]
        },
        'python': {
            ('beginner', 'intermediate'): [
                {'name': 'Python Intermediate Programming', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/python-intermediate'}
            ]
        },
        'java': {
            ('beginner', 'intermediate'): [
                {'name': 'Java Programming Fundamentals', 'source': 'Coursera', 'duration': '5 weeks', 'url': 'https://coursera.org/java-fundamentals'}
            ]
        }
    }
    
    return recommendations.get(skill, {}).get((current_level, target_level), [
        {'name': 'General Programming Course', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/programming'}
    ])

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # CORS headers for all responses
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,Origin,Referer',
        'Access-Control-Max-Age': '86400',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers
        }
    
    try:
        print(f"Raw event: {json.dumps(event)}")
        
        # Handle GET request for listing learning paths
        if event.get('httpMethod') == 'GET':
            response = table.scan()
            items = response['Items']
            print(f"GET request returning {len(items)} items")
            print(f"Items found: {json.dumps(items, default=decimal_default)}")
            
            # Transform data to ensure consistent field names for frontend
            transformed_items = []
            for item in items:
                transformed_items.append({
                    'LearningPathId': item.get('LearningPathId', ''),
                    'Employee': item.get('Employee', ''),
                    'Skill': item.get('Skill', ''),
                    'Level': item.get('Level', ''),
                    'Name': item.get('Name', ''),
                    'Source': item.get('Source', ''),
                    'Duration': item.get('Duration', ''),
                    'Url': item.get('Url', ''),
                    'Completed': item.get('Completed', False),
                    'StateDate': item.get('StateDate', ''),
                    'EndDate': item.get('EndDate', '')
                })
            
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Learning-Paths': transformed_items}, default=decimal_default)}
        
        # Handle both direct Lambda invocation and API Gateway formats
        if 'body' in event:
            # API Gateway format - body is a JSON string
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct Lambda invocation - event is the body
            body = event
        
        print(f"Parsed body: {json.dumps(body)}")
        
        # Check if this is a skill assessment request (has SkillAssessmentId)
        if 'SkillAssessmentId' in body:
            # Generate learning paths based on skill assessment
            skill = body.get('Skill', '')
            current_level = body.get('Current', '')
            target_level = body.get('Target', '')
            employee = body.get('Employee', '')
            
            # Get recommendations and create learning paths
            recommendations = get_recommendations(skill.lower(), current_level.lower(), target_level.lower())
            created_paths = []
            
            for rec in recommendations:
                learning_path_id = str(uuid.uuid4())
                item = {
                    'LearningPathId': learning_path_id,
                    'Employee': employee,
                    'Skill': skill,
                    'Level': target_level,
                    'Name': rec['name'],
                    'Source': rec['source'],
                    'Duration': rec['duration'],
                    'Url': rec['url'],
                    'Completed': False,
                    'StateDate': '',
                    'EndDate': ''
                }
                print(f"Saving item to DynamoDB: {json.dumps(item)}")
                table.put_item(Item=item)
                print(f"Successfully saved item with ID: {learning_path_id}")
                
                created_paths.append({
                    'LearningPathId': learning_path_id,
                    'Employee': employee,
                    'Skill': skill,
                    'Level': target_level,
                    'Name': rec['name'],
                    'Source': rec['source'],
                    'Duration': rec['duration'],
                    'Url': rec['url'],
                    'Completed': False,
                    'StateDate': '',
                    'EndDate': ''
                })
            
            print(f"Created {len(created_paths)} learning paths from skill assessment")
            
            # Verify items were saved by doing a quick scan
            verify_response = table.scan()
            print(f"Total items in table after creation: {len(verify_response['Items'])}")
            
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Learning-Paths': created_paths}, default=decimal_default)}
        
        # Check if operation is in the body
        operation = body.get('operation')
        
        print(f"Processing operation: {operation}")
        
        if operation == 'list':
            response = table.scan()
            items = response['Items']
            print(f"List operation returning {len(items)} items")
            print(f"Items found: {json.dumps(items, default=decimal_default)}")
            
            # Transform data to ensure consistent field names for frontend
            transformed_items = []
            for item in items:
                transformed_items.append({
                    'LearningPathId': item.get('LearningPathId', ''),
                    'Employee': item.get('Employee', ''),
                    'Skill': item.get('Skill', ''),
                    'Level': item.get('Level', ''),
                    'Name': item.get('Name', ''),
                    'Source': item.get('Source', ''),
                    'Duration': item.get('Duration', ''),
                    'Url': item.get('Url', ''),
                    'Completed': item.get('Completed', False),
                    'StateDate': item.get('StateDate', ''),
                    'EndDate': item.get('EndDate', '')
                })
            
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Learning-Paths': transformed_items}, default=decimal_default)}
        
        elif operation == 'read':
            response = table.get_item(Key={'LearningPathId': body['LearningPathId']})
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps(response.get('Item', {}), default=decimal_default)}
        
        elif operation == 'create':
            learning_path_id = body.get('LearningPathId', str(uuid.uuid4()))
            table.put_item(Item={
                'LearningPathId': learning_path_id,
                'Employee': body['Employee'],
                'Skill': body['Skill'],
                'Level': body['Level'],
                'Name': body['Name'],
                'Source': body['Source'],
                'Duration': body['Duration'],
                'Url': body['Url'],
                'Completed': body.get('Completed', False),
                'StateDate': body.get('StateDate', ''),
                'EndDate': body.get('EndDate', '')
            })
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Created', 'LearningPathId': learning_path_id})}
        
        elif operation == 'update':
            table.put_item(Item={
                'LearningPathId': body['LearningPathId'],
                'Employee': body['Employee'],
                'Skill': body['Skill'],
                'Level': body['Level'],
                'Name': body['Name'],
                'Source': body['Source'],
                'Duration': body['Duration'],
                'Url': body['Url'],
                'Completed': body.get('Completed', False),
                'StateDate': body.get('StateDate', ''),
                'EndDate': body.get('EndDate', '')
            })
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Updated'})}
        
        elif operation == 'delete':
            table.delete_item(Key={'LearningPathId': body['LearningPathId']})
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Deleted'})}
        
        else:
            return {'statusCode': 400, 'headers': cors_headers, 'body': json.dumps({'error': 'Missing operation'})}
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        return {'statusCode': 500, 'headers': cors_headers, 'body': json.dumps({'error': str(e)})}