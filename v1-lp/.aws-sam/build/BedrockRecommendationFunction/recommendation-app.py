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