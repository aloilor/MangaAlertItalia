# GitHub Actions: Test and Build Scraper

This workflow tests, builds, and pushes the `manga_scraper` Docker image to Amazon ECR.

## Key Points

1. **Trigger Conditions**  
   - Executes on `push` events to the `main` branch when files under `src/backend/manga_scraper/` are modified.

2. **Environment Variables**  
   - **ROLE_TO_ASSUME**  
   - **AWS_REGION**  
   - **SCRAPER_ECR_REPOSITORY**  
   These are stored as GitHub Secrets and used for AWS authentication and repository management.

3. **High-Level Steps**  
   1. **Checkout** the source code.  
   2. **Configure AWS credentials** via the assumed IAM role.  
   3. **Log in** to Amazon ECR.  
   4. **Set up Python**, install dependencies, and run **PyTest**.  
   5. **Build & Push** the Docker image to ECR.

