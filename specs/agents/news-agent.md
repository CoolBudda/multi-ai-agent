# News Agent

## Purpose
Retrieve, summarize, and personalize news headlines and topic-specific articles for the user.

## Scope
Headline retrieval, topic search, article summarization, source quality filtering, and interest-based personalization.

## Requirements
- Fetch latest news by topic or general interest.
- Summarize articles into concise, readable updates.
- Personalize news based on stored user interests.
- Filter out low-quality or irrelevant sources.

## Inputs
- News query or topic from the user message.
- Saved topic interests from the Memory Service.
- News API article data.

## Outputs
- Headlines or topic-specific article summaries.
- Personalized news feed.
- `news.fetch.completed`, `news.fetch.failed` events.

## Business Rules
- Load `news_topics` at agent start; fall back to general headlines if absent or empty.
- When no topic is specified in the request, use saved topics as the default filter.
- All news API calls go through the service layer tool node.
- Low-quality or irrelevant sources must be filtered before presentation.

## Workflow
1. Load saved topic interests from the Memory Service.
2. Parse the news request for an explicit topic.
3. Fetch articles using the explicit topic or saved interests.
4. Filter by source quality.
5. Summarize and rank results.
6. Return a concise news update.

## Data Model
- `NewsQuery`: `{ topic: str | None }`
- `Article`: `{ title, source, summary, relevance_score, published_at }`
- `NewsResponse`: `{ articles: list[Article] }`

## Error Handling
- If the news API fails, emit `news.fetch.failed` with the error code and return a user-facing retry message.
- If no high-quality results are found, return the best available filtered set with an indication of limited results.

## Acceptance Criteria
- General queries return concise top headlines.
- Topic queries return relevant summaries.
- Saved interests shape results when no topic is explicit.
- Low-quality sources are filtered out.

## Open Questions
- None identified from the current requirements.
