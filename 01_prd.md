# Product Requirements Document (PRD): AuraCode – The Viral 'Dev Spotify Wrapped' & GitHub Clout Engine

**Document Version:** 5.0.0-PROD  
**Author:** Principal Product Architect & Systems Strategist  
**Status:** Approved for Engineering Execution (Iteration 5 - Red-Team Hardened & Production-Optimized)  

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
Modern software engineers crave cultural validation and personalized insights regarding their coding habits, mirroring the massive viral success of consumer analytics products like *Spotify Wrapped*. However, existing developer metrics tools are sterile, productivity-obsessed, and often weaponized for toxic micro-management. They fail to capture the *human* side of software engineering: the 3 AM debugging sessions, chaotic merge conflict resolutions, esoteric YAML configurations, and the emotional toll of force-pushing to `main` on a Friday afternoon.

### 1.2 Solution Overview
**AuraCode** is a viral developer telemetry and gamification engine that ingests GitHub activity asynchronously, computes deep behavioral metrics, assigns a proprietary "Aura" score (-5,000 to +10,000), generates brutal yet hilarious archetypal roasts, and exposes high-performance, edge-cached SVG widgets on an isolated sandboxed domain. By combining rigorous code telemetry with internet culture, AuraCode turns code contributions into viral, shareable social currency while empowering engineering teams with high-density, non-toxic velocity analytics—backed by strict security sanitization, automated GDPR/CCPA data lifecycles, resilient multi-tenant GitHub App installation pools, and fault-tolerant asynchronous intake architectures.

---

## 2. User Personas & Core Journeys

### 2.1 User Personas
*   **The Clout-Chasing Junior (`@code-ninja-99`)**: Wants to flex their PR volume, weekend commits, and high Aura score on X/Twitter and LinkedIn. Authenticates via public-scope OAuth.
*   **The Pragmatic Indie Hacker (`@solo-dev`)**: Commits directly to `main` without opening pull requests or reviews. Expects scoring models that accurately value solo shipping velocity.
*   **The Private-Enterprise Developer (`@corp-dev`)**: Works entirely within private repositories. Requires explicit prompting to install the authorized GitHub App with private scopes to avoid false "Ghost" account classifications.
*   **The Engineering Manager (`@em-bureaucrat`)**: Requires deep team velocity insights via authorized GitHub App enterprise installations (`read:org`, `repo`) to audit delivery cadence and review bottlenecks.

### 2.2 Core User Journeys
1.  **The Asynchronous Viral Acquisition & Card Generation Journey**:
    *   User navigates to `auracode.dev` and clicks "Authenticate with GitHub".
    *   The system immediately provisions a placeholder state and renders an animated skeleton screen: *"Analyzing Code Aura... Synthesizing 3 AM Git logs..."*
    *   An ingestion worker dispatches asynchronously via an ingestion queue, parsing the last 90 days of activity using tree-metadata byte filtering before pulling raw diffs.
    *   The frontend connects via a lightweight Server-Sent Events (SSE) or exponential-backoff polling channel with jitter, receiving progress updates until the background job completes and reveals their interactive scorecard.
2.  **The Solo Maintainer & Private-Repo Developer Journey**:
    *   A developer authenticates, but the ingestion pipeline detects zero public commits or pull requests. 
    *   **Telemetry Check**: The system checks if the user has private repository associations. If private repos exist, the UI presents an explicit prompt: *"We detected zero public repositories. Install the AuraCode GitHub App to analyze your 50,000 lines of private enterprise code."* If they decline or truly have zero activity, the system safely routes them to the "Ghost/Zen Architect" archetype.

---

## 3. Functional Requirements

### 3.1 GitHub Ingestion, Payload Filtering & Multi-Tenant App Pools
*   **FR-1.1**: The system shall ingest public/private repositories, commit event timelines, pull requests, and review comments via the GitHub REST/GraphQL API v4. Initial user onboarding shall be strictly **asynchronous**.
*   **FR-1.2**: **Pre-Ingestion Byte-Size Payload Filtering**: To prevent worker memory exhaustion and GitHub bandwidth throttling, ingestion workers shall query the GitHub Git Trees API / File Metadata headers *before* pulling raw diff blobs. The pipeline shall automatically drop binary files, lockfiles (`package-lock.json`, `Cargo.lock`), and minified assets (`*.min.js`, `*.bundle.js`) exceeding a strict byte size threshold ($\gt 100\text{ KB}$ per file) based on raw `size` properties returned in tree metadata—completely avoiding line-count assumptions or unnecessary diff downloads.
*   **FR-1.3**: **Multi-Tenant GitHub App Rate-Limit Sharding**: The backend shall maintain a managed pool of multiple GitHub App installations (minimum 25 distinct application instances). Requests shall be dynamically routed via a round-robin pool with token-bucket rate-limit tracking in Redis, ensuring 300,000+ hourly viral requests never exhaust a single installation's 15,000 req/hour limit.

### 3.2 Velocity Analyzer & Solo-Hacker Fallback Scoring
*   **FR-2.1**: The velocity engine shall calculate core metrics: *Churn Ratio*, *Weekend Commit Ratio*, *PR Turnaround Time*, and *Review Latency*.
*   **FR-2.2**: **Solo Hacker / Zero-PR Fallback Weighting**: For developers with zero pull requests or review interactions (direct-to-main workflows), the engine shall bypass PR-dependent metrics and rebalance scoring weights toward *Direct Commit Cadence*, *Atomic Commit Density* (commits with `<50` lines changed), and *Main-Branch Force-Push Penalties*.

### 3.3 Aura Calculator & Account Classification
*   **FR-3.1**: The system shall compute a deterministic "Aura Score" ranging from **-5,000 to +10,000**.
*   **FR-3.2**: Scoring Rules Engine: Positive and negative weights applied for test files, atomic changes, force pushes, monolithic commits, and anti-pattern commit messages.
*   **FR-3.3**: **Account State Classification (Ghost vs. Private-Only)**: 
    *   If 90-day activity is zero *and* no private repos are detected, assign *"The Ghost in the Machine"* (score: `0`).
    *   If 90-day public activity is zero *but* private repos exist, trigger the Private-Repo-Only onboarding prompt.

### 3.4 Archetype Roast Engine & Combinatorial Variety
*   **FR-4.1**: The system shall classify the user into one of 16 base archetypes combined with secondary combinatorial trait modifiers and dynamic template interpolation, yielding >300 unique outputs.

### 3.5 Isolated Edge Rendering, SVG Security & Layout Hardening
*   **FR-5.1**: Dynamic SVG cards shall be served from an **isolated, sandboxed static asset domain** (e.g., `https://cdn.auracode-assets.dev/api/aura/{username}.svg?v={version_hash}`).
*   **FR-5.2**: **Mandatory Server-Side XML Sanitization & Visual Layout Hardening**: 
    *   *XSS Defense*: All user-controlled strings must pass through a strict server-side XML parser (stripping script tags, event handlers, and dynamic references).
    *   *Visual Injection Defense*: The SVG rendering engine must enforce hard character limits on repository names and usernames (max 24 characters), applying string truncation with ellipses (`text-overflow`).
    *   *Unicode/RTL Sanitization*: The SVG CSS style block must explicitly sanitize and isolate text nodes using strict defensive properties: `direction: ltr; unicode-bidi: isolate;` to neutralize Right-to-Left (RTL) override characters (`\u202E`) and zero-width space bombs.
*   **FR-5.3**: **Version-Hash Cache Invalidation & Request Coalescing**: 
    *   Every SVG URL path shall include a version hash (`?v={hash}`). 
    *   *Cache Stampede Mitigation*: Edge workers (Cloudflare) must implement **Stale-While-Revalidate (SWR)** combined with an origin-side Redis distributed Mutex lock (`SETEX` lock pattern). When an SVG cache version is invalidated, concurrent requests for the same expired hash trigger *only one* render pass on the origin worker, while concurrent connections await or receive stale-cached content briefly.

### 3.6 Team Velocity Dashboard
*   **FR-6.1**: The system shall support aggregated organization views displaying team burndown health and PR throughput distributions, accessible via authorized GitHub App enterprise installations with `read:org` scopes.

### 3.7 Data Privacy, Compliance & Right to be Forgotten (GDPR/CCPA)
*   **FR-7.1**: The platform shall provide a self-service data deletion endpoint (`DELETE /api/account/data`) triggering cascade deletion across PostgreSQL, Redis, and Cloudflare Edge caches.

### 3.8 Architecture & Data Contracts (Pydantic v2 Models)
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime

class MetricsPayload(BaseModel):
    churn_ratio: float = Field(..., ge=0.0, description="Code churn index with division-by-zero protection")
    weekend_commit_ratio: float = Field(..., ge=0.0, le=1.0)
    pr_turnaround_hours: Optional[float] = Field(None, ge=0.0)
    review_latency_hours: Optional[float] = Field(None, ge=0.0)
    workflow_type: str = Field(..., example="pr-driven") # or "direct-to-main"

class AuraProfileResponse(BaseModel):
    username: str = Field(..., example="torvalds", max_length=39)
    aura_score: int = Field(..., ge=-5000, le=10000)
    archetype: str = Field(..., example="The Merge Conflict Merchant")
    roast_commentary: str
    metrics: MetricsPayload
    avatar_url: HttpUrl
    version_hash: str = Field(..., description="Cache invalidation token")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 4. Non-Functional Requirements (SLOs/SLAs)

*   **Latency SLOs**:
    *   API Read Endpoints (`/api/aura/{username}`): **p95 < 50ms**, **p99 < 150ms** (cached).
    *   SVG Rendering Engine: **p95 < 80ms** at the edge (Cloudflare Workers).
    *   GitHub Ingestion Pipeline: Processed asynchronously via intake queue; initial generation completes within **< 10 seconds (P90)**, buffered by an animated skeleton screen and SSE/polling updates.
*   **Availability SLA**: **99.9% uptime** across core API and web services.
*   **Consistency Model & Concurrency Protection**: 
    *   *Profiles & Scores*: **Eventual Consistency** with **Optimistic Concurrency Control (OCC)** using version tags at the edge, eliminating cross-region distributed locking penalties.
*   **Durability**: Zero data loss for computed user scores and enterprise team configurations.

---

## 5. Scale & Capacity Estimations (Back-of-the-Envelope)

### 5.1 Viral Launch Traffic & Asynchronous Intake Queue Math
*   **Viral Spike Scenario**: 50,000 users authenticate within a brutal 60-minute window during a Product Hunt launch.
*   **Intake Surge Mitigation**: Authentications push ingestion jobs into an **asynchronous intake queue (AWS SQS / Kafka)** with exponential backoff. Workers consume jobs at a rate throttled safely within multi-tenant GitHub App installation limits.
*   **README Badge Edge QPS**: 80,000 active developers embedding SVG badges, viewed 200 times/day $\rightarrow$ $16,000,000$ requests/day ($\approx 185.2$ average QPS, surging to **~1,850 QPS** peak). Governed by strict edge CDN caching (`s-maxage=86400`), version-hash parameters, and origin request coalescing (Mutex locks).

### 5.2 GitHub API Rate-Limit Math & Multi-Tenant Sharding
*   50,000 users $\times$ 6 API requests per onboarding = **300,000 API requests** required during the launch hour.
*   **Sharded App Pool Architecture**: Deploying a pool of **25 distinct GitHub App installations**, each providing 15,000 req/hour, yields a combined capacity of **375,000 req/hour**, safely absorbing the 300,000 req/hour viral intake peak with a 20% headroom margin.

### 5.3 Real-Time Progress Infrastructure Load (SSE & Polling)
*   During the 50,000-user 60-minute launch surge, concurrent onboarding sessions require progress telemetry. 
*   Instead of heavy WebSockets holding permanent memory allocations, the frontend utilizes **Server-Sent Events (SSE)** or **exponential backoff HTTP polling with random jitter** (starting at 1s intervals up to 5s). API Gateway and Redis pub/sub handle connection states within a lightweight stateless edge tier, capping concurrent active polling connections at $\approx 5,000$ peak.

### 5.4 Storage & Memory Sizing
*   **User Footprint**: ~7 KB per user (JSON + metadata). 
*   **Daily Growth**: 100,000 active users/day $\times$ 7 KB = **700 MB/day**. 1-Year Footprint: **~255 GB**.
*   **Redis Working Set**: 80,000 active viral users $\times$ 7 KB = **560 MB**. Provisioning a **2 GB Redis cluster** handles hot caching, rate limits, session state, and origin mutex locks.

---

## 6. Scope Boundaries

### 6.1 In-Scope (v1 Release)
*   GitHub OAuth and multi-tenant GitHub App installation pooling.
*   Asynchronous ingestion pipeline with tree-metadata byte-size filtering ($\gt 100\text{ KB}$) and 90-day window constraints.
*   Aura Score calculation matrix with solo-hacker fallback weights, private-repo detection prompts, and 16 base archetypes.
*   Isolated static asset domain (`cdn.auracode-assets.dev`) serving sanitized SVGs with string truncation, RTL/Unicode neutralization, and request coalescing.
*   Automated GDPR/CCPA cascade deletion and cache purging hooks.

### 6.2 Explicitly Out-of-Scope (v2+ Roadmap)
*   GitLab, Bitbucket, or Azure DevOps integrations.
*   Real-time webhooks for live-updating scores during coding sessions.
*   AI-powered custom LLM roasts (v1 uses high-performance deterministic combinatorial templates).

---

## 7. Edge Cases & Failure Modes

### 7.1 Viral Traffic Spikes & Rate-Limit Lockouts
*   *Failure Mode*: 50,000 users hammering OAuth simultaneously, exhausting standard rate limits.
*   *Mitigation*: Multi-tenant sharded GitHub App installation pool (25+ instances) paired with an asynchronous intake queue and backpressure control.

### 7.2 Stored XSS and Visual Layout Explosions in SVGs
*   *Failure Mode*: Malicious actors injecting script payloads, zero-width space bombs, RTL override characters (`\u202E`), or 100-character repository names.
*   *Mitigation*: Mandatory server-side XML parsing, strict character length truncation, and CSS isolation (`direction: ltr; unicode-bidi: isolate;`) served from an isolated domain (`cdn.auracode-assets.dev`).

### 7.3 Cache Stampedes on Bulk Version-Hash Invalidation
*   *Failure Mode*: Popular users updating profiles simultaneously, causing mass cache misses and origin server collapse.
*   *Mitigation*: Redis distributed mutex locking combined with Cloudflare Stale-While-Revalidate (SWR) edge logic.

### 7.4 Private-Repository Developer Blind Spot
*   *Failure Mode*: Developers with 100% private code authenticated via public OAuth being misclassified as "Ghosts".
*   *Mitigation*: Automated detection of private enterprise associations prompting the installation of private-scoped GitHub App permissions.