# Networking & Load Balancing Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: route HTTPS traffic from the internet to the ECS Fargate service and Next.js frontend, while isolating backend tasks in private subnets.

## 2. Scope Mapping
- Included: VPC layout, public and private subnets, Application Load Balancer, security groups, NAT Gateway, and TLS termination.
- Excluded: Application-level routing, DNS record management.

## 3. File Changes
- agenterrafrom/modules/vpc/main.tf
- agenterrafrom/modules/vpc/variables.tf
- agenterrafrom/modules/vpc/outputs.tf
- agenterrafrom/modules/alb/main.tf
- agenterrafrom/modules/alb/variables.tf
- agenterrafrom/modules/alb/outputs.tf

## 4. LangGraph Nodes (if applicable)
- N/A

## 5. Tools
- Terraform

## 6. State Updates
- N/A

## 7. Implementation Steps (strict order)
1. Define VPC with /16 CIDR block.
2. Define two public subnets (one per AZ) and two private subnets (one per AZ).
3. Define Internet Gateway and attach to VPC.
4. Define NAT Gateway in each public subnet; add routes from private subnets.
5. Define ALB security group accepting inbound port 443 only.
6. Define ECS security group accepting inbound port 8000 from ALB security group only; outbound port 443 unrestricted.
7. Define Application Load Balancer in public subnets with HTTPS listener on port 443.
8. Define ACM certificate reference and attach to HTTPS listener.
9. Define listener rules: /api/* routes to ECS target group; all other paths route to frontend target group.
10. Define ECS and frontend target groups with health check configurations.
11. Output VPC ID, subnet IDs, ALB ARN, and security group IDs for ECS module consumption.

## 8. Dependencies
- Terraform (infrastructure-as-code plan must be implemented first)
- ACM certificate (must exist in AWS account before ALB listener can use HTTPS)

## 9. Test Plan
- Unit tests: terraform validate for vpc and alb modules.
- Integration tests: terraform apply creates VPC, subnets, NAT Gateway, ALB, and security groups with correct rules.
- Workflow tests: HTTPS request reaches ALB; /api/* routes to ECS target group; ECS tasks have no public IP; ECS tasks reach external APIs via NAT Gateway.

## 10. Acceptance Criteria Mapping
- FR-001 Terminate HTTPS at the ALB. -> Validate ALB listener is on port 443 with ACM certificate.
- FR-002 Route /api/* requests to the ECS Fargate backend. -> Validate listener rule forwards /api/* to ECS target group.
- FR-003 Route all other requests to the Next.js frontend. -> Validate default listener rule forwards to frontend target group.
- FR-004 Run ECS tasks in private subnets with NAT Gateway access. -> Validate ECS tasks have no public IP and outbound traffic routes through NAT Gateway.

## 11. Open Questions
- None identified from the current requirements.
