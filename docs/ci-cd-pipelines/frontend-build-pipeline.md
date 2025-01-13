# GitHub Actions: Test and Build Frontend

This workflow automatically builds, tests, and deploys a frontend application to an AWS S3 bucket and then invalidates the associated CloudFront distribution for immediate updates.

## Key Points

1. **Trigger Conditions**  
   - Executes whenever you push targeting the `main` branch under the `src/frontend` folder.

2. **Environment Variables**  
   - **ROLE_TO_ASSUME**  
   - **AWS_REGION**  
   - **S3_BUCKET_FRONTEND**  
   - **CLOUDFRONT_DISTRIBUTION_ID_FRONTEND**  
   These values are stored securely in the repository’s GitHub Secrets.

3. **High-Level Steps**  
   1. **Checkout** your repository.  
   2. **Configure AWS Credentials** using an IAM role.  
   3. **Set up Node.js** to run your build.  
   4. **Install Frontend Dependencies** in `src/frontend/`.  
   5. **Build** the frontend (e.g., `npm run build`).  
   6. **Clear** the S3 bucket to remove outdated files.  
   7. **Upload** the new build artifacts to S3.  
   8. **Invalidate** the CloudFront distribution to ensure new content is served immediately.

