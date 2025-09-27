# CodeBuild Webhook Setup Instructions

## Current Status
- ✅ CodeBuild project configured
- ✅ GitHub connection created (PENDING authorization)
- ❌ Webhook disabled (requires connection authorization)

## To Enable Automatic Builds on Push:

### Step 1: Authorize GitHub Connection
1. Go to AWS Console: https://console.aws.amazon.com/codesuite/settings/connections
2. Find "osintube-github-connection" (status: PENDING)
3. Click "Update pending connection"
4. Authorize with your GitHub account
5. Verify status changes to "AVAILABLE"

### Step 2: Enable Webhook in Terraform
After authorization, uncomment the webhook in `iac/codebuild.tf`:

```hcl
# CodeBuild Webhook for automatic triggering
resource "aws_codebuild_webhook" "osintube" {
  project_name = aws_codebuild_project.osintube.name
  build_type   = "BUILD"

  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "refs/heads/main"
    }
  }
}
```

### Step 3: Apply Terraform
```bash
cd iac
terraform apply -auto-approve
```

## Manual Trigger (Current Solution)
Until webhook is set up, use:
```bash
./trigger_build.sh
```

## Troubleshooting
- If webhook creation fails: Ensure GitHub connection status is "AVAILABLE"
- If builds don't trigger: Check webhook filters match your branch name
- For build failures: Check CloudWatch logs at `/aws/codebuild/osintube-build`
