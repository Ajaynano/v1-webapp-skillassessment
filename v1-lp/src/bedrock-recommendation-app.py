import json
import boto3
import uuid
import os
from datetime import datetime, timedelta
from decimal import Decimal
from botocore.exceptions import ClientError
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

def lambda_handler(event, context):
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
        
        # Handle DELETE request
        if event.get('httpMethod') == 'DELETE':
            path_params = event.get('pathParameters') or {}
            query_params = event.get('queryStringParameters') or {}
            recommendation_id = path_params.get('id') or query_params.get('id') or query_params.get('RecommendationId')
            
            if not recommendation_id:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Missing RecommendationId'})
                }
            
            try:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
                table.delete_item(Key={'RecommendationId': recommendation_id})
                return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Deleted'})}
            except Exception as delete_error:
                print(f"Delete error: {str(delete_error)}")
                return {
                    'statusCode': 500,
                    'headers': cors_headers,
                    'body': json.dumps({'error': f'Delete failed: {str(delete_error)}'})
                }
        
        # Handle GET request for listing recommendations
        if event.get('httpMethod') == 'GET':
            try:
                dynamodb = boto3.resource('dynamodb')
                table_name = os.environ.get('RECOMMENDATIONS_TABLE')
                if not table_name:
                    return {
                        'statusCode': 500,
                        'headers': cors_headers,
                        'body': json.dumps({'error': 'RECOMMENDATIONS_TABLE environment variable not set'})
                    }
                table = dynamodb.Table(table_name)
                response = table.scan()
                items = response['Items']
                
                # Transform to Learning-Paths format with consistent IDs
                learning_paths = []
                for item in items:
                    for rec in item.get('Recommendations', []):
                        # Generate consistent ID based on content for delete operations
                        consistent_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{item.get('Employee', '')}-{rec.get('name', '')}-{rec.get('source', '')}"))
                        # Calculate dates based on duration
                        start_date, end_date = calculate_dates(rec.get('duration', '4 weeks'))
                        learning_paths.append({
                            'LearningPathId': consistent_id,
                            'Employee': item.get('Employee', ''),
                            'Skill': item.get('Skill', ''),
                            'Level': item.get('TargetLevel', ''),
                            'Name': rec.get('name', ''),
                            'Source': rec.get('source', ''),
                            'Duration': rec.get('duration', ''),
                            'Url': rec.get('url', ''),
                            'Completed': False,
                            'StateDate': start_date,
                            'EndDate': end_date
                        })
                
                print(f"GET request returning {len(learning_paths)} learning paths")
                return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Learning-Paths': learning_paths}, default=decimal_default)}
            except Exception as get_error:
                print(f"GET error: {str(get_error)}")
                return {
                    'statusCode': 500,
                    'headers': cors_headers,
                    'body': json.dumps({'error': f'GET failed: {str(get_error)}'})
                }
        
        # Handle both direct Lambda invocation and API Gateway formats
        if 'body' in event:
            if event['body'] is None or event['body'] == '':
                body = {}
            else:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event if event else {}
        
        print(f"Parsed body: {json.dumps(body)}")
        
        # Check if operation is in the body
        operation = body.get('operation')
        
        if operation == 'list':
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
            response = table.scan()
            items = response['Items']
            
            # Transform to Learning-Paths format with consistent IDs
            learning_paths = []
            for item in items:
                for rec in item.get('Recommendations', []):
                    # Generate consistent ID based on content for delete operations
                    consistent_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{item.get('Employee', '')}-{rec.get('name', '')}-{rec.get('source', '')}"))
                    # Calculate dates based on duration
                    start_date, end_date = calculate_dates(rec.get('duration', '4 weeks'))
                    learning_paths.append({
                        'LearningPathId': consistent_id,
                        'Employee': item.get('Employee', ''),
                        'Skill': item.get('Skill', ''),
                        'Level': item.get('TargetLevel', ''),
                        'Name': rec.get('name', ''),
                        'Source': rec.get('source', ''),
                        'Duration': rec.get('duration', ''),
                        'Url': rec.get('url', ''),
                        'Completed': False,
                        'StateDate': start_date,
                        'EndDate': end_date
                    })
            
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'Learning-Paths': learning_paths}, default=decimal_default)}
        
        elif operation == 'read':
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
            response = table.get_item(Key={'RecommendationId': body['RecommendationId']})
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps(response.get('Item', {}), default=decimal_default)}
        
        elif operation == 'delete':
            try:
                learning_path_id = body.get('LearningPathId') or body.get('RecommendationId')
                if not learning_path_id:
                    return {
                        'statusCode': 400,
                        'headers': cors_headers,
                        'body': json.dumps({'error': 'Missing LearningPathId or RecommendationId'})
                    }
                
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
                
                # Scan all recommendations to find the one that matches the LearningPathId
                response = table.scan()
                deleted = False
                
                for item in response['Items']:
                    for rec in item.get('Recommendations', []):
                        # Generate the same consistent ID used in GET/list operations
                        consistent_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{item.get('Employee', '')}-{rec.get('name', '')}-{rec.get('source', '')}"))
                        if consistent_id == learning_path_id:
                            # Delete the entire recommendation record
                            table.delete_item(Key={'RecommendationId': item['RecommendationId']})
                            deleted = True
                            break
                    if deleted:
                        break
                
                if deleted:
                    return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Deleted'})}
                else:
                    return {
                        'statusCode': 404,
                        'headers': cors_headers,
                        'body': json.dumps({'error': 'Learning path not found'})
                    }                        
            except Exception as delete_error:
                print(f"Delete operation error: {str(delete_error)}")
                return {
                    'statusCode': 500,
                    'headers': cors_headers,
                    'body': json.dumps({'error': f'Delete failed: {str(delete_error)}'})
                }
        
        elif operation == 'create':
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Created'})}
        
        elif operation == 'update':
            return {'statusCode': 200, 'headers': cors_headers, 'body': json.dumps({'message': 'Updated'})}
        
        # Default behavior - generate new recommendations
        skill = (body.get('Skill') or body.get('skill', '')).strip()
        current_level = (body.get('Current') or body.get('current_level', '')).strip()
        target_level = (body.get('Target') or body.get('target_level', '')).strip()
        employee = body.get('Employee', '').strip()
        skill_assessment_id = body.get('SkillAssessmentId', '')
        
        # Validate required fields for generation
        if not skill or not current_level or not target_level:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing required fields: Skill, Current, Target'})
            }
        
        # Get AI-powered recommendations
        recommendations = get_bedrock_recommendations(skill, current_level, target_level, employee)
        
        # Save to DynamoDB
        recommendation_id = save_recommendations_to_db(employee, skill, current_level, target_level, recommendations, skill_assessment_id)
        
        response_data = {
            'recommendation_id': recommendation_id,
            'recommendations': recommendations,
            'employee': employee,
            'skill': skill.title(),
            'current_level': current_level.title(),
            'target_level': target_level.title(),
            'powered_by': 'Amazon Bedrock AI'
        }
        
        if skill_assessment_id:
            response_data['skill_assessment_id'] = skill_assessment_id
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }

def get_bedrock_recommendations(skill, current_level, target_level, employee):
    try:
        print(f"ATTEMPTING BEDROCK: skill={skill}, employee={employee}")
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        prompt = f"""Generate 3-5 personalized learning recommendations for:
Employee: {employee}
Skill: {skill}
Current Level: {current_level}
Target Level: {target_level}

Provide practical, real-world courses from platforms like Coursera, Udemy, AWS Training, Microsoft Learn, Pluralsight, etc.

Return ONLY a JSON array with this exact format:
[
  {{
    "name": "Course Name",
    "source": "Platform Name", 
    "duration": "X weeks/hours",
    "url": "https://example.com/course"
  }}
]"""

        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 1000,
                "temperature": 0.1,
                "topP": 0.9
            }
        }
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-premier-v1:0',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['results'][0]['outputText']
        print(f"BEDROCK RESPONSE: {ai_response}")
        
        # Extract JSON from response - handle extra text after JSON
        start_idx = ai_response.find('[')
        if start_idx != -1:
            # Find the matching closing bracket
            bracket_count = 0
            end_idx = start_idx
            for i, char in enumerate(ai_response[start_idx:], start_idx):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                recommendations = json.loads(json_str)
                print(f"BEDROCK SUCCESS: Generated {len(recommendations)} recommendations")
                return recommendations
        
        print(f"BEDROCK FAILED: No valid JSON found in response, using fallback")
        return get_fallback_recommendations(skill, current_level, target_level)
        
    except Exception as e:
        print(f"BEDROCK ERROR: {str(e)} - Using fallback")
        return get_fallback_recommendations(skill, current_level, target_level)

def save_recommendations_to_db(employee, skill, current_level, target_level, recommendations, skill_assessment_id=None):
    """Save recommendations to DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['RECOMMENDATIONS_TABLE'])
        
        recommendation_id = str(uuid.uuid4())
        
        item = {
            'RecommendationId': recommendation_id,
            'Employee': employee,
            'Skill': skill,
            'CurrentLevel': current_level,
            'TargetLevel': target_level,
            'Recommendations': recommendations,
            'CreatedAt': datetime.utcnow().isoformat(),
            'Source': 'Bedrock AI'
        }
        
        if skill_assessment_id:
            item['SkillAssessmentId'] = skill_assessment_id
        
        table.put_item(Item=item)
        return recommendation_id
        
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        return str(uuid.uuid4())  # Return a UUID even if save fails

def get_fallback_recommendations(skill, current_level, target_level):
    """Fallback recommendations if Bedrock fails"""
    print(f"USING FALLBACK: skill={skill}, current={current_level}, target={target_level}")
    skill_lower = skill.lower().strip()
    
    if 'ai' in skill_lower or 'artificial intelligence' in skill_lower:
        return [
            {'name': 'Introduction to Artificial Intelligence', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://www.coursera.org/learn/introduction-to-ai'},
            {'name': 'Machine Learning Course', 'source': 'Coursera', 'duration': '11 weeks', 'url': 'https://www.coursera.org/learn/machine-learning'}
        ]
    elif 'azure' in skill_lower:
        return [
            {'name': 'Azure Fundamentals AZ-900', 'source': 'Microsoft Learn', 'duration': '3 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/azure-fundamentals/'},
            {'name': 'Azure Administrator AZ-104', 'source': 'Microsoft Learn', 'duration': '8 weeks', 'url': 'https://docs.microsoft.com/en-us/learn/paths/az-104-administrator-prerequisites/'}
        ]
    elif 'aws' in skill_lower:
        return [
            {'name': 'AWS Cloud Practitioner', 'source': 'AWS Training', 'duration': '4 weeks', 'url': 'https://aws.amazon.com/training/learn-about/cloud-practitioner/'},
            {'name': 'AWS Solutions Architect', 'source': 'AWS Training', 'duration': '12 weeks', 'url': 'https://aws.amazon.com/training/learn-about/architect/'}
        ]
    elif 'python' in skill_lower:
        return [
            {'name': 'Python for Everybody', 'source': 'Coursera', 'duration': '8 months', 'url': 'https://www.coursera.org/specializations/python'},
            {'name': 'Complete Python Bootcamp', 'source': 'Udemy', 'duration': '22 hours', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/'}
        ]
    else:
        return [
            {'name': f'{skill} Fundamentals', 'source': 'Coursera', 'duration': '6 weeks', 'url': f'https://www.coursera.org/courses?query={skill.replace(" ", "+")}'},
            {'name': f'Advanced {skill}', 'source': 'Udemy', 'duration': '8 weeks', 'url': f'https://www.udemy.com/courses/search/?q={skill.replace(" ", "+")}'}
        ]