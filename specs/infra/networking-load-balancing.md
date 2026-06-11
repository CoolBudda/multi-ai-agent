# Networking & Load Balancing

## Purpose
Route HTTPS traffic from the internet to the ECS Fargate service and Next.js frontend, while isolating backend tasks in private subnets.

## Scope
VPC layout, public and private subnets, Application Load Balancer, security groups, NAT Gateway, and TLS termination.

## Requirements
- Terminate HTTPS at the ALB.
- Route `/api/*` requests to the ECS Fargate backend.
- Route all other requests to the Next.js frontend.
- Run ECS tasks in private subnets with NAT Gateway access to the internet.

## Inputs
- AWS region and AZ selection.
- ALB listener rules.
- Security group rule definitions.
- ACM certificate for TLS.

## Outputs
- Running ALB with HTTPS listener.
- ECS tasks reachable only from the ALB security group.
- NAT Gateway providing outbound internet access for ECS tasks.

## Business Rules
- The ALB accepts inbound traffic on port 443 only.
- ECS tasks accept traffic on port 8000 from the ALB security group only.
- ECS tasks have outbound access to port 443 for external APIs, Bedrock, DynamoDB, and Secrets Manager.
- No ECS task has a public IP address.

## Workflow
1. ALB receives an HTTPS request on port 443.
2. Listener rules evaluate the request path.
3. `/api/*` routes to the ECS target group on port 8000.
4. All other paths route to the frontend target group.
5. ECS tasks use the NAT Gateway for outbound calls to external services.

## Data Model
- VPC CIDR: `/16`.
- Two public subnets (one per AZ) for the ALB.
- Two private subnets (one per AZ) for ECS tasks.
- Security groups: ALB SG, ECS SG.

## Error Handling
- If an ECS task fails health checks, the ALB stops sending traffic to it.
- If the NAT Gateway is unavailable, ECS tasks cannot reach external APIs; emit a service degradation alert.

## Acceptance Criteria
- HTTPS traffic reaches the ALB and is routed to the correct target group.
- ECS tasks have no public IP and are reachable only from the ALB.
- ECS tasks can make outbound HTTPS calls via the NAT Gateway.

## Open Questions
- None identified from the current requirements.
