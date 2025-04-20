import datetime
import logging
import random
from typing import Dict, List, Any, Optional

from it_incident_response.protocols.mcp import MCPTool, MCPToolType

logger = logging.getLogger("it-incident-response.tools.knowledge-base")

class KnowledgeBaseTool(MCPTool):
    """Knowledge Base tool implementation"""

    def __init__(self):
        super().__init__(
            tool_id="knowledge-base",
            tool_type=MCPToolType.KNOWLEDGE_BASE,
            name="Knowledge Base",
            description="Accesses incident resolution knowledge and best practices",
            api_endpoint="http://localhost:8001/mcp/knowledge-base",
            parameters={
                "query": {"type": "string", "description": "Search query for the knowledge base"},
                "tags": {"type": "array", "description": "Tags to filter articles by", "default": []},
                "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 5}
            }
        )
        # Pre-populated knowledge base for simulation
        self.knowledge_base = self._initialize_knowledge_base()

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute knowledge base search with provided parameters"""
        if not params:
            params = {}

        query = params.get("query", "")
        if not query:
            return {"status": "error", "message": "Missing required parameter: query"}

        tags = params.get("tags", [])
        max_results = params.get("max_results", 5)

        # Search knowledge base
        results = self.search_knowledge_base(query, tags, max_results)

        return {
            "status": "success",
            "data": {
                "query": query,
                "result_count": len(results),
                "articles": results,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }

    def search_knowledge_base(self, query: str, tags: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant articles"""
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        # Calculate relevance scores
        scored_articles = []
        for article in self.knowledge_base:
            # Calculate base score from title and content matches
            score = 0

            # Title match (weighted higher)
            if query_lower in article["title"].lower():
                score += 0.5

            # Content match
            if query_lower in article["content"].lower():
                score += 0.3

            # Tag match
            article_tags = article.get("tags", [])
            if article_tags:
                matching_tags = set(tags).intersection(set(article_tags))
                if matching_tags:
                    score += 0.2 * len(matching_tags) / len(tags) if tags else 0.2

            # Add small random variation for simulation
            score += random.uniform(-0.05, 0.05)

            # Only include articles with non-zero relevance
            if score > 0:
                # Create a copy of the article with the relevance score
                article_with_score = article.copy()
                article_with_score["relevance"] = round(min(score, 1.0), 2)  # Cap at 1.0
                scored_articles.append(article_with_score)

        # Sort by relevance and limit to max_results
        sorted_articles = sorted(scored_articles, key=lambda x: x["relevance"], reverse=True)
        return sorted_articles[:max_results]

    def _initialize_knowledge_base(self) -> List[Dict[str, Any]]:
        """Initialize a simulated knowledge base with articles"""
        return [
            {
                "id": "KB-1001",
                "title": "Resolving Database Connection Timeouts",
                "content": "Database connection timeouts are often caused by network latency, connection pool exhaustion, or database server overload. This article outlines steps to diagnose and resolve these issues.",
                "tags": ["database", "timeout", "connection", "troubleshooting"],
                "resolution_steps": [
                    "Check database server status and resource utilization",
                    "Verify network connectivity and latency between application and database servers",
                    "Inspect connection pool settings and increase size if necessary",
                    "Review recent configuration changes that might have affected connectivity",
                    "Implement connection retry logic with exponential backoff"
                ],
                "created_at": "2024-10-15T10:00:00Z",
                "updated_at": "2025-02-20T15:30:00Z"
            },
            {
                "id": "KB-1002",
                "title": "API Gateway 503 Errors Troubleshooting Guide",
                "content": "503 Service Unavailable errors from API Gateways typically indicate backend service issues or gateway configuration problems. This guide provides a systematic approach to resolving these errors.",
                "tags": ["api", "gateway", "503", "service unavailable", "troubleshooting"],
                "resolution_steps": [
                    "Check health and status of backend services",
                    "Verify gateway configuration and routing rules",
                    "Review recent deployments or configuration changes",
                    "Check for circuit breaker activation and thresholds",
                    "Temporarily scale up backend services to handle load if needed"
                ],
                "created_at": "2024-11-05T09:15:00Z",
                "updated_at": "2025-01-18T11:45:00Z"
            },
            {
                "id": "KB-1003",
                "title": "Diagnosing and Fixing Memory Leaks in Java Applications",
                "content": "Memory leaks in Java applications can cause performance degradation and eventual crashes. This article explains how to identify, diagnose, and resolve memory leaks in production Java services.",
                "tags": ["java", "memory leak", "performance", "troubleshooting"],
                "resolution_steps": [
                    "Capture and analyze heap dumps during high memory usage",
                    "Use memory profilers to identify objects not being garbage collected",
                    "Review code for common memory leak patterns (static collections, unclosed resources)",
                    "Implement proper resource cleanup in finally blocks or try-with-resources",
                    "Consider weak references for caching implementations"
                ],
                "created_at": "2024-09-20T14:30:00Z",
                "updated_at": "2025-03-05T10:20:00Z"
            },
            {
                "id": "KB-1004",
                "title": "Storage Cluster Disk Space Management",
                "content": "Managing disk space in storage clusters is critical to maintaining system availability. This guide covers both emergency response to critical disk space issues and long-term management strategies.",
                "tags": ["storage", "disk space", "clustering", "maintenance"],
                "resolution_steps": [
                    "Identify and remove temporary files and logs",
                    "Run data retention policies immediately to free space",
                    "Add emergency storage capacity if available",
                    "Implement or adjust data retention and archiving policies",
                    "Set up proactive alerts at lower threshold levels"
                ],
                "created_at": "2024-08-15T11:45:00Z",
                "updated_at": "2025-02-28T16:10:00Z"
            },
            {
                "id": "KB-1005",
                "title": "SSL Certificate Management and Renewal Process",
                "content": "Proper SSL certificate management is essential for secure communications. This document outlines best practices for certificate monitoring, renewal, and emergency replacement.",
                "tags": ["ssl", "security", "certificate", "expiration"],
                "resolution_steps": [
                    "Verify certificate details and expiration dates",
                    "Generate CSR and obtain new certificate from CA",
                    "Test new certificate in staging environment",
                    "Deploy new certificate and restart services as needed",
                    "Update certificate monitoring to ensure alerts trigger earlier"
                ],
                "created_at": "2024-12-10T09:30:00Z",
                "updated_at": "2025-03-15T14:45:00Z"
            },
            {
                "id": "KB-1006",
                "title": "Network Latency Troubleshooting Between Application Tiers",
                "content": "Network latency between application tiers can severely impact system performance. This article provides methods to diagnose and address network latency issues in multi-tier architectures.",
                "tags": ["network", "latency", "performance", "troubleshooting"],
                "resolution_steps": [
                    "Measure latency between system components using network diagnostic tools",
                    "Check for network congestion or hardware issues",
                    "Review network configuration including QoS settings",
                    "Consider geographic distribution of services if cross-region",
                    "Implement caching strategies to reduce dependency on network calls"
                ],
                "created_at": "2024-10-25T13:20:00Z",
                "updated_at": "2025-01-30T11:15:00Z"
            },
            {
                "id": "KB-1007",
                "title": "Optimizing Database Connection Pools for High Load",
                "content": "Properly configured connection pools are crucial for database performance under high load. This guide explains how to optimize connection pool settings based on workload characteristics.",
                "tags": ["database", "connection pool", "performance", "optimization"],
                "resolution_steps": [
                    "Analyze application connection usage patterns",
                    "Adjust minimum and maximum pool sizes based on concurrent users",
                    "Configure connection validation and timeout settings",
                    "Implement statement caching if supported",
                    "Consider separate pools for different types of operations",
                    "Monitor pool metrics and adjust based on actual usage patterns"
                ],
                "created_at": "2024-07-18T10:40:00Z",
                "updated_at": "2025-02-10T09:25:00Z"
            }
        ]
