#!/bin/bash
# Deployment script for Skill Management Portal to S3 with CloudFront invalidation
# Usage: ./deploy.sh [environment]

set -e

# Configuration
ENVIRONMENT=${1:-prod}
#DIST_DIR="/mnt/c/Devops/aws-hackthon-day/shared-materials/dist/skill-management-portal/browser"
DIST_DIR="/mnt/c/Devops/aws-hackthon-day/v1-sk/build/"
TERRAFORM_DIR="."
S3_BUCKET="skill-management-portal-prod-ro0qg44w"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are available."
}

# Get Terraform outputs
get_terraform_outputs() {
    print_status "Using configured S3 bucket: $S3_BUCKET"
    
    cd "$TERRAFORM_DIR"
    
    # Try to get CloudFront distribution ID from Terraform if available
    if [ -f "terraform.tfstate" ]; then
        CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null || echo "")
        CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain_name 2>/dev/null || echo "")
    else
        print_warning "Terraform state file not found. CloudFront invalidation will be skipped."
        CLOUDFRONT_DISTRIBUTION_ID=""
        CLOUDFRONT_DOMAIN=""
    fi
    
    print_status "S3 Bucket: $S3_BUCKET"
    if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        print_status "CloudFront Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID"
        print_status "CloudFront Domain: $CLOUDFRONT_DOMAIN"
    else
        print_warning "CloudFront distribution ID not available. Skipping CloudFront invalidation."
    fi
    
    cd ..
}

# Check if build exists
check_build() {
    print_status "Checking build directory..."
    
    if [ ! -d "$DIST_DIR" ]; then
        print_error "Build directory not found: $DIST_DIR"
        print_error "Please run 'ng build --prod' first."
        exit 1
    fi
    
    if [ ! -f "$DIST_DIR/index.html" ]; then
        print_error "index.html not found in build directory."
        exit 1
    fi
    
    print_status "Build directory found and valid."
}

# Sync files to S3
deploy_to_s3() {
    print_status "Deploying all files from $DIST_DIR to S3 bucket: $S3_BUCKET"
    
    # Upload all files to S3 with appropriate cache headers
    
    # First, upload index.html with no-cache headers (if it exists)
    if [ -f "$DIST_DIR/index.html" ]; then
        print_status "Uploading index.html with no-cache headers..."
        aws s3 cp "$DIST_DIR/index.html" "s3://$S3_BUCKET/" \
            --cache-control "no-cache, no-store, must-revalidate" \
            --metadata-directive REPLACE
    fi
    
    # Upload all static assets with long cache headers (excluding index.html)
    print_status "Uploading static assets..."
    aws s3 sync "$DIST_DIR/" "s3://$S3_BUCKET/" \
        --exclude "index.html" \
        --exclude "*.js" \
        --exclude "*.css" \
        --cache-control "public, max-age=31536000" \
        --delete
    
    # Upload JS files with specific content type and cache headers
    print_status "Uploading JavaScript files..."
    aws s3 sync "$DIST_DIR/" "s3://$S3_BUCKET/" \
        --exclude "*" \
        --include "*.js" \
        --cache-control "public, max-age=31536000" \
        --content-type "application/javascript"
    
    # Upload CSS files with specific content type and cache headers
    print_status "Uploading CSS files..."
    aws s3 sync "$DIST_DIR/" "s3://$S3_BUCKET/" \
        --exclude "*" \
        --include "*.css" \
        --cache-control "public, max-age=31536000" \
        --content-type "text/css"
    
    print_status "All files uploaded to S3 bucket '$S3_BUCKET' successfully."
}

# Create CloudFront invalidation
invalidate_cloudfront() {
    print_status "Creating CloudFront invalidation..."
    
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    print_status "CloudFront invalidation created: $INVALIDATION_ID"
    print_status "Waiting for invalidation to complete (this may take a few minutes)..."
    
    aws cloudfront wait invalidation-completed \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --id "$INVALIDATION_ID"
    
    print_status "CloudFront invalidation completed."
}

# Main deployment process
main() {
    print_status "Starting deployment for environment: $ENVIRONMENT"
    
    check_dependencies
    get_terraform_outputs
    check_build
    deploy_to_s3
    invalidate_cloudfront
    
    print_status "Deployment completed successfully!"
    print_status "Your application is available at: https://$CLOUDFRONT_DOMAIN"
    
    # If app_domain is configured, show custom domain info
    if [ "$CLOUDFRONT_DOMAIN" != "$(terraform output -raw app_domain 2>/dev/null || echo '')" ]; then
        print_warning "To use a custom domain, configure DNS to point to: $CLOUDFRONT_DOMAIN"
    fi
}

# Run main function
main "$@"