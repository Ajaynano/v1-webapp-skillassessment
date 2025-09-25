# Amazon Bedrock Integration Setup

## Prerequisites

1. **Enable Bedrock Model Access**
   - Go to AWS Console → Amazon Bedrock → Model access
   - Request access to `Anthropic Claude 3 Haiku` model
   - Wait for approval (usually instant for Claude 3 Haiku)

2. **Deploy the Updated Stack**
   ```bash
   sam build
   sam deploy
   ```

## Testing Bedrock Integration

### Local Testing
```bash
# Test Bedrock function locally (requires AWS credentials)
sam local invoke BedrockRecommendationFunction -e test-bedrock-recommendation-events.json
```

### API Testing
```bash
# Replace with your actual API Gateway URL
curl -X POST https://your-api-gateway-url/Prod/bedrock-recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "Employee": "John Doe",
    "Skill": "Python",
    "Current": "Beginner", 
    "Target": "Intermediate"
  }'
```

## Key Features

- **AI-Powered**: Uses Claude 3 Haiku for personalized recommendations
- **Fallback**: Falls back to static recommendations if Bedrock fails
- **Cost-Effective**: Uses the most affordable Claude model
- **Fast**: Haiku model provides quick responses (1-3 seconds)

## Cost Considerations

- Claude 3 Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Typical recommendation request: ~200 input tokens, ~300 output tokens
- Cost per request: ~$0.0004 (less than $0.001)

## Troubleshooting

1. **Model Access Denied**: Ensure Claude 3 Haiku access is enabled in Bedrock console
2. **Region Issues**: Bedrock is available in limited regions (us-east-1, us-west-2, etc.)
3. **Timeout**: Increase Lambda timeout if needed (currently set to 60 seconds)