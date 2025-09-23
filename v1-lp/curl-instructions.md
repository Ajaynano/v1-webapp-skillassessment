# Learning Path API - cURL Instructions

Replace `YOUR_API_ENDPOINT` with your actual API Gateway URL from the CloudFormation outputs.

## 1. Create Learning Path
```bash
curl -X POST YOUR_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "create",
    "Employee": "John Doe",
    "Skill": "Java",
    "Level": "Intermediate",
    "Name": "Advanced Java Programming",
    "Source": "Coursera",
    "Duration": "6 weeks",
    "Url": "https://coursera.org/java-course",
    "Completed": false,
    "StateDate": "25-08-2025",
    "EndDate": "06-10-2025"
  }'
```

## 2. List All Learning Paths
```bash
curl -X POST YOUR_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list"
  }'
```

## 3. Read Single Learning Path
```bash
curl -X POST YOUR_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "read",
    "LearningPathId": "test123"
  }'
```

## 4. Update Learning Path
```bash
curl -X POST YOUR_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update",
    "LearningPathId": "test123",
    "Employee": "John Doe",
    "Skill": "Python",
    "Level": "Advanced",
    "Name": "Data Engineering with Python",
    "Source": "Udemy",
    "Duration": "3 weeks",
    "Url": "https://udemy.com/python-course",
    "Completed": true,
    "StateDate": "01-09-2025",
    "EndDate": "21-09-2025"
  }'
```

## 5. Delete Learning Path
```bash
curl -X POST YOUR_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "delete",
    "LearningPathId": "test123"
  }'
```

## CORS Preflight (OPTIONS)
```bash
curl -X OPTIONS YOUR_API_ENDPOINT \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```