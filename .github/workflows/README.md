# CI/CD Pipeline for Car Rental API

This GitHub Actions workflow will build a Docker image from your code, push it to Amazon ECR, and then deploy it to Amazon ECS.

## Prerequisites

Before you can use this workflow, you need to:

1. Create an Amazon ECR repository named `se-project`
2. Create an Amazon ECS cluster named `se-project`
3. Create an Amazon ECS service named `car-rental-service`
4. Create an IAM user with permissions to push to ECR and deploy to ECS
5. Configure the following GitHub Secrets:
   - `AWS_SECRET_ACCESS_KEY` - Corresponding AWS secret key

## Run locally - Local Testing with Act

For more detailed instructions on using Act, please refer to the README in the [`.act` directory](../../backend/.act/README.md)

## Task Definition

The `.aws/task-definition.json` file contains configuration for your ECS task including:

1. Container name and image reference
2. CPU and memory allocation
3. Port mappings
4. Log configuration
5. Environment variables (sourced from GitHub Secrets)

## Customization

You may need to modify the `deploy.yml` workflow file:

1. Change the `AWS_REGION` if your resources are in a different region
2. Adjust the repository, service, and cluster names if different
3. Update the branch name in the trigger section if you're not using `main`

## Troubleshooting

If the deployment fails:

1. Check the GitHub Actions logs for details
2. Verify your AWS credentials are correct
3. Ensure your task definition is valid
4. Check that your ECS service has the necessary permissions
5. Verify the container health check is passing
6. Ensure all required GitHub Secrets are properly configured

