# NF-004: Auto-Scaling on Load Metrics

## Type
Non-Functional

## Description
The backend service scales out and in based on CPU, memory, and ALB request-rate thresholds.

## Requirement Trace
- Source File: docs/deployment.md
- Source Reference: ECS Fargate Service > Scaling Policy table.

## Notes
- Thresholds are explicitly defined for scale-out and scale-in windows.
