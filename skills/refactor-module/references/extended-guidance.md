<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Refactoring Patterns

### Pattern 1: Resource Grouping
Extract related resources into cohesive modules:
- Networking (VPC, Subnets, Route Tables)
- Compute (ASG, Launch Templates, Load Balancers)
- Data (RDS, ElastiCache, S3)

### Pattern 2: Configuration Layering
```hcl
# Base module with defaults
module "vpc_base" {
  source = "./modules/vpc-base"
  # Minimal required inputs
}

# Environment-specific wrapper
module "vpc_prod" {
  source = "./modules/vpc-production"
  # Inherits from base, adds prod-specific config
}
```

### Pattern 3: Composition
```hcl
# Small, focused modules
module "vpc" {
  source = "./modules/vpc"
}

module "security_groups" {
  source = "./modules/security-groups"
  vpc_id = module.vpc.vpc_id
}

module "application" {
  source     = "./modules/application"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  sg_ids     = module.security_groups.app_sg_ids
}
```

## Common Pitfalls

### 1. Over-Abstraction
```hcl
# ❌ Don't create overly generic modules
variable "resources" {
  type = map(map(any))  # Too flexible, hard to validate
}

# ✅ Do use specific, typed interfaces
variable "database_config" {
  type = object({
    engine         = string
    instance_class = string
  })
}
```

### 2. Tight Coupling
```hcl
# ❌ Don't couple modules through direct references
# module A
output "instance_id" { value = aws_instance.app.id }

# module B (in same config)
resource "aws_eip" "app" {
  instance = module.a.instance_id  # Tight coupling
}

# ✅ Do pass dependencies through root module
module "compute" {
  source = "./modules/compute"
}

resource "aws_eip" "app" {
  instance = module.compute.instance_id
}
```

### 3. State Migration Errors
Always test migration in non-production first:
```bash
# Create plan to verify no changes after migration
terraform plan -out=migration.tfplan

# Review carefully
terraform show migration.tfplan

# Apply only if plan shows no changes
terraform apply migration.tfplan
```

## Version Control Strategy

```hcl
# Use semantic versioning for modules
module "vpc" {
  source  = "git::https://github.com/org/terraform-modules.git//vpc?ref=v1.2.0"
  version = "~> 1.2"
}

# Pin to specific versions in production
# Use version ranges in development
```

## Success Criteria

- [ ] Module has single, well-defined responsibility
- [ ] All variables have descriptions and types
- [ ] Validation rules prevent invalid configurations
- [ ] Outputs provide sufficient information for consumers
- [ ] Documentation includes usage examples
- [ ] Tests verify module behavior
- [ ] State migration completed without resource recreation
- [ ] No plan differences after refactoring

## Related Skills
- [Terraform code generation](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/terraform/code-generation/skills/terraform-style-guide/SKILL.md) - Style guide for the new Terraform Module
- [Azure Verified Modules](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/terraform/code-generation/skills/azure-verified-modules/SKILL.md) - Recommended module specifications for Azure

## Resources
- [Terraform Module Development](https://developer.hashicorp.com/terraform/language/modules/develop)
- [Module Best Practices](https://developer.hashicorp.com/terraform/cloud-docs/registry/design)

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-07 | Initial skill definition |
