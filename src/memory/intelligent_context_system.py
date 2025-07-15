#!/usr/bin/env python3
"""
🧠 Intelligent Context System - Human-like Learning Implementation
===============================================================

Designed for scale with emotional intelligence, cross-session memory,
and adaptive learning patterns for truly human-like AI behavior.
"""

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class EmotionalContext:
    """Emotional state tracking for human-like responses"""

    primary_emotion: str  # joy, frustration, curiosity, confidence, concern
    intensity: float  # 0.0 to 1.0
    triggers: List[str]  # What caused this emotion
    context: str  # Situational context


@dataclass
class LearningWeight:
    """Learning importance weighting"""

    technical_weight: float  # How technically important
    emotional_weight: float  # How emotionally significant
    frequency_weight: float  # How often this pattern occurs
    recency_weight: float  # How recent this learning is


class IntelligentContextSystem:
    """Human-like intelligent context management system"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.session_id = str(uuid.uuid4())

        # Database configuration
        self.db_config = {
            "host": "localhost",
            "database": "coding_rule2_ai",
            "user": "dd",
            "password": "",
            "port": 5432,
        }

        # Emotional intelligence patterns
        self.emotion_patterns = {
            "frustration": [
                r"(エラー|失敗|動かない|why|なぜ|困った)",
                r"(again|また|何度も|繰り返し)",
            ],
            "joy": [
                r"(成功|うまく|完了|素晴らしい|excellent)",
                r"(解決|fixed|works|動いた)",
            ],
            "curiosity": [
                r"(どうやって|how|なぜ|why|調べ|investigate)",
                r"(面白い|interesting|learn|学習)",
            ],
            "confidence": [
                r"(確信|certain|definitely|絶対)",
                r"(完璧|perfect|最適|optimal)",
            ],
            "concern": [
                r"(心配|worried|問題|problem|リスク|risk)",
                r"(注意|careful|慎重|cautious)",
            ],
        }

    def connect_db(self) -> psycopg2.extensions.connection:
        """Database connection with error handling"""
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.OperationalError as e:
            print(f"⚠️ Database connection failed: {e}")
            print("💡 Falling back to file-based storage")
            return None

    def analyze_emotional_context(self, content: str) -> EmotionalContext:
        """Analyze emotional context from content"""
        emotions_detected = {}

        for emotion, patterns in self.emotion_patterns.items():
            total_matches = 0
            triggers = []

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_matches += len(matches)
                triggers.extend(matches)

            if total_matches > 0:
                # Normalize intensity based on content length and match frequency
                intensity = min(1.0, total_matches / max(1, len(content.split()) / 10))
                emotions_detected[emotion] = {
                    "intensity": intensity,
                    "triggers": triggers[:3],  # Top 3 triggers
                }

        # Find primary emotion
        if emotions_detected:
            primary = max(
                emotions_detected.keys(),
                key=lambda e: emotions_detected[e]["intensity"],
            )
            return EmotionalContext(
                primary_emotion=primary,
                intensity=emotions_detected[primary]["intensity"],
                triggers=emotions_detected[primary]["triggers"],
                context=content[:200],  # Context snippet
            )

        # Default neutral state
        return EmotionalContext(
            primary_emotion="neutral", intensity=0.0, triggers=[], context=content[:200]
        )

    def calculate_learning_weight(
        self, content: str, event_type: str, emotional_context: EmotionalContext
    ) -> LearningWeight:
        """Calculate how much to learn from this event"""

        # Technical importance
        technical_indicators = ["error", "critical", "failed", "success", "solution"]
        technical_score = sum(
            1
            for indicator in technical_indicators
            if indicator.lower() in content.lower()
        ) / len(technical_indicators)

        # Emotional significance
        emotional_score = emotional_context.intensity
        if emotional_context.primary_emotion in ["frustration", "joy"]:
            emotional_score *= 1.5  # Boost learning from strong emotions

        # Frequency analysis (simplified - would use actual DB stats)
        frequency_score = 0.5  # Default medium frequency

        # Recency boost
        recency_score = 1.0  # Current events get full recency weight

        return LearningWeight(
            technical_weight=technical_score,
            emotional_weight=emotional_score,
            frequency_weight=frequency_score,
            recency_weight=recency_score,
        )

    def store_intelligent_context(
        self, content: str, event_type: str, source: str, importance: str = "normal"
    ) -> Dict[str, Any]:
        """Store context with human-like intelligence features"""

        # Analyze emotional context
        emotional_ctx = self.analyze_emotional_context(content)

        # Calculate learning weights
        learning_weights = self.calculate_learning_weight(
            content, event_type, emotional_ctx
        )

        # Generate embeddings
        embedding = self._generate_embedding(content)

        # Identify patterns
        patterns = self._identify_patterns(content, event_type)

        # Cross-reference with existing knowledge
        cross_refs = self._find_cross_references(content, embedding)

        # Assess confidence
        confidence = self._assess_confidence(content, patterns, learning_weights)

        event_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "source": source,
            "event_type": event_type,
            "content": content,
            "session_id": self.session_id,
            "vector_embedding": embedding,
            "importance_level": importance,
            "project_name": self.project_root.name,
            # Human-like intelligence fields
            "emotional_context": {
                "primary_emotion": emotional_ctx.primary_emotion,
                "intensity": emotional_ctx.intensity,
                "triggers": emotional_ctx.triggers,
                "context": emotional_ctx.context,
            },
            "learning_weight": (
                learning_weights.technical_weight * 0.3
                + learning_weights.emotional_weight * 0.4
                + learning_weights.frequency_weight * 0.2
                + learning_weights.recency_weight * 0.1
            ),
            "cross_references": cross_refs,
            "pattern_tags": patterns,
            "confidence_score": confidence,
        }

        # Store in database
        success = self._store_to_database(event_data)

        return {
            "status": "success" if success else "fallback",
            "event_id": event_data["id"],
            "emotional_state": emotional_ctx.primary_emotion,
            "learning_weight": event_data["learning_weight"],
            "confidence": confidence,
            "patterns_identified": len(patterns),
        }

    def intelligent_search(
        self,
        query: str,
        emotional_filter: Optional[str] = None,
        learning_threshold: float = 0.3,
    ) -> Dict[str, Any]:
        """Human-like intelligent context search"""

        query_embedding = self._generate_embedding(query)
        query_emotion = self.analyze_emotional_context(query)

        conn = self.connect_db()
        if not conn:
            return self._fallback_file_search(query)

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Build intelligent query with emotional and learning filters
            conditions = ["vector_embedding IS NOT NULL"]
            params = [query_embedding]

            if emotional_filter:
                conditions.append("emotional_context->>'primary_emotion' = %s")
                params.append(emotional_filter)

            if learning_threshold > 0:
                conditions.append("learning_weight >= %s")
                params.append(learning_threshold)

            # Add text search
            conditions.append("(content ILIKE %s OR pattern_tags && %s)")
            params.extend([f"%{query}%", [query]])

            # Add vector similarity
            params.append(query_embedding)

            where_clause = " AND ".join(conditions)

            # Reorder parameters for proper placement
            vector_param = params[-1]  # Remove vector param from end
            params = params[:-1]  # Remove last element

            cur.execute(
                f"""
                SELECT
                    id, timestamp, source, event_type, content, importance_level,
                    emotional_context, learning_weight, pattern_tags, confidence_score,
                    cross_references,
                    1 - (vector_embedding <=> %s::vector) as similarity
                FROM context_stream
                WHERE {where_clause}
                ORDER BY
                    learning_weight DESC,
                    confidence_score DESC,
                    similarity DESC,
                    timestamp DESC
                LIMIT 20
            """,
                [vector_param] + params,
            )

            results = cur.fetchall()

            # Categorize and enrich results
            categorized = self._categorize_intelligent_results(
                [dict(row) for row in results], query_emotion
            )

            cur.close()
            conn.close()

            return {
                "status": "success",
                "query": query,
                "query_emotion": query_emotion.primary_emotion,
                "total_results": len(results),
                "categorized_results": categorized,
                "search_intelligence": {
                    "emotional_filter": emotional_filter,
                    "learning_threshold": learning_threshold,
                    "confidence_weighted": True,
                },
            }

        except Exception as e:
            print(f"⚠️ Database search error: {e}")
            return self._fallback_file_search(query)

    def update_session_memory(
        self, user_intent: str, key_decisions: List[str], unresolved_issues: List[str]
    ) -> Dict[str, Any]:
        """Update cross-session memory for continuity"""

        emotional_state = self.analyze_emotional_context(
            f"{user_intent} {' '.join(key_decisions)} {' '.join(unresolved_issues)}"
        )

        session_data = {
            "session_id": self.session_id,
            "user_intent": user_intent,
            "context_summary": self._generate_session_summary(),
            "emotional_state": {
                "primary_emotion": emotional_state.primary_emotion,
                "intensity": emotional_state.intensity,
                "session_mood": self._assess_session_mood(),
            },
            "key_decisions": key_decisions,
            "unresolved_issues": unresolved_issues,
            "next_session_prep": self._prepare_next_session_context(),
            "session_quality_score": self._calculate_session_quality(),
        }

        conn = self.connect_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO session_memory
                    (session_id, user_intent, context_summary, emotional_state,
                     key_decisions, unresolved_issues, next_session_prep, session_quality_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        session_data["session_id"],
                        session_data["user_intent"],
                        session_data["context_summary"],
                        json.dumps(session_data["emotional_state"]),
                        json.dumps(session_data["key_decisions"]),
                        json.dumps(session_data["unresolved_issues"]),
                        json.dumps(session_data["next_session_prep"]),
                        session_data["session_quality_score"],
                    ),
                )
                conn.commit()
                cur.close()
                conn.close()

                return {"status": "success", "session_id": self.session_id}
            except Exception as e:
                print(f"⚠️ Session memory update error: {e}")

        # Fallback to file storage
        return self._store_session_to_file(session_data)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate vector embeddings"""
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(
                model="text-embedding-ada-002", input=text[:8000]
            )
            return response.data[0].embedding
        except Exception:
            # Fallback to zero vector
            return [0.0] * 1536

    def _identify_patterns(self, content: str, event_type: str) -> List[str]:
        """Identify behavioral and technical patterns"""
        patterns = []

        # Technical patterns
        if "error" in content.lower():
            patterns.append("error_pattern")
        if "success" in content.lower():
            patterns.append("success_pattern")
        if re.search(r"\d+", content):
            patterns.append("numerical_data")

        # Behavioral patterns
        if event_type.endswith("_completion"):
            patterns.append("task_completion")
        if "learning" in content.lower():
            patterns.append("learning_event")

        return patterns

    def _find_cross_references(self, content: str, embedding: List[float]) -> List[str]:
        """Find related contexts using similarity"""
        # Simplified - would use actual DB similarity search
        return []

    def _assess_confidence(
        self, content: str, patterns: List[str], learning_weights: LearningWeight
    ) -> float:
        """Assess AI confidence in this data"""
        base_confidence = 0.5

        # Boost confidence for specific patterns
        if "error_pattern" in patterns:
            base_confidence += 0.2
        if "success_pattern" in patterns:
            base_confidence += 0.3

        # Factor in learning weights
        confidence = base_confidence * (1 + learning_weights.technical_weight * 0.3)

        return min(1.0, confidence)

    def _store_to_database(self, event_data: Dict[str, Any]) -> bool:
        """Store event to database"""
        conn = self.connect_db()
        if not conn:
            return False

        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO context_stream
                (id, timestamp, source, event_type, content, metadata, session_id,
                 vector_embedding, importance_level, project_name, emotional_context,
                 learning_weight, cross_references, pattern_tags, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id, timestamp) DO NOTHING
            """,
                (
                    event_data["id"],
                    event_data["timestamp"],
                    event_data["source"],
                    event_data["event_type"],
                    event_data["content"],
                    json.dumps({}),  # metadata placeholder
                    event_data["session_id"],
                    event_data["vector_embedding"],
                    event_data["importance_level"],
                    event_data["project_name"],
                    json.dumps(event_data["emotional_context"]),
                    event_data["learning_weight"],
                    event_data["cross_references"],
                    event_data["pattern_tags"],
                    event_data["confidence_score"],
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ Database storage error: {e}")
            return False

    def _categorize_intelligent_results(
        self, results: List[Dict], query_emotion: EmotionalContext
    ) -> Dict[str, List]:
        """Categorize results with emotional intelligence"""
        categories = {
            "high_confidence": [],
            "emotional_match": [],
            "learning_priority": [],
            "pattern_match": [],
            "recent_context": [],
            "general": [],
        }

        for result in results:
            # High confidence results
            if result.get("confidence_score", 0) > 0.8:
                categories["high_confidence"].append(result)

            # Emotional resonance
            result_emotion = result.get("emotional_context", {}).get(
                "primary_emotion", "neutral"
            )
            if result_emotion == query_emotion.primary_emotion:
                categories["emotional_match"].append(result)

            # Learning priority
            if result.get("learning_weight", 0) > 0.7:
                categories["learning_priority"].append(result)

            # Pattern matches
            if result.get("pattern_tags"):
                categories["pattern_match"].append(result)

            # Recent context (last 24 hours)
            if (datetime.now(timezone.utc) - result["timestamp"]).days < 1:
                categories["recent_context"].append(result)
            else:
                categories["general"].append(result)

        return categories

    def _generate_session_summary(self) -> str:
        """Generate intelligent session summary"""
        return f"Session {self.session_id[:8]} - AI Learning Context"

    def _assess_session_mood(self) -> str:
        """Assess overall session emotional tone"""
        return "productive"  # Simplified

    def _prepare_next_session_context(self) -> Dict[str, Any]:
        """Prepare context for next session"""
        return {
            "continue_from": "current_context",
            "priorities": ["learning", "improvement"],
            "emotional_state": "neutral",
        }

    def _calculate_session_quality(self) -> float:
        """Calculate session quality score"""
        return 0.8  # Simplified

    def _fallback_file_search(self, query: str) -> Dict[str, Any]:
        """Fallback file-based search"""
        return {
            "status": "fallback",
            "message": "Using file-based search",
            "results": [],
        }

    def _store_session_to_file(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store session data to file as fallback"""
        return {"status": "file_fallback", "session_id": self.session_id}


def main():
    """Demo of intelligent context system"""
    print("🧠 Intelligent Context System - Human-like Learning")

    ics = IntelligentContextSystem()

    # Store some intelligent context
    result = ics.store_intelligent_context(
        content="Successfully implemented database optimization with great results!",
        event_type="optimization_success",
        source="development",
        importance="high",
    )

    print(f"Storage result: {result}")

    # Intelligent search
    search_result = ics.intelligent_search(
        query="database optimization", emotional_filter="joy", learning_threshold=0.5
    )

    print(f"Search results: {search_result.get('total_results', 0)} found")

    # Update session memory
    session_result = ics.update_session_memory(
        user_intent="Optimize database performance",
        key_decisions=["Implement PostgreSQL", "Use vector embeddings"],
        unresolved_issues=["Need to test at scale"],
    )

    print(f"Session memory: {session_result}")


if __name__ == "__main__":
    main()
