# System Architecture Specification: AuraCode (Iteration 5/5 - Production Sign-Off)

---

## 1. High-Level Design (HLD)

### 1.1 System Component Diagram
```mermaid
graph TD
    Client[Client / X/Twitter / GitHub README] -->|HTTPS / GET SVG| Edge[Cloudflare Edge / SWR CDN]
    Client -->|HTTPS / REST API| Gateway[API Gateway / Load Balancer]
    
    subgraph Core Application Cluster
        Gateway -->|FastAPI Pods & Global Exception Handler| App[AuraCode Service Layer]
        App -->|Read/Write / Local AsyncIO Locks| Redis[(Redis Cluster: Rate Limits, Mutex & Cache)]
        App -->|Dispatch Stage 1 Jobs| SQS1[AWS SQS / Fetcher Queue]
    end

    subgraph Asynchronous Multi-Stage Worker Fleet DAG (AWS SQS + Native Workers)
        SQS1 --> Worker1[Fetcher Workers]
        Worker1 -->|GitHub REST/GraphQL API v4| GitHub[GitHub API]
        Worker1 -->|Enqueue Stage 2| SQS2[AWS SQS / Calculator Queue]
        SQS2 --> Worker2[Calculator Workers]
        Worker2 -->|Enqueue Stage 3| SQS3[AWS SQS / Persist Queue]
        SQS3 --> Worker3[Persister Workers]
        Worker3 -->|Persist Metrics, Scores & Outbox Event| DB[(PostgreSQL Hash-Partitioned Primary)]
        Worker3 -->|Poison / Max Retries Exceeded| DLQ[AWS SQS / Dead Letter Queue]
        
        subgraph Decoupled Outbox Publisher with SKIP LOCKED
            DB -->|CDC / Polling Outbox with FOR UPDATE SKIP LOCKED| OutboxQueue[AWS SQS / Purge Queue]
            OutboxQueue --> PurgeWorker[Cloudflare Purge Worker]
            PurgeWorker -->|Async Retry / POST Purge API| Cloudflare[Cloudflare API Purge]
        end
    end

    Edge -->|Cache Miss / Local Process Lock Fallback| App
```

### 1.2 Component Responsibilities
*   **Cloudflare Edge (CDN / SWR)**: Terminates TLS, serves pre-rendered SVG clout cards with Stale-Why-Revalidate (SWR) headers, strips malicious payloads, and isolates static assets on `cdn.auracode-assets.dev`. Purged asynchronously via the Outbox pattern.
*   **API Gateway & Load Balancer**: Distributes incoming HTTP/S traffic across stateless FastAPI service pods using least-connection algorithms.
*   **FastAPI Service Layer**: Handles authentication, route validation via Pydantic v2, synchronous read queries, dispatches asynchronous background telemetry jobs, and wraps DB calls with PyBreaker circuit breakers and global exception sanitization.
*   **Redis Cluster**: Manages rate-limiting token buckets, session states, and distributed mutex locks with dynamic p99-scaled TTLs and automatic worker lease-extension heartbeats. Enforces strict failure modes (fails open for rate-limiting, fails closed with `503` for idempotency during outages).
*   **Asynchronous Multi-Stage Ingestion Fleet**: Consists of decoupled Fetcher, Calculator, and Persister workers coordinated via AWS SQS queues and DLQs, polling natively using `aioboto3` with exponential backoff, randomized jitter, and visibility timeout scaling.
*   **PostgreSQL (Multi-AZ Hash-Partitioned)**: Stores durable user profiles, hash-partitioned historical metrics snapshots strictly partitioned by immutable `user_id` UUIDs, and outbox events processed safely via `FOR UPDATE SKIP LOCKED`.

### 1.3 Data Flow Walkthroughs

#### A. Write Path: User Onboarding & Ingestion (Multi-Stage DAG with Transactional Outbox)
1. User authenticates via GitHub OAuth; the API Gateway forwards the request to FastAPI.
2. FastAPI provisions a placeholder user row in PostgreSQL, generates an initial `version_hash`, and enqueues a Stage 1 fetcher job into `auracode-fetcher-sqs`.
3. **Stage 1 (Fetcher)**: A worker pulls the job via SQS long-polling, selects a GitHub App instance from the sharded installation pool, and retrieves raw commit trees, pruning files $>100\text{ KB}$. The payload is pushed to `auracode-calculator-sqs`.
4. **Stage 2 (Calculator)**: A worker computes metrics (churn, weekend commit ratio, PR turnaround) and the Aura score (-5,000 to +10,000). The result is pushed to `auracode-persist-sqs`.
5. **Stage 3 (Persister)**: A worker executes a single database transaction persisting the calculated metrics to PostgreSQL *and* inserting a cache-purge event into the `outbox_events` table (Transactional Outbox Pattern). 
6. **Decoupled Purge Pipeline**: A background CDC poller safely claims pending outbox entries using `FOR UPDATE SKIP LOCKED`, pushing events to `auracode-purge-sqs`. A dedicated Cloudflare Purge Worker consumes the queue, executing `POST /zones/{zone_id}/purge_cache` with independent exponential backoff. Failed ingestion jobs exceeding extended max-receive counts (8 attempts) are routed to `auracode-ingest-dlq`.

#### B. Read Path: SVG Clout Card Rendering
1. A markdown README requests `https://cdn.auracode-assets.dev/api/aura/{username}.svg?v={hash}`.
2. Cloudflare Edge checks its cache. If stale or missing, it forwards the request to the origin API Gateway.
3. FastAPI evaluates a local process-level `asyncio.Lock` (per worker instance) combined with a Redis distributed lock. If Redis is down, the system gracefully bypasses database advisory lock stampedes by serving immediate stale data from application memory or returning a `429 Too Many Requests` code to shed load.
4. Only one worker performs the render pass; concurrent requests wait or receive stale-cached content.
5. The service pulls user data, executes strict XML sanitization and RTL override neutralization, and returns the sanitized SVG. Cloudflare caches the payload with SWR headers.

---

## 2. Low-Level Design & Data Models (LLD)

### 2.1 Database Schema (PostgreSQL DDL)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table (Decoupled primary key; immutable user UUID)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    github_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(39) UNIQUE NOT NULL,
    avatar_url TEXT NOT NULL,
    aura_score INT NOT NULL CHECK (aura_score >= -5000 AND aura_score <= 10000),
    archetype VARCHAR(64) NOT NULL,
    roast_commentary TEXT NOT NULL,
    version_hash VARCHAR(32) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Metrics Snapshots Table (Hash Partitioned strictly by immutable user_id UUID)
CREATE TABLE metrics_snapshots (
    id UUID DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    churn_ratio NUMERIC(5, 4) NOT NULL CHECK (churn_ratio >= 0.0),
    weekend_commit_ratio NUMERIC(3, 2) NOT NULL CHECK (weekend_commit_ratio BETWEEN 0.0 AND 1.0),
    pr_turnaround_hours NUMERIC(8, 2) CHECK (pr_turnaround_hours >= 0.0),
    review_latency_hours NUMERIC(8, 2) CHECK (review_latency_hours >= 0.0),
    workflow_type VARCHAR(32) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) PARTITION BY HASH (user_id);

-- Hash Partitions for metrics_snapshots (4 Modulo Partitions)
CREATE TABLE metrics_snapshots_p0 PARTITION OF metrics_snapshots
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE metrics_snapshots_p1 PARTITION OF metrics_snapshots
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE metrics_snapshots_p2 PARTITION OF metrics_snapshots
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE metrics_snapshots_p3 PARTITION OF metrics_snapshots
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Transactional Outbox Table with Concurrency Guard Rails
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING' NOT NULL,
    locked_by VARCHAR(64),
    locked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Team Enterprise Installations
CREATE TABLE team_installations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id BIGINT UNIQUE NOT NULL,
    github_install_id BIGINT UNIQUE NOT NULL,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Indexing Strategy
*   `CREATE UNIQUE INDEX idx_users_github_id ON users(github_id);` — Ensures fast OAuth identity resolution.
*   `CREATE INDEX idx_users_username ON users(username);` — B-Tree index optimized for high-frequency profile and badge reads (`/api/aura/{username}`).
*   `CREATE INDEX idx_metrics_user_time ON metrics_snapshots(user_id, calculated_at DESC);` — Composite index for fetching historical velocity charts efficiently within hash partitions.
*   `CREATE INDEX idx_outbox_pending ON outbox_events(status, created_at) WHERE status = 'PENDING';` — Partial index for lightning-fast outbox event polling without table scans.

### 2.3 Data Consistency Guarantees
*   **Scores & Profiles**: **Eventual Consistency** with **Optimistic Concurrency Control (OCC)** via `version_hash` tags at the edge, eliminating distributed locking penalties.
*   **Transactions**: ACID transactions enforced for user onboarding, score recalculations, and transactional outbox event emission.

---

## 3. API Contracts & Idempotency

### 3.1 Endpoint Definitions

#### 1. Trigger Ingestion Job
*   **Method**: `POST`
*   **Route**: `/api/ingest/trigger`
*   **Headers**: `Idempotency-Key: <uuid>`, `Authorization: Bearer <token>`
*   **Request Body**: `{ "force_refresh": false }`
*   **Response Schema**: `{ "status": "queued", "job_id": "uuid", "estimated_seconds": 6 }`
*   **Status Codes**: `202 Accepted`, `400 Bad Request`, `401 Unauthorized`, `409 Conflict`, `429 Too Many Requests`, `503 Service Unavailable`

#### 2. Get User Aura Profile
*   **Method**: `GET`
*   **Route**: `/api/aura/{username}`
*   **Response Schema**: `AuraProfileResponse`
*   **Status Codes**: `200 OK`, `404 Not Found`, `304 Not Modified`, `503 Service Unavailable`

#### 3. GDPR Account Deletion
*   **Method**: `DELETE`
*   **Route**: `/api/account/data`
*   **Headers**: `Authorization: Bearer <token>`
*   **Response Schema**: `{ "status": "deleted", "cascade_purged_at": "timestamp" }`
*   **Status Codes**: `204 No Content`, `401 Unauthorized`, `503 Service Unavailable`

### 3.2 Idempotency Key Handling with Lease-Extension & Redis Outage Fallback
Mutating endpoints (`POST`, `DELETE`) enforce an `Idempotency-Key` header utilizing a Redis Lua script combined with an active worker heartbeat lease-extension background task:
1. When a request arrives, an atomic Redis script evaluates the idempotency key:
   - If missing, sets status to `processing`, stores the request `worker_uuid`, and sets an initial TTL (30 seconds).
   - If present as `processing`, checks if the worker heartbeat has expired (>30 seconds since last touch). If dead, **steals the lock** by overwriting the `worker_uuid`. If alive, returns `409 Conflict`.
   - If `completed`, returns the cached response payload.
2. **Lease Extension**: Workers holding active idempotency locks execute an asynchronous background task refreshing the Redis TTL every 10 seconds while long-running jobs (e.g., deep commit tree parsing) are active, preventing premature lock expiration.
3. **Redis Outage Fallback**: If Redis is unreachable during an idempotency check, the system **fails closed** and returns a `503 Service Unavailable` response with `{"error": "Idempotency store unavailable", "correlation_id": "uuid"}`.

---

## 4. Scalability, Caching & Performance

### 4.1 Caching Topology & Edge Purging
*   **Transactional Outbox Purging with SKIP LOCKED**: User profile JSON payloads are cached in Redis. Write paths strictly invalidate Redis keys and record a purge event in PostgreSQL `outbox_events`. A background publisher pulls batches safely using:
    ```sql
    UPDATE outbox_events 
    SET status = 'PROCESSING', locked_by = :worker_id, locked_at = CURRENT_TIMESTAMP 
    WHERE id IN (
        SELECT id FROM outbox_events 
        WHERE status = 'PENDING' 
        ORDER BY created_at 
        LIMIT 100 
        FOR UPDATE SKIP LOCKED
    );
    ```
    This eliminates polling race conditions and deadlocks across concurrent outbox workers.
*   **Stale-While-Revalidate (SWR) at Edge**: Cloudflare Edge caches SVG responses (`Cache-Control: public, max-age=3600, stale-while-revalidate=86400`).
*   **Cache Stampede Mitigation**: In-memory Python `asyncio.Lock` per worker instance acts as a first-tier defense against cache stampedes. If Redis is unreachable during a cache miss, the system **rejects excess concurrent render requests with a `429 Too Many Requests` or serves stale memory/CDN data immediately**, entirely eliminating risky database advisory lock thrashing on PostgreSQL.

### 4.2 Asynchronous Processing, Backpressure & Native Workers
*   Jobs are routed through a multi-stage SQS DAG (Fetcher $\rightarrow$ Calculator $\rightarrow$ Persister) and consumed by native asynchronous Python worker processes using `aioboto3` long-polling loops.
*   **Reliability & Backpressure**: SQS queues are configured with a robust `MaxReceiveCount` of 8 to withstand transient GitHub API 5xx outages and secondary rate-limit blocks (HTTP 429/403) without premature DLQ dumping. Messages failing all attempts route to `auracode-ingest-dlq`.
*   Workers enforce exponential backoff and randomized jitter on retries (`base_delay = 2s`, `max_retries = 8`).

### 4.3 Database Connection Pooling & Circuit Breakers
*   Configured with **PgBouncer in Transaction Pooling mode** (`statement_cache_size=20`, `pool_size=20`, `max_overflow=10`, `pool_timeout=30`). Application ORMs (SQLAlchemy with `asyncpg`) explicitly manage connection lifecycles without relying on session-level states.
*   **PostgreSQL Circuit Breaker**: Critical database read/write blocks are wrapped with a PyBreaker circuit breaker. If connection timeouts or error rates exceed safety thresholds, the breaker trips instantly, returning a sanitized `503 Service Unavailable` response.

---

## 5. Reliability, Fault Tolerance & Security

### 5.1 SPOF Elimination & Redis Failure Modes
*   **Redis Control Plane Fallback**: 
    *   *Rate-Limiting*: Fails **open** (permitting traffic with high-priority alerting) to prevent total user lockout during Redis outages.
    *   *Idempotency*: Fails **closed** (`503 Service Unavailable`) to prevent duplicate ingestion storms during outages.
    *   *Mutex/Cache Locks*: Bypasses database advisory locks entirely during outages, falling back to local `asyncio.Lock` instances and serving stale data or `429` responses.
*   **PostgreSQL & API Tier**: Multi-AZ PostgreSQL with synchronous replication and horizontally autoscaled FastAPI pods.

### 5.2 Exception Sanitization Guardrails
*   A global FastAPI exception handler catches all unhandled system, database (`asyncpg`), and internal errors, logging stack traces internally with a unique request correlation ID while returning a sanitized JSON response (`{"error": "Internal Server Error", "correlation_id": "uuid"}`).

### 5.3 Security, Sanitization & Hardening
*   **SVG XSS Defense**: All user-controlled strings (usernames, archetype titles) pass through strict server-side XML escaping. Script tags and inline event handlers are stripped.
*   **RTL & Unicode Neutralization**: SVG CSS properties enforce `direction: ltr; unicode-bidi: isolate;` to prevent Right-to-Left override attacks.
*   **Credential Hygiene**: GitHub OAuth tokens are encrypted at rest using AES-GCM-256 via AWS KMS.

---

## 6. Project Directory & File Blueprint

```text
auracode/
├── README.md
├── pyproject.toml
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   ├── security.py
│   │   ├── circuit_breaker.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── metrics.py
│   │   ├── outbox.py
│   │   └── team.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── aura.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_client.py
│   │   ├── calculator.py
│   │   ├── roaster.py
│   │   └── cdn_purge.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   ├── fetcher.py
│   │   ├── calculator.py
│   │   ├── persister.py
│   │   └── outbox_publisher.py
│   └── api/
│       ├── __init__.py
│       ├── v1/
│           ├── __init__.py
│           ├── auth.py
│           ├── ingest.py
│           ├── aura.py
│           └── svg.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── test_calculator.py
    │   ├── test_roaster.py
    │   └── test_svg_sanitizer.py
    └── integration/
        ├── test_ingestion_pipeline.py
        └── test_api_endpoints.py
```