# GitHub Actions: Test and Build Main Backend

This workflow tests, builds, and deploys the main backend service to an Amazon ECS cluster. It also handles pushing Docker images to Amazon ECR, ensuring that code changes automatically trigger continuous integration and deployment.

## Key Highlights

1. **Trigger Conditions**  
   - Runs on `push` events targeting the `main` branch for changes in `src/backend/main_backend/`.

2. **Environment Variables**  
   - **ROLE_TO_ASSUME**  
   - **AWS_REGION**  
   - **MAIN_BACKEND_ECR_REPOSITORY**  
   - **ECS_SERVICE**  
   - **ECS_CLUSTER**  
   - **ECS_TASK_DEFINITION**  
   - **CONTAINER_NAME**  
   These are stored securely as GitHub Secrets for AWS deployment.

3. **High-Level Workflow**  
   1. **Checkout** the repository.  
   2. **Configure AWS Credentials** using an IAM role.  
   3. **Log in** to Amazon ECR.  
   4. **Set up Python** for running tests.  
   5. **Install Dependencies** and run **PyTest**.  
   6. **Build & Push** Docker image to ECR.  
   7. **Retrieve** the ECS Task Definition.  
   8. **Deploy** the new task definition to the ECS service.