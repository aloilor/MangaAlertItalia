# GitHub Actions: Test and Build Email Notifier

This workflow validates code changes in the `email_notifier` service, then packages and pushes a Docker image to an Amazon ECR repository.

## Key Points

1. **Trigger Conditions**  
   - Executes on `push` or `pull_request` to the `main` branch whenever files in `src/backend/email_notifier/` change.

2. **Environment Variables**  
   - **ROLE_TO_ASSUME**  
   - **AWS_REGION**  
   - **NOTIFIER_ECR_REPOSITORY**  
   These are stored as GitHub Secrets for secure AWS access and repository identification.

3. **High-Level Process**  
   1. **Checkout** the source code.  
   2. **Configure AWS** credentials via an assumed IAM role.  
   3. **Log in** to the Amazon ECR registry.  
   4. **Set up Python** and install dependencies.  
   5. **Run PyTest** to validate the code.  
   6. **Build & Push** the Docker image to ECR.

