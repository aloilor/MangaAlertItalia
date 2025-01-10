# GitHub Actions: Terraform CI/CD Pipeline

This workflow manages Terraform operations for infrastructure code found in the `infra/` directory. It runs formatting, validation, planning, and (on pushes to the `main` branch) automatically applies changes.

## Key Points

1. **Trigger Conditions**  
   - Executes on `push` and `pull_request` events targeting the `main` branch for changes in the `infra/` folder.

2. **Environment Variables**  
   - **ROLE_TO_ASSUME**  
   - **AWS_REGION**  
   - **BUCKET_TF_STATE**  
   These values are stored as GitHub Secrets to enable secure AWS and Terraform configuration.

3. **High-Level Steps**  
   1. **Checkout** the repository.  
   2. **Configure AWS** credentials using the specified IAM role.  
   3. **Setup Terraform**, pinned to version `1.9.5`.  
   4. **Terraform Init** with a remote backend (S3 state).  
   5. **Terraform Format** check to ensure style consistency.  
   6. **Terraform Validate** to confirm syntax correctness.  
   7. **Terraform Plan** on pull requests; outputs a plan summary via PR comment.  
   8. **Terraform Apply** automatically on `push` to `main`.

4. **Usage**  
   1. **Commit or open a PR** for changes in `infra/`. The workflow runs automatically:
      - Pull requests get a Terraform plan preview.  
      - Merging or pushing directly to `main` triggers the `apply`.

