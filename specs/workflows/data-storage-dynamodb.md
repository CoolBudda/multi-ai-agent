# Data Storage (DynamoDB)

## Purpose
Persist user preferences reliably with low-latency access for all specialist agents.

## Scope
DynamoDB table definition, access patterns, IAM permissions, and data retention policy.

## Requirements
- Store user preferences keyed by user ID.
- Support read and write operations from the ECS backend service.
- Scale automatically with request volume.

## Inputs
- User ID (partition key).
- Preference field name and value.

## Outputs
- Stored preference record.
- Retrieved preference record.

## Business Rules
- Table name: `user-preferences`.
- Partition key: `user_id` (String).
- Billing mode: on-demand (pay per request).
- No TTL — preferences persist indefinitely.
- The ECS task role must have `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:UpdateItem` permissions on this table.
- Only essential user data is stored; no raw PII beyond required preference fields.

## Workflow
1. Memory Service receives a read request with a user ID.
2. Memory Service calls `GetItem` on the `user-preferences` table.
3. If no record exists, return an empty preferences object.
4. On write, Memory Service calls `PutItem` or `UpdateItem`.

## Data Model
- Primary key: `user_id` (String).
- Attributes: `preferred_airline`, `seat_preference`, `meeting_start_time`, `favorite_cuisine`, `news_topics`.

## Error Handling
- If `GetItem` fails, return empty preferences and proceed with agent defaults.
- If `PutItem`/`UpdateItem` fails, surface a user-facing error; do not silently discard the write.

## Acceptance Criteria
- Preferences written by the Memory Service can be read back in subsequent agent calls.
- On-demand scaling handles variable request load without pre-provisioning.
- The ECS task role grants only the required DynamoDB actions.

## Open Questions
- None identified from the current requirements.
