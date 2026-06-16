# NF-005: Zero-Downtime Rolling Deployments

## Type
Non-Functional

## Description
Deployments must use ECS rolling update settings that preserve service availability during releases.

## Requirement Trace
- Source File: docs/deployment.md
- Source Reference: CI/CD Pipeline > Rolling Deployment; minimum healthy percent 100 and maximum percent 200.

## Notes
- Health check grace period is explicitly set to 30 seconds.
