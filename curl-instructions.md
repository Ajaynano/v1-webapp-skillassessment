# Skills Assessment API - cURL Instructions

Replace `YOUR_API_ENDPOINT` with your actual API Gateway URL from the CloudFormation outputs.

## 1. Create Skill Assessment
```bash
curl -X POST https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "create",
    "SkillAssessmentId": "test123",
    "Employee": "Steveb Doe",
    "Skill": "Python",
    "Current": "Beginner",
    "Target": "Intermediate"
  }'
```

## 2. List All Skill Assessments
```bash
curl -X POST https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list"
  }'
```

## 3. Read Single Skill Assessment
```bash
curl -X POST https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "read",
    "SkillAssessmentId": "test123"
  }'
```

## 4. Update Skill Assessment
```bash
curl -X POST https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update",
    "SkillAssessmentId": "test123",
    "Employee": "John Doe",
    "Skill": "Python",
    "Current": "Intermediate",
    "Target": "Advanced"
  }'
```

## 5. Delete Skill Assessment
```bash
curl -X POST https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "delete",
    "SkillAssessmentId": "test123"
  }'
```

## CORS Preflight (OPTIONS)
```bash
curl -X OPTIONS https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```