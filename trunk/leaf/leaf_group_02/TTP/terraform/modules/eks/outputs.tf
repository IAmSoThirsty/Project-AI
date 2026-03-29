output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = aws_eks_cluster.main.certificate_authority[0].data
}

output "cluster_security_group_id" {
  description = "Security group ID for the cluster"
  value       = aws_security_group.eks_cluster.id
}

output "node_group_id" {
  description = "EKS node group ID"
  value       = aws_eks_node_group.main.id
}

output "load_balancer_dns" {
  description = "Load balancer DNS (placeholder for ALB)"
  value       = "Set up via Kubernetes Ingress"
}
