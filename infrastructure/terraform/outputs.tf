# Outputs - Display important information after creation

output "vpc_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.main.name
}

output "vpc_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.main.id
}

output "gke_subnet_name" {
  description = "Name of the GKE subnet"
  value       = google_compute_subnetwork.gke_subnet.name
}

output "gke_subnet_cidr" {
  description = "CIDR range of the GKE subnet"
  value       = google_compute_subnetwork.gke_subnet.ip_cidr_range
}

output "data_subnet_name" {
  description = "Name of the data subnet"
  value       = google_compute_subnetwork.data_subnet.name
}

output "nat_name" {
  description = "Name of the Cloud NAT"
  value       = google_compute_router_nat.nat.name
}

output "network_summary" {
  description = "Summary of network configuration"
  value = {
    vpc_name    = google_compute_network.main.name
    region      = var.region
    gke_subnet  = google_compute_subnetwork.gke_subnet.ip_cidr_range
    data_subnet = google_compute_subnetwork.data_subnet.ip_cidr_range
    nat_enabled = true
  }
}

# Cloud Run & Container Registry Outputs
output "artifact_registry_repository" {
  description = "Artifact Registry repository for containers"
  value       = google_artifact_registry_repository.containers.name
}

output "artifact_registry_url" {
  description = "URL for pushing container images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
}
