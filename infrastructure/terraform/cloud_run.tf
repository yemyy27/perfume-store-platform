# Cloud Run - Serverless container platform for microservices

# Enable Cloud Run API
resource "google_project_service" "run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Enable Artifact Registry API (for container images)
resource "google_project_service" "artifact_registry_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Build API
resource "google_project_service" "cloudbuild_api" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Create Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "containers" {
  location      = var.region
  repository_id = "${var.environment}-containers"
  description   = "Docker container images for microservices"
  format        = "DOCKER"
  
  depends_on = [google_project_service.artifact_registry_api]
}
