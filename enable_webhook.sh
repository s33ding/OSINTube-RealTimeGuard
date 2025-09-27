#!/bin/bash

echo "Enabling CodeBuild webhook for automatic triggers..."

# Uncomment webhook in Terraform
sed -i 's/^# resource "aws_codebuild_webhook"/resource "aws_codebuild_webhook"/' iac/codebuild.tf
sed -i 's/^#   project_name/  project_name/' iac/codebuild.tf
sed -i 's/^#   build_type/  build_type/' iac/codebuild.tf
sed -i 's/^#   filter_group/  filter_group/' iac/codebuild.tf
sed -i 's/^#     filter/    filter/' iac/codebuild.tf
sed -i 's/^#       type/      type/' iac/codebuild.tf
sed -i 's/^#       pattern/      pattern/' iac/codebuild.tf
sed -i 's/^#     }/    }/' iac/codebuild.tf
sed -i 's/^#   }/  }/' iac/codebuild.tf
sed -i 's/^# }/}/' iac/codebuild.tf

# Apply Terraform
cd iac
terraform apply -auto-approve

echo "Webhook enabled! Builds will now trigger automatically on push to main branch."
