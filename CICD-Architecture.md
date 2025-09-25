# CI/CD Architecture - Skill Management Portal

## Overview
This document provides a graphical representation of the CI/CD pipeline for the Skill Management Portal, covering Frontend, Skills Assessment API, and Learning Path API deployments.

## CI/CD Flow Diagram

```mermaid
graph TB
    subgraph "GitHub Repository"
        A[Developer Push/PR] --> B{Changed Files?}
        B -->|build/** changes| C[Frontend Workflow]
        B -->|src/**, template.yaml changes| D[Skills Assessment Workflow]
        B -->|v1-lp/** changes| E[Learning Path Workflow]
    end

    subgraph "Frontend CI/CD"
        C --> F[Checkout Code]
        F --> G[Configure AWS Credentials]
        G --> H[Sync to S3 Bucket]
        H --> I[Set Cache Headers]
        I --> J[Invalidate CloudFront]
        J --> K[Frontend Deployed ✅]
    end

    subgraph "Skills Assessment API CI/CD"
        D --> L[Checkout Code]
        L --> M[Setup Python 3.11]
        M --> N[Setup SAM CLI]
        N --> O[Configure AWS Credentials]
        O --> P[SAM Build]
        P --> Q[SAM Deploy]
        Q --> R[Skills API Deployed ✅]
    end

    subgraph "Learning Path API CI/CD"
        E --> S[Checkout Code]
        S --> T[Setup Python 3.11]
        T --> U[Setup SAM CLI]
        U --> V[Configure AWS Credentials]
        V --> W[SAM Build - v1-lp/]
        W --> X[SAM Deploy - v1-lp/]
        X --> Y[Learning Path API Deployed ✅]
    end

    subgraph "AWS Infrastructure"
        K --> Z1[S3 + CloudFront]
        R --> Z2[API Gateway + Lambda]
        Y --> Z3[API Gateway + Lambda]
        Z1 --> Z4[DynamoDB]
        Z2 --> Z4
        Z3 --> Z4
        Z4 --> Z5[Cognito User Pool]
        Z5 --> Z6[QuickSight Dashboard]
    end

    style A fill:#e1f5fe
    style K fill:#c8e6c9
    style R fill:#c8e6c9
    style Y fill:#c8e6c9
```

## Workflow Triggers

### Frontend Deployment
- **Trigger**: Changes to `build/**` directory
- **Workflow**: `.github/workflows/deploy-frontend.yml`
- **Target**: S3 + CloudFront

### Skills Assessment API
- **Trigger**: Changes to `src/**`, `template.yaml`, `samconfig.toml`
- **Workflow**: `.github/workflows/deploy-skills-assessment.yml`
- **Target**: Lambda + API Gateway

### Learning Path API
- **Trigger**: Changes to `v1-lp/**`
- **Workflow**: `.github/workflows/deploy.yml`
- **Target**: Lambda + API Gateway

## Deployment Flow Details

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant GHA as GitHub Actions
    participant AWS as AWS Services

    Dev->>GH: Push Code Changes
    GH->>GHA: Trigger Workflow
    
    alt Frontend Changes
        GHA->>AWS: Upload to S3
        GHA->>AWS: Invalidate CloudFront
        AWS-->>GHA: Deployment Success
    else Backend Changes (Skills/LP API)
        GHA->>GHA: SAM Build
        GHA->>AWS: SAM Deploy
        AWS->>AWS: Create/Update Lambda
        AWS->>AWS: Update API Gateway
        AWS-->>GHA: Deployment Success
    end
    
    GHA-->>Dev: Deployment Notification
```

## Environment Configuration

### Required GitHub Secrets
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### AWS Resources
- **S3 Bucket**: Frontend hosting
- **CloudFront**: CDN distribution
- **API Gateway**: REST API endpoints
- **Lambda Functions**: Backend logic
- **DynamoDB**: Data storage
- **Cognito**: Authentication
- **QuickSight**: Analytics dashboard

## Manual Deployment Options

All workflows support manual triggering via `workflow_dispatch` for on-demand deployments.

```bash
# Trigger via GitHub CLI
gh workflow run deploy-frontend.yml
gh workflow run deploy-skills-assessment.yml
gh workflow run deploy.yml
```