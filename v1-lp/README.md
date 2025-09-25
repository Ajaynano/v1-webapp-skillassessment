# Learning Path API

A serverless API for managing employee learning paths built with AWS SAM, Lambda, and DynamoDB.

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured
- SAM CLI installed
- Python 3.9+

### Deploy
```bash
# Clone and navigate to project
cd v1-lp

# Build the application
sam build

# Deploy to AWS
sam deploy --guided

# Note the API endpoint from outputs
```

## 📋 API Operations

All operations use POST method to `/learning-path` endpoint with operation type in request body.

### 1. Create Learning Path
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/learning-path  \
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

**Response:**
```json
{
  "message": "Created",
  "LearningPathId": "generated-uuid"
}
```

### 2. List All Learning Paths
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/learning-path \
  -H "Content-Type: application/json" \
  -d '{"operation": "list"}'
```

**Response:**
```json
{
  "Learning-Paths": [
    {
      "LearningPathId": "uuid",
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
    }
  ]
}
```

### 3. Read Single Learning Path
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/learning-path  \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "read",
    "LearningPathId": "your-learning-path-id"
  }'
```

### 4. Update Learning Path
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/learning-path  \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update",
    "LearningPathId": "your-learning-path-id",
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

### 5. Delete Learning Path
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/learning-path  \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "delete", 
    "LearningPathId": "your-learning-path-id"
  }'
```

## 🎯 Learning Path Recommendations

### Get AI-Powered Recommendations (Bedrock)
```bash
curl -X POST https://your-api-gateway-url/Prod/bedrock-recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "Employee": "John Doe",
    "Skill": "Python",
    "Current": "Beginner",
    "Target": "Intermediate",
    "SkillAssessmentId": "optional-assessment-id"
  }'
```

### Get Skill-Based Recommendations (Original Format)
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai",
    "current_level": "beginner",
    "target_level": "basic"
  }'
```

### Get Recommendations from Skill Assessment
```bash
curl -X POST https://zblsje9px2.execute-api.us-east-1.amazonaws.com/Prod/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "SkillAssessmentId": "c6bf654b-3001-42d0-a13e-54ca33f1a737",
    "Employee": "Kalaiselvan Pandiyan",
    "Skill": "AI",
    "Current": "Beginner",
    "Target": "Basic"
  }'
```

**Supported Skills:**
- `ai` - Artificial Intelligence
- `cloud-azure` - Microsoft Azure
- `cloud-aws` - Amazon Web Services
- `.net` - .NET Framework
- `python` - Python Programming
- `java` - Java Programming
- `data` - Data Science

**Bedrock AI Response:**
```json
{
  "recommendation_id": "abc123-def456-ghi789",
  "recommendations": [
    {
      "name": "Python for Data Science and Machine Learning",
      "source": "Udemy",
      "duration": "25 hours",
      "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"
    },
    {
      "name": "Python Programming Specialization",
      "source": "Coursera",
      "duration": "5 months",
      "url": "https://www.coursera.org/specializations/python-3-programming"
    }
  ],
  "employee": "John Doe",
  "skill": "Python",
  "current_level": "Beginner",
  "target_level": "Intermediate",
  "powered_by": "Amazon Bedrock AI"
}
```

### Get Saved Recommendations
```bash
curl -X GET https://your-api-gateway-url/Prod/recommendations/abc123-def456-ghi789
```

**Original Response:**
```json
{
  "recommendations": [
    {
      "name": "Introduction to Artificial Intelligence",
      "source": "Coursera",
      "duration": "4 weeks",
      "url": "https://coursera.org/learn/introduction-to-ai"
    }
  ],
  "employee": "Kalaiselvan Pandiyan",
  "skill": "Ai",
  "current_level": "Beginner",
  "target_level": "Basic",
  "skill_assessment_id": "c6bf654b-3001-42d0-a13e-54ca33f1a737"
}
```

## 🧪 Testing

### Direct Lambda Testing
```bash
# Test learning path function
sam local invoke LearningPathFunction -e test-events.json

# Test recommendation function
sam local invoke RecommendationFunction -e test-recommendation-events.json
```

### API Testing
```bash
# Test deployed API
sam local start-api
curl -X POST http://localhost:3000/learning-path -H "Content-Type: application/json" -d @test-events.json
curl -X POST http://localhost:3000/recommendations -H "Content-Type: application/json" -d @test-recommendation-events.json
curl -X POST http://localhost:3000/bedrock-recommendations -H "Content-Type: application/json" -d @test-bedrock-recommendation-events.json
```

## 📊 Data Schema

### Learning Path Fields
- `LearningPathId` (string) - Auto-generated UUID
- `Employee` (string) - Employee name
- `Skill` (string) - Skill being learned
- `Level` (string) - Skill level (Beginner/Intermediate/Advanced)
- `Name` (string) - Course/learning path name
- `Source` (string) - Learning platform (Coursera, Udemy, etc.)
- `Duration` (string) - Time to complete
- `Url` (string) - Course URL
- `Completed` (boolean) - Completion status
- `StateDate` (string) - Start date (DD-MM-YYYY)
- `EndDate` (string) - End date (DD-MM-YYYY)

### Recommendation Fields
- `RecommendationId` (string) - Auto-generated UUID
- `Employee` (string) - Employee name
- `Skill` (string) - Target skill
- `CurrentLevel` (string) - Current skill level
- `TargetLevel` (string) - Target skill level
- `Recommendations` (array) - List of recommended courses
- `CreatedAt` (string) - ISO timestamp
- `Source` (string) - "Bedrock AI" or "Static"
- `SkillAssessmentId` (string, optional) - Related assessment ID

## 🛠 Development

### Local Development
```bash
# Start API locally
sam local start-api

# Invoke function directly
sam local invoke LearningPathFunction -e test-events.json
```

### Logs
```bash
# View logs
sam logs -n LearningPathFunction --stack-name learning-path-api --tail
```

## 🗑 Cleanup
```bash
# Delete the stack
sam delete --stack-name learning-path-api
```

## 📁 Project Structure
```
v1-lp/
├── template.yaml                    # SAM template
├── samconfig.toml                  # SAM configuration  
├── src/
│   ├── app.py                     # Learning Path Lambda function
│   ├── learning-path-app.py       # Alternative Learning Path function
│   └── recommendation-app.py      # Recommendation Lambda function
├── test-events.json               # Learning Path test events
├── test-recommendation-events.json # Recommendation test events
├── curl-instructions.md           # cURL examples
└── README.md                     # This file
```