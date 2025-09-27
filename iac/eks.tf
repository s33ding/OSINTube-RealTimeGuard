# AWS provider for sa-east-1 region
provider "aws" {
  alias  = "sa_east_1"
  region = "sa-east-1"
}

# Data source for existing EKS cluster in sa-east-1
data "aws_eks_cluster" "sas_cluster" {
  provider = aws.sa_east_1
  name     = "sas-6881323-eks"
}

# Kubernetes provider configuration
provider "kubernetes" {
  host                   = data.aws_eks_cluster.sas_cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.sas_cluster.certificate_authority[0].data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.sas_cluster.name, "--region", "sa-east-1"]
  }
}

# Update aws-auth ConfigMap to include CodeBuild role
resource "kubernetes_config_map_v1_data" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = yamlencode([
      {
        rolearn  = "arn:aws:iam::248189947068:role/sas-6881323-default-eks-node-group"
        username = "system:node:{{EC2PrivateDNSName}}"
        groups   = ["system:bootstrappers", "system:nodes"]
      },
      {
        rolearn  = aws_iam_role.codebuild_role.arn
        username = "codebuild"
        groups   = ["system:masters"]
      }
    ])
  }

  force = true
}
