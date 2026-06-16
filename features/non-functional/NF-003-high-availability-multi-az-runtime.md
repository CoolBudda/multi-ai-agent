# NF-003: High Availability Multi-AZ Runtime

## Type
Non-Functional

## Description
The runtime must maintain high availability by running at least two ECS tasks across Availability Zones.

## Requirement Trace
- Source File: docs/deployment.md
- Source Reference: ECS Fargate Service > Scaling Policy; "Minimum tasks: 2 (one per Availability Zone for HA)."

## Notes
- Networking layout also specifies 2 AZ public/private subnet distribution.
