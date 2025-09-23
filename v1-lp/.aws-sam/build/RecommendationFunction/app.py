import json
import boto3
import os
from decimal import Decimal
import uuid
from datetime import datetime, timedelta
import re

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def calculate_dates(duration):
    """Calculate start and end dates based on duration"""
    start_date = datetime.now()
    
    # Parse duration and calculate end date
    if 'week' in duration.lower():
        weeks = int(re.findall(r'\d+', duration)[0])
        end_date = start_date + timedelta(weeks=weeks)
    elif 'month' in duration.lower():
        months = int(re.findall(r'\d+', duration)[0])
        end_date = start_date + timedelta(days=months * 30)
    elif 'hour' in duration.lower():
        hours = int(re.findall(r'\d+', duration)[0])
        # Assume 2 hours per day, 5 days per week
        days = (hours / 2) * (7/5)
        end_date = start_date + timedelta(days=int(days))
    else:
        # Default to 4 weeks if duration format is unclear
        end_date = start_date + timedelta(weeks=4)
    
    return start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y')

def get_recommendations(skill, current_level, target_level):
    # Normalize skill names
    skill_mapping = {
        'cloudazure': 'cloud-azure',
        'azure': 'cloud-azure',
        'cloudaws': 'cloud-aws',
        'aws': 'cloud-aws'
    }
    
    # Clean and normalize the skill name
    clean_skill = skill.lower().replace(' ', '').replace('-', '')
    normalized_skill = skill_mapping.get(clean_skill, skill.lower().replace(' - ', '-').replace(' ', '-'))
    
    recommendations = {
        'ai': {
            ('beginner', 'basic'): [
                {'name': 'Introduction to Artificial Intelligence', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://www.coursera.org/learn/introduction-to-ai'},
                {'name': 'AI For Everyone', 'source': 'Coursera', 'duration': '3 weeks', 'url': 'https://www.coursera.org/learn/ai-for-everyone'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'Machine Learning Course', 'source': 'Coursera', 'duration': '11 weeks', 'url': 'https://www.coursera.org/learn/machine-learning'},
                {'name': 'Deep Learning Specialization', 'source': 'Coursera', 'duration': '4 months', 'url': 'https://www.coursera.org/specializations/deep-learning'}
            ]
        },
        'python': {
            ('beginner', 'intermediate'): [
                {'name': 'Python for Everybody', 'source': 'Coursera', 'duration': '8 months', 'url': 'https://www.coursera.org/specializations/python'},
                {'name': 'Complete Python Bootcamp', 'source': 'Udemy', 'duration': '22 hours', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/'}
            ]
        },
        'java': {
            ('beginner', 'intermediate'): [
                {'name': 'Java Programming and Software Engineering', 'source': 'Coursera', 'duration': '5 months', 'url': 'https://www.coursera.org/specializations/java-programming'}
            ]
        },
        'data': {
            ('beginner', 'intermediate'): [
                {'name': 'Data Science Specialization', 'source': 'Coursera', 'duration': '11 months', 'url': 'https://www.coursera.org/specializations/jhu-data-science'}
            ]
        },
        'cloud-azure': {
            ('beginner', 'basic'): [
                {'name': 'Azure Fundamentals AZ-900', 'source': 'Microsoft Learn', 'duration': '3 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/azure-fundamentals/'},
                {'name': 'Azure Fundamentals', 'source': 'Pluralsight', 'duration': '6 hours', 'url': 'https://www.pluralsight.com/paths/azure-fundamentals'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'Azure Administrator AZ-104', 'source': 'Microsoft Learn', 'duration': '8 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/az-104-administrator-prerequisites/'},
                {'name': 'Azure Solutions Architect AZ-305', 'source': 'Microsoft Learn', 'duration': '10 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/microsoft-azure-architect-design-prerequisites/'}
            ]
        },
        'cloud-aws': {
            ('beginner', 'basic'): [
                {'name': 'AWS Cloud Practitioner', 'source': 'AWS Training', 'duration': '4 weeks', 'url': 'https://aws.amazon.com/training/learn-about/cloud-practitioner/'},
                {'name': 'AWS Fundamentals', 'source': 'Coursera', 'duration': '4 months', 'url': 'https://www.coursera.org/specializations/aws-fundamentals'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'AWS Solutions Architect Associate', 'source': 'AWS Training', 'duration': '12 weeks', 'url': 'https://aws.amazon.com/training/learn-about/architect/'},
                {'name': 'AWS Developer Associate', 'source': 'A Cloud Guru', 'duration': '8 weeks', 'url': 'https://acloudguru.com/course/aws-certified-developer-associate'}
            ]
        },
        '.net': {
            ('beginner', 'basic'): [
                {'name': '.NET Core Fundamentals', 'source': 'Microsoft Learn', 'duration': '4 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/build-dotnet-applications-csharp/'},
                {'name': 'C# Fundamentals', 'source': 'Pluralsight', 'duration': '5 hours', 'url': 'https://www.pluralsight.com/courses/csharp-fundamentals-dev'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'ASP.NET Core Web API', 'source': 'Microsoft Learn', 'duration': '6 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/create-web-api-with-aspnet-core/'},
                {'name': 'Entity Framework Core', 'source': 'Pluralsight', 'duration': '4 hours', 'url': 'https://www.pluralsight.com/courses/entity-framework-core-getting-started'}
            ]
        }
    }
    
    return recommendations.get(normalized_skill, {}).get((current_level, target_level), [
        {'name': 'General Programming Course', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://www.coursera.org/courses?query=programming'}
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
                start_date, end_date = calculate_dates(rec['duration'])
                
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
                    'StateDate': start_date,
                    'EndDate': end_date
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
                    'StateDate': start_date,
                    'EndDate': end_date
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