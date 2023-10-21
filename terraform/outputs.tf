output "rds_cluster_endpoint" {
  description = "The endpoint to call rds cluster"
  value       = module.db.cluster_id
}
