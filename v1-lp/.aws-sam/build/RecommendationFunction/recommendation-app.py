import json

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
        
        # Handle both old format and new skill assessment format
        skill = (body.get('Skill') or body.get('skill', '')).lower()
        current_level = (body.get('Current') or body.get('current_level', '')).lower()
        target_level = (body.get('Target') or body.get('target_level', '')).lower()
        employee = body.get('Employee', '')
        skill_assessment_id = body.get('SkillAssessmentId', '')
        
        recommendations = get_recommendations(skill, current_level, target_level)
        
        response_data = {
            'recommendations': recommendations,
            'employee': employee,
            'skill': skill.title(),
            'current_level': current_level.title(),
            'target_level': target_level.title()
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

def get_recommendations(skill, current_level, target_level):
    recommendations = {
        'ai': {
            ('beginner', 'basic'): [
                {'name': 'Introduction to Artificial Intelligence', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/learn/introduction-to-ai'},
                {'name': 'AI Fundamentals', 'source': 'edX', 'duration': '3 weeks', 'url': 'https://edx.org/course/artificial-intelligence'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'Machine Learning Basics', 'source': 'Coursera', 'duration': '6 weeks', 'url': 'https://coursera.org/learn/machine-learning'},
                {'name': 'Deep Learning Fundamentals', 'source': 'Udacity', 'duration': '8 weeks', 'url': 'https://udacity.com/course/deep-learning'}
            ]
        },
        'python': {
            ('beginner', 'intermediate'): [
                {'name': 'Python Intermediate Programming', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/python-intermediate'},
                {'name': 'Data Structures in Python', 'source': 'Udemy', 'duration': '3 weeks', 'url': 'https://udemy.com/python-data-structures'}
            ]
        },
        'java': {
            ('beginner', 'intermediate'): [
                {'name': 'Java Programming Fundamentals', 'source': 'Coursera', 'duration': '5 weeks', 'url': 'https://coursera.org/java-fundamentals'}
            ]
        },
        'data': {
            ('beginner', 'intermediate'): [
                {'name': 'Data Analysis with Python', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/data-analysis-python'}
            ]
        },
        'cloud-azure': {
            ('beginner', 'basic'): [
                {'name': 'Azure Fundamentals', 'source': 'Microsoft Learn', 'duration': '3 weeks', 'url': 'https://learn.microsoft.com/azure-fundamentals'},
                {'name': 'Introduction to Azure Services', 'source': 'Pluralsight', 'duration': '2 weeks', 'url': 'https://pluralsight.com/azure-intro'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'Azure Administrator Associate', 'source': 'Microsoft Learn', 'duration': '8 weeks', 'url': 'https://learn.microsoft.com/azure-administrator'},
                {'name': 'Azure Solutions Architect', 'source': 'Udemy', 'duration': '10 weeks', 'url': 'https://udemy.com/azure-architect'}
            ]
        },
        'cloud-aws': {
            ('beginner', 'basic'): [
                {'name': 'AWS Cloud Practitioner', 'source': 'AWS Training', 'duration': '4 weeks', 'url': 'https://aws.amazon.com/training/cloud-practitioner'},
                {'name': 'Introduction to AWS Services', 'source': 'Coursera', 'duration': '3 weeks', 'url': 'https://coursera.org/aws-intro'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'AWS Solutions Architect Associate', 'source': 'AWS Training', 'duration': '12 weeks', 'url': 'https://aws.amazon.com/training/architect-associate'},
                {'name': 'AWS Developer Associate', 'source': 'A Cloud Guru', 'duration': '8 weeks', 'url': 'https://acloudguru.com/aws-developer'}
            ]
        },
        '.net': {
            ('beginner', 'basic'): [
                {'name': '.NET Core Fundamentals', 'source': 'Microsoft Learn', 'duration': '4 weeks', 'url': 'https://learn.microsoft.com/dotnet-fundamentals'},
                {'name': 'C# Programming Basics', 'source': 'Pluralsight', 'duration': '3 weeks', 'url': 'https://pluralsight.com/csharp-basics'}
            ],
            ('basic', 'intermediate'): [
                {'name': 'ASP.NET Core Web Development', 'source': 'Microsoft Learn', 'duration': '6 weeks', 'url': 'https://learn.microsoft.com/aspnet-core'},
                {'name': 'Entity Framework Core', 'source': 'Udemy', 'duration': '4 weeks', 'url': 'https://udemy.com/entity-framework-core'}
            ]
        }
    }
    
    return recommendations.get(skill, {}).get((current_level, target_level), [
        {'name': 'General Programming Course', 'source': 'Coursera', 'duration': '4 weeks', 'url': 'https://coursera.org/programming'}
    ])