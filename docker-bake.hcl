# Docker Bake file for DockFlow POC
# Build with: docker bake

variable "TAG" {
  default = "latest"
}

variable "REGISTRY" {
  default = "dockflow"
}

variable "PLATFORMS" {
  default = ["linux/amd64"]
}

# Default target
target "__default__" {
  platforms = PLATFORMS
  tags = ["${REGISTRY}/dockflow-api:${TAG}"]
}

# Matrix strategy for different build configurations
target "api" {
  inherits = ["__default__"]
  context = "./backend"
  dockerfile = "Dockerfile"
  args = {
    BUILDKIT_INLINE_CACHE = "1"
  }
  tags = [
    "${REGISTRY}/dockflow-api:${TAG}",
    "${REGISTRY}/dockflow-api:latest"
  ]
}

# Development build
target "api-dev" {
  inherits = ["api"]
  dockerfile = "Dockerfile.dev"
  tags = ["${REGISTRY}/dockflow-api:dev"]
  args = {
    BUILDKIT_INLINE_CACHE = "1"
    FLASK_ENV = "development"
  }
}

# Production build
target "api-prod" {
  inherits = ["api"]
  dockerfile = "Dockerfile.prod"
  tags = ["${REGISTRY}/dockflow-api:prod"]
  args = {
    BUILDKIT_INLINE_CACHE = "1"
    FLASK_ENV = "production"
  }
}

# Test build
target "api-test" {
  inherits = ["api"]
  dockerfile = "Dockerfile.test"
  tags = ["${REGISTRY}/dockflow-api:test"]
  args = {
    BUILDKIT_INLINE_CACHE = "1"
    FLASK_ENV = "testing"
  }
}

# Multi-stage build for different environments
group "default" {
  targets = ["api"]
}

group "all" {
  targets = ["api", "api-dev", "api-prod", "api-test"]
}

group "dev" {
  targets = ["api-dev"]
}

group "prod" {
  targets = ["api-prod"]
}

group "test" {
  targets = ["api-test"]
} 