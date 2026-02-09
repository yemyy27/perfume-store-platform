# VPC Network - The foundation of our cloud infrastructure
# This creates an isolated network for all our resources

resource "google_compute_network" "main" {
  name                    = "${var.environment}-perfume-store-vpc"
  auto_create_subnetworks = false
  description             = "Main VPC network for perfume store platform"
}

# Subnet for GKE cluster and application workloads
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${var.environment}-gke-subnet"
  ip_cidr_range = "10.0.0.0/20" # 4096 IP addresses
  region        = var.region
  network       = google_compute_network.main.id

  # Secondary IP ranges for Kubernetes pods and services
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14" # For pod IPs
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20" # For service IPs
  }

  description = "Subnet for GKE cluster and workloads"
}

# Subnet for Cloud SQL and other data services
resource "google_compute_subnetwork" "data_subnet" {
  name          = "${var.environment}-data-subnet"
  ip_cidr_range = "10.1.0.0/24" # 256 IP addresses
  region        = var.region
  network       = google_compute_network.main.id
  description   = "Subnet for databases and data services"
}

# Cloud Router - Required for Cloud NAT
resource "google_compute_router" "router" {
  name    = "${var.environment}-router"
  region  = var.region
  network = google_compute_network.main.id

  bgp {
    asn = 64514
  }
}

# Cloud NAT - Allows private resources to access internet
resource "google_compute_router_nat" "nat" {
  name                               = "${var.environment}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
