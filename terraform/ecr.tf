module "data_embedding_handler_lambda" {
  source = "./modules/ecr_compute_service_access"

  name          = var.ecr_config.data_embedding_handler.name
  image_mutable = var.ecr_config.data_embedding_handler.image_mutable
  force_delete  = var.ecr_config.data_embedding_handler.force_delete
  scan_on_push  = var.ecr_config.data_embedding_handler.scan_on_push
  keep_images   = var.ecr_config.data_embedding_handler.keep_images
}

module "query_handler" {
  source = "./modules/ecr_compute_service_access"

  name          = var.ecr_config.data_embedding_handler.name
  image_mutable = var.ecr_config.data_embedding_handler.image_mutable
  force_delete  = var.ecr_config.data_embedding_handler.force_delete
  scan_on_push  = var.ecr_config.data_embedding_handler.scan_on_push
  keep_images   = var.ecr_config.data_embedding_handler.keep_images
}