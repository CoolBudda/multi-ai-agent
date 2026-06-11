# News Agent Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: retrieve, summarize, and personalize news headlines and topic-specific articles for the user.

## 2. Scope Mapping
- Included: Headline retrieval, topic search, article summarization, source quality filtering, interest-based personalization.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/agents/news_agent.py
- backend/agentservice/src/tools/news_tools.py
- backend/agentservice/src/services/memory_service.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/agents/test_news_agent.py
- backend/agentservice/tests/tools/test_news_tools.py

## 4. LangGraph Nodes (if applicable)
- load_news_topics
- parse_news_request
- fetch_articles
- filter_source_quality
- summarize_and_rank
- return_news_update

## 5. Tools
- Memory Service
- News API

## 6. State Updates
- news_topics
- topic
- title
- source
- summary
- relevance_score
- published_at
- articles

## 7. Implementation Steps (strict order)
1. Implement load of news_topics from Memory Service with fallback to general headlines when absent or empty.
2. Implement parsing of explicit topic from user request.
3. Implement article fetch through service layer tool node using explicit topic or saved interests.
4. Implement low-quality and irrelevant source filtering before presentation.
5. Implement summarization and ranking of filtered articles.
6. Return concise update payload with headlines or topic-specific summaries.
7. Emit news.fetch.completed and news.fetch.failed events at required points.
8. Return retry message on API failure and indicate limited results when high-quality results are limited.

## 8. Dependencies
- Memory Service
- News API

## 9. Test Plan
- Unit tests: Topic parsing, source-quality filter logic, ranking and summary formatting, event emission.
- Integration tests: Memory topic load behavior, News API fetch path, failure handling responses.
- Workflow tests: End-to-end general headlines flow, explicit-topic flow, and limited-results flow.

## 10. Acceptance Criteria Mapping
- FR-001 Fetch latest news by topic or general interest. -> Validate explicit-topic and fallback headline retrieval paths.
- FR-002 Summarize articles into concise, readable updates. -> Validate concise summary output format for returned articles.
- FR-003 Personalize news based on stored user interests. -> Validate saved interests are used when no topic is explicit.
- FR-004 Filter out low-quality or irrelevant sources. -> Validate filtered output excludes low-quality or irrelevant sources.

## 11. Open Questions
- None identified from the current requirements.
