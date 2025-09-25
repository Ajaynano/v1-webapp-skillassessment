# Skill Management Portal

A comprehensive skill management application built with Angular frontend and AWS serverless backend services.

## 🏗️ Architecture

- **Frontend**: Angular application deployed to S3 with CloudFront CDN
- **Backend**: AWS Lambda functions with API Gateway
- **Database**: DynamoDB for data storage
- **Authentication**: AWS Cognito User Pool
- **Analytics**: Amazon QuickSight integration

## 🚀 Angular App Deployment

### Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform installed (for infrastructure)
- Bash shell (WSL on Windows, or Git Bash)

### Quick Deploy

```bash
# Make the deploy script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh prod
```

### Manual Deployment Steps

#### 1. Configure Environment

Update the environment configuration in `build/assets/environments/environment.json`:

```json
{
  "apiUrl": "https://your-api-gateway-url/Prod/skills-assessments",
  "lpApiUrl": "https://your-api-gateway-url/Prod/bedrock-recommendations",
  "quicksightEmbeddingApiUrl": "https://your-api-gateway-url/Prod/quicksight-embed",
  "dashboardID": "your-dashboard-id",
  "userPoolId": "your-cognito-user-pool-id",
  "userPoolClientId": "your-cognito-client-id"
}
```

#### 2. Deploy Infrastructure (if not already done)

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply
```

#### 3. Deploy Angular App

The Angular app is pre-built and located in the `build/` directory. Deploy using:

```bash
# Set your S3 bucket name
export S3_BUCKET="your-s3-bucket-name"

# Upload files to S3
aws s3 sync build/ s3://$S3_BUCKET/ --delete

# Set proper cache headers for index.html
aws s3 cp build/index.html s3://$S3_BUCKET/ \
  --cache-control "no-cache, no-store, must-revalidate"

# Set long cache headers for static assets
aws s3 sync build/ s3://$S3_BUCKET/ \
  --exclude "index.html" \
  --cache-control "public, max-age=31536000"
```

#### 4. Invalidate CloudFront Cache

```bash
# Get your CloudFront distribution ID
export DISTRIBUTION_ID="your-cloudfront-distribution-id"

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

### Automated Deployment Script

The `deploy.sh` script automates the entire deployment process:

```bash
#!/bin/bash
# Deploy with environment parameter
./deploy.sh prod

# The script will:
# 1. Check dependencies (AWS CLI, Terraform)
# 2. Get infrastructure outputs
# 3. Validate build directory
# 4. Upload files to S3 with proper cache headers
# 5. Create CloudFront invalidation
# 6. Wait for invalidation to complete
```

### Build Directory Structure

```
build/
├── assets/
│   ├── environments/
│   │   ├── environment.json          # Runtime configuration
│   │   └── amplifyconfiguration.json # AWS Amplify config
│   ├── images/                       # Static images
│   └── js/                          # JavaScript utilities
├── media/                           # Media assets
├── index.html                       # Main HTML file
├── main-*.js                        # Angular main bundle
├── polyfills-*.js                   # Browser polyfills
├── scripts-*.js                     # Additional scripts
└── styles-*.css                     # Compiled styles
```

### Environment Configuration

The app uses runtime configuration from `build/assets/environments/environment.json`. Update this file with your AWS resource endpoints:

- `apiUrl`: Skills Assessment API endpoint
- `lpApiUrl`: Learning Path API endpoint  
- `quicksightEmbeddingApiUrl`: QuickSight embedding API
- `dashboardID`: QuickSight dashboard ID
- `userPoolId`: Cognito User Pool ID
- `userPoolClientId`: Cognito User Pool Client ID

### Deployment Verification

After deployment, verify the application:

1. **Access the app**: Visit your CloudFront domain
2. **Check API connectivity**: Test login and data loading
3. **Verify QuickSight**: Ensure dashboards load properly
4. **Test all features**: Skills assessment, learning paths, recommendations

### Troubleshooting

#### Common Issues

**Build files not found**
```bash
# Ensure build directory exists
ls -la build/
```

**S3 upload permissions**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify S3 bucket access
aws s3 ls s3://your-bucket-name/
```

**CloudFront invalidation fails**
```bash
# Check distribution exists
aws cloudfront list-distributions

# Verify permissions for CloudFront
aws iam get-user
```

**CORS issues**
- Ensure API Gateway has proper CORS configuration
- Check that API endpoints match environment.json

#### Logs and Monitoring

```bash
# Check CloudFront logs
aws logs describe-log-groups --log-group-name-prefix "/aws/cloudfront"

# Monitor S3 access logs
aws s3 ls s3://your-bucket-name/logs/
```

## 🔧 Development

### Local Development

For local development, you would typically:

```bash
# Install dependencies (if package.json exists)
npm install

# Start development server
ng serve

# Build for production
ng build --prod
```

### API Integration

The Angular app integrates with multiple AWS services:

- **Skills Assessment API**: CRUD operations for skill assessments
- **Learning Path API**: Manage employee learning paths
- **Bedrock Recommendations**: AI-powered learning recommendations
- **QuickSight**: Embedded analytics dashboards
- **Cognito**: User authentication and authorization

## 📁 Project Structure

```
v1-sk/
├── build/                           # Pre-built Angular app
│   ├── assets/
│   ├── media/
│   └── *.js, *.css, *.html
├── v1-lp/                          # Learning Path API
│   ├── src/
│   ├── template.yaml
│   └── README.md
├── src/                            # Skills Assessment API
│   └── app.py
├── deploy.sh                       # Deployment script
├── template.yaml                   # Main SAM template
├── samconfig.toml                  # SAM configuration
└── README.md                       # This file
```

## 🚀 Backend APIs

This project includes multiple serverless APIs:

- **Skills Assessment API**: See `src/app.py`
- **Learning Path API**: See `v1-lp/README.md` for detailed documentation

## 🗑️ Cleanup

To remove all deployed resources:

```bash
# Delete S3 bucket contents
aws s3 rm s3://your-bucket-name --recursive

# Destroy infrastructure
terraform destroy

# Delete SAM stacks
sam delete --stack-name your-stack-name
```

## 🔄 GitHub Integration

### Automated CI/CD with GitHub Actions

The project includes GitHub Actions workflows for automated deployment:

#### Setup GitHub Secrets

Add these secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

#### Workflows

**Backend Deployment** (`.github/workflows/deploy.yml`):
- Triggers on push to main/master
- Builds and deploys SAM applications
- Deploys both Skills Assessment and Learning Path APIs

**Frontend Deployment** (`.github/workflows/deploy-frontend.yml`):
- Triggers on changes to `build/` directory
- Deploys Angular app to S3
- Invalidates CloudFront cache

#### Manual Deployment

Trigger deployments manually:

```bash
# Push to trigger backend deployment
git push origin main

# Trigger frontend deployment
gh workflow run deploy-frontend.yml
```

### Repository Setup

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Add GitHub remote
git remote add origin https://github.com/your-username/skill-management-portal.git
git push -u origin main
```

### Branch Protection

Recommended branch protection rules:
- Require pull request reviews
- Require status checks (GitHub Actions)
- Restrict pushes to main branch

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Verify all environment configurations
4. Ensure proper AWS permissions