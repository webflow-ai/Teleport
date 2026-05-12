# Retrieval Benchmark Report

**Total Queries**: 3
**Strategies Compared**: raw, enhanced

## Summary Metrics

| Strategy | Avg Similarity Score | Unique Chunks | Avg Latency (ms) |
|----------|---------------------|---------------|------------------|
| raw | 0.5286 | 8 | 35.33 |
| enhanced | 0.5120 | 8 | 32.68 |

## Result Overlap Analysis

**raw ∩ enhanced**: 8 common chunks

## Per-Query Results

### Query 1: "How do microservices communicate?"

#### raw

**Latency**: 37.32 ms

**Retrieved Chunks**:

1. **Score: 0.6484**
   ```
   Microservices architecture is a design pattern where applications are composed
   ```

2. **Score: 0.5399**
   ```
   asynchronous communication between services.
   ```

3. **Score: 0.4889**
   ```
   of small, independent services that communicate over well-defined APIs. Each service
   ```

#### enhanced

**Expanded Query**: "how do microservices communicate?"

**Latency**: 35.65 ms

**Retrieved Chunks**:

1. **Score: 0.6484**
   ```
   Microservices architecture is a design pattern where applications are composed
   ```

2. **Score: 0.5399**
   ```
   asynchronous communication between services.
   ```

3. **Score: 0.4889**
   ```
   of small, independent services that communicate over well-defined APIs. Each service
   ```

### Query 2: "What is the difference between commands and queries?"

#### raw

**Latency**: 42.96 ms

**Retrieved Chunks**:

1. **Score: 0.5751**
   ```
   and write operations into different models. Commands modify state, while queries
   ```

2. **Score: 0.5296**
   ```
   CQRS (Command Query Responsibility Segregation) is a pattern that separates read
   ```

3. **Score: 0.2799**
   ```
   retrieve data. This separation allows for optimized data models and improved
   ```

#### enhanced

**Expanded Query**: "what is the difference between commands and queries?"

**Latency**: 34.14 ms

**Retrieved Chunks**:

1. **Score: 0.5751**
   ```
   and write operations into different models. Commands modify state, while queries
   ```

2. **Score: 0.5296**
   ```
   CQRS (Command Query Responsibility Segregation) is a pattern that separates read
   ```

3. **Score: 0.2799**
   ```
   retrieve data. This separation allows for optimized data models and improved
   ```

### Query 3: "How does an API Gateway work?"

#### raw

**Latency**: 25.71 ms

**Retrieved Chunks**:

1. **Score: 0.8453**
   ```
   API Gateway is a server that acts as an entry point for client requests to
   ```

2. **Score: 0.4412**
   ```
   of small, independent services that communicate over well-defined APIs. Each service
   ```

3. **Score: 0.4094**
   ```
   backend services. It handles request routing, composition, protocol translation,
   ```

#### enhanced

**Expanded Query**: "how does an api (interface) gateway work?"

**Latency**: 28.25 ms

**Retrieved Chunks**:

1. **Score: 0.7836**
   ```
   API Gateway is a server that acts as an entry point for client requests to
   ```

2. **Score: 0.3824**
   ```
   backend services. It handles request routing, composition, protocol translation,
   ```

3. **Score: 0.3803**
   ```
   of small, independent services that communicate over well-defined APIs. Each service
   ```
