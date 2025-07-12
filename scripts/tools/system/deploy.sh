#!/bin/bash
# AI Compliance Engine - Deployment Script
# Phase 1: Infrastructure deployment automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/ace-deploy-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Help function
show_help() {
    cat << EOF
AI Compliance Engine Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    infrastructure  Deploy infrastructure (AWS/GCP)
    kubernetes      Deploy Kubernetes configurations
    applications    Deploy applications
    monitoring      Deploy monitoring stack
    all            Deploy everything
    destroy        Destroy infrastructure

Options:
    -e, --environment   Environment (dev/staging/prod) [default: dev]
    -r, --region        AWS region [default: us-east-1]
    -p, --project       GCP project ID
    -d, --dry-run       Show what would be deployed without executing
    -v, --verbose       Enable verbose output
    -h, --help          Show this help message

Examples:
    $0 -e dev infrastructure
    $0 -e prod -r us-west-2 all
    $0 -e staging --dry-run kubernetes
    $0 destroy -e dev

EOF
}

# Default values
ENVIRONMENT="dev"
AWS_REGION="us-east-1"
GCP_PROJECT=""
DRY_RUN=false
VERBOSE=false
COMMAND=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--project)
            GCP_PROJECT="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        infrastructure|kubernetes|applications|monitoring|all|destroy)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate inputs
if [[ -z "$COMMAND" ]]; then
    error "Command is required. Use -h for help."
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    error "Environment must be one of: dev, staging, prod"
fi

# Set derived variables
export AWS_DEFAULT_REGION="$AWS_REGION"
export TF_VAR_aws_region="$AWS_REGION"
export TF_VAR_environment="$ENVIRONMENT"

if [[ -n "$GCP_PROJECT" ]]; then
    export TF_VAR_gcp_project_id="$GCP_PROJECT"
    export GOOGLE_PROJECT="$GCP_PROJECT"
fi

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check required tools
    local tools=("terraform" "kubectl" "helm" "aws" "gcloud")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "$tool is not installed or not in PATH"
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or invalid"
    fi
    
    # Check GCP credentials if GCP project is specified
    if [[ -n "$GCP_PROJECT" ]]; then
        if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 &> /dev/null; then
            error "GCP credentials not configured or invalid"
        fi
    fi
    
    success "Prerequisites check passed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log "Deploying infrastructure for environment: $ENVIRONMENT"
    
    # Deploy AWS infrastructure
    log "Deploying AWS infrastructure..."
    cd "$PROJECT_ROOT/infrastructure/aws"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        terraform plan -var-file="terraform.tfvars"
    else
        terraform init
        terraform plan -var-file="terraform.tfvars"
        terraform apply -var-file="terraform.tfvars" -auto-approve
    fi
    
    # Deploy GCP infrastructure (DR) if GCP project is specified
    if [[ -n "$GCP_PROJECT" ]]; then
        log "Deploying GCP infrastructure (DR)..."
        cd "$PROJECT_ROOT/infrastructure/gcp"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            terraform plan -var-file="terraform.tfvars"
        else
            terraform init
            terraform plan -var-file="terraform.tfvars"
            terraform apply -var-file="terraform.tfvars" -auto-approve
        fi
    fi
    
    success "Infrastructure deployment completed"
}

# Deploy Kubernetes configurations
deploy_kubernetes() {
    log "Deploying Kubernetes configurations..."
    
    # Update kubeconfig
    log "Updating kubeconfig..."
    aws eks update-kubeconfig --region "$AWS_REGION" --name "ace-cluster-$ENVIRONMENT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would deploy Kubernetes configurations"
        kubectl diff -f "$PROJECT_ROOT/kubernetes/" || true
    else
        # Apply Kubernetes manifests
        log "Applying namespaces..."
        kubectl apply -f "$PROJECT_ROOT/kubernetes/namespaces.yaml"
        
        log "Applying RBAC configurations..."
        kubectl apply -f "$PROJECT_ROOT/kubernetes/rbac.yaml"
        
        log "Applying network policies..."
        kubectl apply -f "$PROJECT_ROOT/kubernetes/network-policies.yaml"
        
        # Install Istio if not already installed
        if ! kubectl get namespace istio-system &> /dev/null; then
            log "Installing Istio..."
            curl -L https://istio.io/downloadIstio | sh -
            ./istio-*/bin/istioctl install --set values.defaultRevision=default -y
            kubectl label namespace default istio-injection=enabled
        fi
        
        log "Applying Istio configurations..."
        kubectl apply -f "$PROJECT_ROOT/kubernetes/istio-setup.yaml"
    fi
    
    success "Kubernetes deployment completed"
}

# Deploy applications
deploy_applications() {
    log "Deploying applications..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would deploy applications using Helm"
        helm template ace "$PROJECT_ROOT/helm/ace" \
            --namespace "ace-api" \
            --set environment="$ENVIRONMENT" \
            --values "$PROJECT_ROOT/helm/ace/values-$ENVIRONMENT.yaml"
    else
        # Deploy applications using Helm
        log "Deploying applications with Helm..."
        helm upgrade --install ace "$PROJECT_ROOT/helm/ace" \
            --namespace "ace-api" \
            --create-namespace \
            --set environment="$ENVIRONMENT" \
            --values "$PROJECT_ROOT/helm/ace/values-$ENVIRONMENT.yaml" \
            --wait --timeout=600s
        
        # Verify deployment
        log "Verifying deployment..."
        kubectl rollout status deployment/ace-api -n ace-api
        kubectl get pods -n ace-api
    fi
    
    success "Applications deployment completed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would deploy monitoring stack"
    else
        # Add Prometheus Helm repository
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo add grafana https://grafana.github.io/helm-charts
        helm repo update
        
        # Deploy Prometheus
        log "Deploying Prometheus..."
        helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
            --namespace ace-monitoring \
            --create-namespace \
            --values "$PROJECT_ROOT/monitoring/prometheus-values.yaml" \
            --wait --timeout=600s
        
        # Deploy Grafana dashboards
        log "Deploying Grafana dashboards..."
        kubectl apply -f "$PROJECT_ROOT/monitoring/grafana-dashboards.yaml"
        
        # Deploy AlertManager configuration
        log "Deploying AlertManager configuration..."
        kubectl apply -f "$PROJECT_ROOT/monitoring/alertmanager-config.yaml"
    fi
    
    success "Monitoring deployment completed"
}

# Destroy infrastructure
destroy_infrastructure() {
    log "Destroying infrastructure for environment: $ENVIRONMENT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would destroy infrastructure"
        return
    fi
    
    # Confirm destruction
    read -p "Are you sure you want to destroy the $ENVIRONMENT environment? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        log "Destruction cancelled"
        return
    fi
    
    # Remove applications first
    log "Removing applications..."
    helm uninstall ace -n ace-api || true
    helm uninstall prometheus -n ace-monitoring || true
    
    # Remove Kubernetes resources
    log "Removing Kubernetes resources..."
    kubectl delete -f "$PROJECT_ROOT/kubernetes/" || true
    
    # Destroy GCP infrastructure
    if [[ -n "$GCP_PROJECT" ]]; then
        log "Destroying GCP infrastructure..."
        cd "$PROJECT_ROOT/infrastructure/gcp"
        terraform destroy -var-file="terraform.tfvars" -auto-approve
    fi
    
    # Destroy AWS infrastructure
    log "Destroying AWS infrastructure..."
    cd "$PROJECT_ROOT/infrastructure/aws"
    terraform destroy -var-file="terraform.tfvars" -auto-approve
    
    success "Infrastructure destruction completed"
}

# Main deployment function
main() {
    log "Starting AI Compliance Engine deployment"
    log "Environment: $ENVIRONMENT"
    log "AWS Region: $AWS_REGION"
    log "Command: $COMMAND"
    log "Dry Run: $DRY_RUN"
    
    if [[ "$VERBOSE" == "true" ]]; then
        set -x
    fi
    
    check_prerequisites
    
    case "$COMMAND" in
        infrastructure)
            deploy_infrastructure
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        applications)
            deploy_applications
            ;;
        monitoring)
            deploy_monitoring
            ;;
        all)
            deploy_infrastructure
            deploy_kubernetes
            deploy_applications
            deploy_monitoring
            ;;
        destroy)
            destroy_infrastructure
            ;;
        *)
            error "Unknown command: $COMMAND"
            ;;
    esac
    
    success "Deployment completed successfully"
    log "Log file: $LOG_FILE"
}

# Run main function
main "$@"