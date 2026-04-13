output "cluster_name" {
  value = aws_eks_cluster.main.name
}
output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}
output "cluster_certificate_authority_data" {
  value     = aws_eks_cluster.main.certificate_authority[0].data
  sensitive = true
}
output "oidc_issuer_url" {
  value = aws_eks_cluster.main.identity[0].oidc[0].issuer
}
output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.eks.arn
}
output "node_group_role_arn" {
  value = aws_iam_role.eks_node_group.arn
}
output "configure_kubectl_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}