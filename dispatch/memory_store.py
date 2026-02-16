#!/usr/bin/env python3
"""
Memory Store - Embedded vector store adapter for semantic memory

This module provides long-term memory capabilities for the Dispatch system
using an embedded vector store, enabling semantic search over events, specs,
and flight_rules without external dependencies.
"""

import json
import os
import pickle
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import math


@dataclass
class MemoryType:
    """Memory type categories for organization"""
    EVENT: str = "event"      # Task events, history
    SPEC: str = "spec"        # Specification summaries
    RULE: str = "rule"        # Flight rules, policies
    TASK: str = "task"        # Task outcomes, patterns
    ERROR: str = "error"      # Failure lessons, solutions


@dataclass
class MemoryEntry:
    """Represents a memory entry with metadata"""
    memory_id: str
    content: str
    memory_type: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without embedding to save space)"""
        result = asdict(self)
        result.pop('embedding', None)
        return {k: v for k, v in result.items() if v is not None}


class SimpleEmbedder:
    """
    Simple character-level and word-level embedding generator.

    Creates vectors based on character n-grams and word patterns.
    This is a pure Python implementation that works without external ML libraries.
    """

    def __init__(self, vector_dim: int = 256):
        """
        Initialize embedder

        Args:
            vector_dim: Dimension of output vectors
        """
        self.vector_dim = vector_dim

    def _text_to_features(self, text: str) -> Dict[int, float]:
        """
        Convert text to feature vector (bag of words + n-grams)

        Args:
            text: Input text

        Returns:
            Dictionary mapping feature indices to values
        """
        # Normalize text
        text = text.lower()
        words = text.split()

        features = {}

        # Word-based features (uni-grams)
        for word in words:
            # Hash word to feature index
            idx = hash(f"word_{word}") % self.vector_dim
            features[idx] = features.get(idx, 0) + 1

        # Character n-gram features (3-grams)
        text = ' '.join(words)
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            if len(trigram) == 3:
                idx = hash(f"trigram_{trigram}") % self.vector_dim
                features[idx] = features.get(idx, 0) + 0.5

        return features

    def _features_to_vector(self, features: Dict[int, float]) -> List[float]:
        """
        Convert features to normalized vector

        Args:
            features: Feature dictionary

        Returns:
            Normalized vector as list
        """
        vector = [0.0] * self.vector_dim

        # Fill vector from features
        for idx, val in features.items():
            vector[idx] = val

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: Input text to embed

        Returns:
            Vector representation as list of floats
        """
        features = self._text_to_features(text)
        return self._features_to_vector(features)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts

        Returns:
            List of vectors
        """
        return [self.embed(text) for text in texts]


class MemoryStore:
    """
    Embedded vector store for semantic memory

    Provides add, search, and delete operations with local file storage.
    Uses SQLite for persistence and cosine similarity for search.

    Example:
        store = MemoryStore()
        store.add("Successfully completed task S01", "task")
        results = store.search("task completion patterns")
    """

    def __init__(self, db_path: Optional[str] = None,
                 vector_dim: int = 256,
                 embedder: Optional[Any] = None):
        """
        Initialize MemoryStore

        Args:
            db_path: Path to SQLite database (default: ./memory_store.db)
            vector_dim: Dimension of vectors (default: 256)
            embedder: Custom embedder instance (default: SimpleEmbedder)
        """
        if db_path is None:
            db_path = os.path.join(os.getcwd(), "memory_store.db")

        self.db_path = db_path
        self.vector_dim = vector_dim
        self.embedder = embedder or SimpleEmbedder(vector_dim=vector_dim)

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Create index for faster filtering by type
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type
            ON memories(memory_type)
        """)

        # Create index for faster filtering by timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON memories(created_at)
        """)

        conn.commit()
        conn.close()

    def _generate_id(self, content: str) -> str:
        """Generate unique memory ID from content hash"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp = datetime.now().isoformat(timespec='seconds')
        return f"mem-{content_hash}-{timestamp.replace(':', '-')}"

    def _serialize_embedding(self, embedding: List[float]) -> bytes:
        """Serialize embedding to bytes for storage"""
        return pickle.dumps(embedding)

    def _deserialize_embedding(self, data: bytes) -> List[float]:
        """Deserialize embedding from storage"""
        return pickle.loads(data)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score between 0 and 1
        """
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        norm1 = math.sqrt(sum(v * v for v in vec1))
        norm2 = math.sqrt(sum(v * v for v in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def add(self, content: str, memory_type: str,
            metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a memory entry

        Args:
            content: The memory content to store
            memory_type: Type of memory (event, spec, rule, task, error)
            metadata: Additional metadata to attach

        Returns:
            Memory ID if successful

        Example:
            store.add("Task S01 completed successfully", "task")
        """
        # Generate embedding
        embedding = self.embedder.embed(content)

        # Generate ID
        memory_id = self._generate_id(content)
        created_at = datetime.now().isoformat()

        # Serialize metadata
        metadata_json = json.dumps(metadata) if metadata else None

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO memories
                (memory_id, content, memory_type, embedding, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                memory_id,
                content,
                memory_type,
                self._serialize_embedding(embedding),
                metadata_json,
                created_at
            ))
            conn.commit()
        finally:
            conn.close()

        return memory_id

    def search(self, query: str, memory_type: Optional[str] = None,
               limit: int = 10, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search memory entries by semantic similarity

        Args:
            query: Search query string
            memory_type: Filter by memory type (optional)
            limit: Maximum number of results (default: 10)
            min_score: Minimum similarity score (default: 0.0)

        Returns:
            List of memory entries with similarity scores

        Example:
            results = store.search("task completion patterns", "task", limit=5)
        """
        # Generate query embedding
        query_embedding = self.embedder.embed(query)

        results = []

        # Query database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Build query
            sql = "SELECT memory_id, content, memory_type, embedding, metadata, created_at FROM memories"
            params = []

            if memory_type:
                sql += " WHERE memory_type = ?"
                params.append(memory_type)

            cursor.execute(sql, params)

            # Calculate similarity for each result
            for row in cursor.fetchall():
                memory_id, content, mem_type, embedding_blob, metadata_json, created_at = row
                embedding = self._deserialize_embedding(embedding_blob)

                # Calculate similarity
                score = self._cosine_similarity(query_embedding, embedding)

                if score >= min_score:
                    # Parse metadata
                    metadata = json.loads(metadata_json) if metadata_json else None

                    results.append({
                        "memory_id": memory_id,
                        "content": content,
                        "memory_type": mem_type,
                        "score": score,
                        "metadata": metadata,
                        "created_at": created_at
                    })

        finally:
            conn.close()

        # Sort by similarity score (descending) and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory entry

        Args:
            memory_id: ID of the memory to delete

        Returns:
            True if successful, False otherwise

        Example:
            store.delete("mem-abc123-2024-01-15")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory entry by ID

        Args:
            memory_id: ID of the memory

        Returns:
            Memory entry dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT memory_id, content, memory_type, metadata, created_at
                FROM memories WHERE memory_id = ?
            """, (memory_id,))

            row = cursor.fetchone()
            if row:
                memory_id, content, mem_type, metadata_json, created_at = row
                metadata = json.loads(metadata_json) if metadata_json else None

                return {
                    "memory_id": memory_id,
                    "content": content,
                    "memory_type": mem_type,
                    "metadata": metadata,
                    "created_at": created_at
                }
            return None
        finally:
            conn.close()

    def get_all(self, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all memory entries

        Args:
            memory_type: Filter by memory type (optional)

        Returns:
            List of all memory entries

        Example:
            all_tasks = store.get_all(memory_type="task")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            sql = "SELECT memory_id, content, memory_type, metadata, created_at FROM memories"
            params = []

            if memory_type:
                sql += " WHERE memory_type = ?"
                params.append(memory_type)

            cursor.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                memory_id, content, mem_type, metadata_json, created_at = row
                metadata = json.loads(metadata_json) if metadata_json else None

                results.append({
                    "memory_id": memory_id,
                    "content": content,
                    "memory_type": mem_type,
                    "metadata": metadata,
                    "created_at": created_at
                })

            return results
        finally:
            conn.close()

    def count(self, memory_type: Optional[str] = None) -> int:
        """
        Count memory entries

        Args:
            memory_type: Filter by memory type (optional)

        Returns:
            Number of memory entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if memory_type:
                cursor.execute(
                    "SELECT COUNT(*) FROM memories WHERE memory_type = ?",
                    (memory_type,)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM memories")

            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory store statistics

        Returns:
            Dictionary with statistics

        Example:
            stats = store.get_stats()
            print(f"Total memories: {stats['total']}")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Total count
            cursor.execute("SELECT COUNT(*) FROM memories")
            total = cursor.fetchone()[0]

            # Count by type
            cursor.execute("""
                SELECT memory_type, COUNT(*) as count
                FROM memories
                GROUP BY memory_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            # Database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

            return {
                "total": total,
                "by_type": by_type,
                "vector_dim": self.vector_dim,
                "db_path": self.db_path,
                "db_size_bytes": db_size,
                "db_size_mb": db_size / (1024 * 1024)
            }
        finally:
            conn.close()

    def clear(self, memory_type: Optional[str] = None) -> int:
        """
        Clear memory entries

        Args:
            memory_type: Filter by memory type (optional, clears all if None)

        Returns:
            Number of entries deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if memory_type:
                cursor.execute("DELETE FROM memories WHERE memory_type = ?", (memory_type,))
            else:
                cursor.execute("DELETE FROM memories")

            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def rebuild_indexes(self) -> None:
        """Rebuild database indexes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("REINDEX")
            conn.commit()
        finally:
            conn.close()


def create_memory_store(db_path: Optional[str] = None,
                        vector_dim: int = 256) -> MemoryStore:
    """
    Factory function to create MemoryStore instance

    Args:
        db_path: Path to SQLite database (optional)
        vector_dim: Dimension of vectors (default: 256)

    Returns:
        MemoryStore instance

    Example:
        store = create_memory_store()
        store = create_memory_store(db_path="custom.db")
    """
    return MemoryStore(db_path=db_path, vector_dim=vector_dim)


# Legacy compatibility with previous DispatchMemory API
class DispatchMemory:
    """
    Legacy compatibility layer for DispatchMemory

    Provides the same interface as the previous Mem0-based implementation,
    but uses the embedded MemoryStore internally.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DispatchMemory (legacy compatibility)

        Args:
            config: Configuration dictionary (not used, for compatibility)
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._store = create_memory_store()

    def _check_available(self) -> bool:
        """Check if memory is available"""
        return self.enabled

    def add(self, data: str, user_id: str = "dispatch",
            memory_type: str = "task", metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a memory entry (legacy compatibility)

        Args:
            data: The memory content to store
            user_id: User/agent identifier (not used)
            memory_type: Type of memory
            metadata: Additional metadata to attach

        Returns:
            Memory ID if successful, None otherwise
        """
        if not self._check_available():
            return None

        # Map legacy types to new types
        type_mapping = {
            "task": "task",
            "error": "error",
            "user": "task",
            "system": "task"
        }
        new_type = type_mapping.get(memory_type, memory_type)

        # Add user_id to metadata if provided
        if metadata is None:
            metadata = {}
        metadata["user_id"] = user_id

        return self._store.add(data, new_type, metadata)

    def search(self, query: str, user_id: str = "dispatch",
               limit: int = 5, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search memory entries (legacy compatibility)

        Args:
            query: Search query string
            user_id: User/agent identifier (not used)
            limit: Maximum number of results
            memory_type: Filter by memory type

        Returns:
            List of memory entries with metadata
        """
        if not self._check_available():
            return []

        # Map legacy types
        type_mapping = {
            "task": "task",
            "error": "error",
            "user": "task",
            "system": "task"
        }
        new_type = type_mapping.get(memory_type, memory_type) if memory_type else None

        results = self._store.search(query, new_type, limit=limit)

        # Convert to legacy format
        legacy_results = []
        for r in results:
            legacy_results.append({
                "memory": r["content"],
                "metadata": r["metadata"] or {},
                "score": r["score"]
            })

        return legacy_results

    def get_all(self, user_id: str = "dispatch",
                memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all memory entries (legacy compatibility)

        Args:
            user_id: User/agent identifier (not used)
            memory_type: Filter by memory type

        Returns:
            List of all memory entries
        """
        if not self._check_available():
            return []

        type_mapping = {
            "task": "task",
            "error": "error",
            "user": "task",
            "system": "task"
        }
        new_type = type_mapping.get(memory_type, memory_type) if memory_type else None

        return self._store.get_all(new_type)

    def update(self, memory_id: str, data: str,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a memory entry (not implemented - use delete + add)

        Returns:
            False (not supported)
        """
        return False

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory entry (legacy compatibility)

        Args:
            memory_id: ID of the memory to delete

        Returns:
            True if successful, False otherwise
        """
        if not self._check_available():
            return False

        return self._store.delete(memory_id)

    def clear_all(self, user_id: str = "dispatch") -> int:
        """
        Clear all memories (legacy compatibility)

        Args:
            user_id: User/agent identifier (not used)

        Returns:
            Number of memories deleted
        """
        if not self._check_available():
            return 0

        return self._store.clear()

    def get_stats(self, user_id: str = "dispatch") -> Dict[str, Any]:
        """
        Get memory statistics (legacy compatibility)

        Args:
            user_id: User/agent identifier (not used)

        Returns:
            Dictionary with memory statistics
        """
        stats = self._store.get_stats()

        return {
            "total": stats["total"],
            "by_type": stats["by_type"],
            "enabled": self.enabled,
            "mem0_available": True  # Always available for embedded store
        }


def create_memory(config_path: Optional[str] = None,
                  config: Optional[Dict[str, Any]] = None) -> DispatchMemory:
    """
    Factory function to create DispatchMemory instance (legacy compatibility)

    Args:
        config_path: Path to config JSON file (optional)
        config: Direct config dictionary (optional)

    Returns:
        DispatchMemory instance
    """
    if config is None and config_path:
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception:
            config = {}

    return DispatchMemory(config)


# Convenience functions

def remember_task(task_id: str, outcome: str, pattern: str,
                  config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Convenience function to remember a task outcome"""
    memory = create_memory(config=config)
    memory_text = f"Task {task_id}: {outcome}. Pattern: {pattern}"
    return memory.add(memory_text, "dispatch", "task", {"task_id": task_id})


def remember_error(error_type: str, solution: str,
                   config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Convenience function to remember an error solution"""
    memory = create_memory(config=config)
    memory_text = f"Error: {error_type}. Solution: {solution}"
    return memory.add(memory_text, "dispatch", "error", {"error_type": error_type})


def search_similar_tasks(query: str, limit: int = 3,
                         config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Convenience function to search for similar task patterns"""
    memory = create_memory(config=config)
    return memory.search(query, "dispatch", limit=limit, memory_type="task")


def search_error_solutions(query: str, limit: int = 3,
                           config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Convenience function to search for error solutions"""
    memory = create_memory(config=config)
    return memory.search(query, "dispatch", limit=limit, memory_type="error")


if __name__ == "__main__":
    # Example usage
    import sys

    print("Memory Store - Embedded Vector Store\n")
    print("=" * 50)

    # Create store
    store = MemoryStore()
    print("\n1. Created memory store")
    print(f"   Database: {store.db_path}")
    print(f"   Vector dimension: {store.vector_dim}")

    # Add some memories
    print("\n2. Adding memories...")
    store.add("Successfully completed task S01 with async pattern", "task")
    store.add("Fixed import error by installing missing package", "error")
    store.add("Database connection timeout resolved by increasing pool size", "error")
    store.add("Task S02 failed due to missing dependencies", "task")
    print("   Added 4 memories")

    # Search
    print("\n3. Searching for 'async patterns':")
    results = store.search("async patterns", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['content']}")

    # Search errors
    print("\n4. Searching for 'connection issues':")
    results = store.search("connection issues", memory_type="error", limit=2)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['content']}")

    # Stats
    print("\n5. Memory store statistics:")
    stats = store.get_stats()
    print(f"   Total memories: {stats['total']}")
    print(f"   By type: {stats['by_type']}")
    print(f"   Database size: {stats['db_size_mb']:.2f} MB")
