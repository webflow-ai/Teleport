"""
Sample technical documents for testing the Context-Aware Retrieval Engine.

These documents cover software architecture topics and are used for:
- Integration testing of the ingestion pipeline
- Benchmarking retrieval strategies
- Validating end-to-end system behavior
"""

# 10 technical paragraphs on software architecture topics
SAMPLE_DOCUMENTS = [
    """
    Microservices architecture is a design pattern that structures an application as a collection 
    of loosely coupled services. Each service is independently deployable and scalable, focusing 
    on a specific business capability. This architectural style enables organizations to develop 
    and deploy services independently, allowing teams to work autonomously and choose the best 
    technology stack for their specific service. The microservices approach contrasts with 
    monolithic architecture, where all components are tightly integrated into a single deployable unit.
    """,
    
    """
    Event-driven architecture (EDA) is a software design pattern that promotes the production, 
    detection, consumption, and reaction to events. In this architecture, services communicate 
    through asynchronous event messages rather than synchronous request-response calls. Events 
    represent state changes or significant occurrences in the system. This pattern enables loose 
    coupling between services, improves scalability, and allows systems to react to changes in 
    real-time. Common implementations use message brokers like Apache Kafka, RabbitMQ, or AWS EventBridge.
    """,
    
    """
    The Repository pattern is a design pattern that mediates between the domain and data mapping 
    layers, acting like an in-memory collection of domain objects. It provides a more object-oriented 
    view of the persistence layer and encapsulates the logic required to access data sources. By 
    centralizing data access logic, the Repository pattern promotes separation of concerns and makes 
    the codebase more maintainable and testable. Repositories typically expose methods like find, 
    save, update, and delete, abstracting away the underlying database implementation details.
    """,
    
    """
    CQRS (Command Query Responsibility Segregation) is an architectural pattern that separates 
    read and write operations into different models. Commands modify state and don't return data, 
    while queries return data without modifying state. This separation allows for independent 
    optimization of read and write workloads, enabling different data models, scaling strategies, 
    and even separate databases for each concern. CQRS is particularly beneficial in complex domains 
    where read and write patterns differ significantly, and is often combined with event sourcing.
    """,
    
    """
    API Gateway is a server that acts as an entry point for client requests to backend services 
    in a microservices architecture. It handles cross-cutting concerns such as authentication, 
    rate limiting, request routing, load balancing, and protocol translation. The gateway pattern 
    simplifies client interactions by providing a unified interface to multiple services, reducing 
    the number of round trips between client and server. Popular implementations include Kong, 
    AWS API Gateway, and Azure API Management. The gateway can also perform request aggregation, 
    combining responses from multiple services into a single response.
    """,
    
    """
    Domain-Driven Design (DDD) is a software development approach that emphasizes collaboration 
    between technical experts and domain experts to create a shared understanding of the business 
    domain. DDD introduces concepts like bounded contexts, aggregates, entities, and value objects 
    to model complex business logic. The ubiquitous language ensures that developers and domain 
    experts use the same terminology. Strategic DDD focuses on high-level architecture and context 
    mapping, while tactical DDD provides patterns for implementing domain models. This approach is 
    particularly effective for complex domains with intricate business rules.
    """,
    
    """
    The Circuit Breaker pattern is a design pattern used to detect failures and prevent cascading 
    failures in distributed systems. When a service experiences repeated failures, the circuit 
    breaker trips to an open state, immediately returning errors without attempting the operation. 
    After a timeout period, it enters a half-open state to test if the underlying issue has been 
    resolved. If successful, it closes and resumes normal operation; otherwise, it reopens. This 
    pattern improves system resilience and prevents resource exhaustion. Libraries like Hystrix, 
    Resilience4j, and Polly provide circuit breaker implementations.
    """,
    
    """
    Serverless architecture is a cloud computing execution model where the cloud provider dynamically 
    manages the allocation and provisioning of servers. Developers write functions that execute in 
    response to events, without managing infrastructure. The serverless model offers automatic 
    scaling, pay-per-execution pricing, and reduced operational overhead. Functions as a Service 
    (FaaS) platforms like AWS Lambda, Azure Functions, and Google Cloud Functions enable this 
    paradigm. While serverless reduces infrastructure management, it introduces challenges like 
    cold starts, vendor lock-in, and debugging complexity in distributed environments.
    """,
    
    """
    The Saga pattern is a design pattern for managing distributed transactions across multiple 
    services in a microservices architecture. Instead of traditional ACID transactions, sagas 
    coordinate a sequence of local transactions, where each service performs its transaction and 
    publishes an event. If a step fails, the saga executes compensating transactions to undo 
    previous steps and maintain consistency. Sagas can be implemented using choreography (services 
    coordinate through events) or orchestration (a central coordinator manages the workflow). This 
    pattern is essential for maintaining data consistency without distributed locks.
    """,
    
    """
    Hexagonal Architecture, also known as Ports and Adapters, is an architectural pattern that 
    aims to create loosely coupled application components that can be easily connected to their 
    software environment through ports and adapters. The core business logic resides in the center 
    (the hexagon), isolated from external concerns like databases, user interfaces, and external 
    services. Ports define interfaces for communication, while adapters implement these interfaces 
    to connect to specific technologies. This architecture promotes testability by allowing easy 
    substitution of external dependencies with test doubles, and enables technology-agnostic 
    business logic that can evolve independently of infrastructure choices.
    """
]

SIMPLE_DOCUMENTS = [
    "Python is a high-level programming language known for its simplicity and readability.",
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
    "REST APIs use HTTP methods like GET, POST, PUT, and DELETE to perform operations on resources.",
    "Docker containers package applications with their dependencies for consistent deployment.",
    "Git is a distributed version control system for tracking changes in source code."
]

def get_documents(category="default"):
    """Get documents by category."""
    if category == "simple":
        return SIMPLE_DOCUMENTS
    return SAMPLE_DOCUMENTS
