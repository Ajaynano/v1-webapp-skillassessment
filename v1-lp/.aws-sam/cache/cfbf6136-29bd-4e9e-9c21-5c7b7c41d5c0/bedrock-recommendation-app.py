import json
import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': cors_headers}
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        skill = (body.get('Skill') or body.get('skill', '')).strip()
        current_level = (body.get('Current') or body.get('current_level', '')).strip()
        target_level = (body.get('Target') or body.get('target_level', '')).strip()
        employee = body.get('Employee', '').strip()
        skill_assessment_id = body.get('SkillAssessmentId', '')
        
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
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }

def get_bedrock_recommendations(skill, current_level, target_level, employee):
    try:
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
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # Extract JSON from response
        start_idx = ai_response.find('[')
        end_idx = ai_response.rfind(']') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = ai_response[start_idx:end_idx]
            return json.loads(json_str)
        
        # Fallback if JSON parsing fails
        return get_fallback_recommendations(skill, current_level, target_level)
        
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
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
    skill_lower = skill.lower()
    
    if 'ai' in skill_lower or 'artificial intelligence' in skill_lower:
        return [
            {'name': 'Introduction to Artificial Intelligence', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://www.coursera.org/learn/introduction-to-ai'},
            {'name': 'Machine Learning Course', 'source': 'Coursera', 'duration': '11 weeks', 'url': 'https://www.coursera.org/learn/machine-learning'}
        ]
    elif 'aws' in skill_lower or 'cloud' in skill_lower:
        return [
            {'name': 'AWS Cloud Practitioner', 'source': 'AWS Training', 'duration': '4 weeks', 'url': 'https://aws.amazon.com/training/learn-about/cloud-practitioner/'},
            {'name': 'AWS Solutions Architect', 'source': 'AWS Training', 'duration': '12 weeks', 'url': 'https://aws.amazon.com/training/learn-about/architect/'}
        ]
    else:
        return [
            {'name': f'{skill} Fundamentals', 'source': 'Coursera', 'duration': '6 weeks', 'url': f'https://www.coursera.org/courses?query={skill.replace(" ", "+")}'},
            {'name': f'Advanced {skill}', 'source': 'Udemy', 'duration': '8 weeks', 'url': f'https://www.udemy.com/courses/search/?q={skill.replace(" ", "+")}'}
        ]