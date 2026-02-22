#!/usr/bin/env python3
"""
Event Bus - Event-driven communication system for modules

This module provides a publish-subscribe event bus that enables
loose coupling between modules. Modules can publish events and
subscribe to events they're interested in.
"""

import json
import logging
import queue
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Memory integration - lazy import to avoid circular dependencies
_memory_store = None


def _get_memory_store():
    """Get or create memory store instance (lazy init)"""
    global _memory_store
    if _memory_store is None:
        try:
            from memory_store import MemoryStore

            _memory_store = MemoryStore()
            logger.info("Memory store initialized in EventBus")
        except Exception as e:
            logger.warning(f"Memory store not available: {e}")
            return None
    return _memory_store


def _index_event_to_memory(event_type: str, data: Dict[str, Any], source: str):
    """Automatically index event to memory store"""
    store = _get_memory_store()
    if store is None:
        return

    try:
        # Create searchable content from event
        content_parts = [f"Event: {event_type}"]

        # Add relevant data fields
        for key in ["task_id", "error", "summary", "project", "status", "message"]:
            if key in data:
                content_parts.append(f"{key}: {data[key]}")

        content = " | ".join(content_parts)

        # Determine memory type
        if "error" in event_type or "fail" in str(data):
            mem_type = "error"
        elif "task" in event_type:
            mem_type = "task"
        else:
            mem_type = "event"

        # Add to memory
        store.add(content, mem_type, {"source": source, "event_type": event_type})
        logger.debug(f"Indexed event to memory: {event_type}")
    except Exception as e:
        logger.warning(f"Failed to index event to memory: {e}")


@dataclass
class Event:
    """Represents an event in the system"""

    event_type: str
    data: Dict[str, Any]
    timestamp: str
    source: str
    event_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source,
        }


class EventBus:
    """
    Event-driven communication bus for modules

    Provides publish-subscribe pattern for decoupled communication:
    - Publish: Send events to all subscribers
    - Subscribe: Register callback for specific event types
    - Unsubscribe: Remove callbacks

    Event Types:
    - task.started: Task execution started
    - task.completed: Task execution completed successfully
    - task.failed: Task execution failed
    - error.detected: Error detected by any module
    - fix.applied: Fix applied to resolve an issue
    - finding.found: Auditor found a code issue
    - learning.stored: New knowledge stored in memory
    - action.retried: Action was retried
    - action.escalated: Action escalated to human

    Example:
        bus = EventBus()

        # Subscribe to events
        def on_error(data):
            print(f"Error: {data['error']}")
        bus.subscribe("error.detected", on_error)

        # Publish event
        bus.publish("error.detected", {"error": "Something failed", "source": "module"})
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize EventBus

        Args:
            config: Configuration dictionary with options:
                - queue_size (int): Maximum queue size (default: 1000)
                - async_mode (bool): Enable async event processing (default: True)
                - retry_failed (bool): Retry failed event delivery (default: True)
                - max_retries (int): Maximum retry attempts (default: 3)
                - event_log_path (str): Path to event log file (optional)
        """
        self.config = config or {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_queue = queue.Queue(maxsize=self.config.get("queue_size", 1000))
        self.async_mode = self.config.get("async_mode", True)
        self.retry_failed = self.config.get("retry_failed", True)
        self.max_retries = self.config.get("max_retries", 3)
        self.event_log_path = self.config.get("event_log_path")

        # Event counter for unique IDs
        self._event_counter = 0
        self._counter_lock = threading.Lock()

        # Event history for debugging
        self.event_history: List[Dict[str, Any]] = []
        self._history_lock = threading.Lock()
        self._max_history = 1000

        # Statistics
        self.stats = {"published": 0, "delivered": 0, "failed": 0, "retried": 0}

        # Background thread for async processing
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None

        if self.async_mode:
            self.start()

        logger.info(f"EventBus initialized (async={self.async_mode})")

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        with self._counter_lock:
            self._event_counter += 1
            return f"evt-{int(time.time() * 1000)}-{self._event_counter}"

    def subscribe(
        self, event_type: str, callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to an event type

        Args:
            event_type: Event type to subscribe to
            callback: Function to call when event is published

        Returns:
            Subscription ID for unsubscribing later

        Example:
            def on_task_started(data):
                print(f"Task {data['task_id']} started")
            bus.subscribe("task.started", on_task_started)
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")

        subscription_id = f"sub-{event_type}-{len(self.subscribers[event_type])}"

        # Store callback with metadata
        self.subscribers[event_type].append(
            {
                "id": subscription_id,
                "callback": callback,
                "subscribed_at": datetime.now().isoformat(),
            }
        )

        logger.info(f"Subscribed {subscription_id} to {event_type}")
        return subscription_id

    def unsubscribe(self, event_type: str, subscription_id: str) -> bool:
        """
        Unsubscribe from an event type

        Args:
            event_type: Event type to unsubscribe from
            subscription_id: Subscription ID returned by subscribe()

        Returns:
            True if unsubscribed successfully, False otherwise
        """
        for i, sub in enumerate(self.subscribers[event_type]):
            if sub["id"] == subscription_id:
                del self.subscribers[event_type][i]
                logger.info(f"Unsubscribed {subscription_id} from {event_type}")
                return True
        return False

    def publish(
        self, event_type: str, data: Dict[str, Any], source: str = "unknown"
    ) -> Optional[str]:
        """
        Publish an event to all subscribers

        Args:
            event_type: Type of event (e.g., "task.started", "error.detected")
            data: Event data as dictionary
            source: Source of the event (module/component name)

        Returns:
            Event ID if published successfully, None if queue is full

        Example:
            bus.publish("task.started", {
                "task_id": "S01",
                "description": "Build infrastructure"
            }, source="dispatch")
        """
        event_id = self._generate_event_id()
        timestamp = datetime.now().isoformat()

        # Create event
        event = {
            "id": event_id,
            "type": event_type,
            "data": data,
            "timestamp": timestamp,
            "source": source,
        }

        # Add to history
        with self._history_lock:
            self.event_history.append(event)
            if len(self.event_history) > self._max_history:
                self.event_history.pop(0)

        # Log event
        self._log_event(event)

        # Index event to memory store for semantic search
        _index_event_to_memory(event_type, data, source)

        # Update stats
        self.stats["published"] += 1

        if self.async_mode:
            # Add to queue for async processing
            try:
                self.event_queue.put(event, block=False)
                logger.debug(f"Published {event_type} (id={event_id}) to queue")
                return event_id
            except queue.Full:
                logger.error(f"Event queue full, dropping {event_type}")
                return None
        else:
            # Process synchronously
            self._process_event(event)
            return event_id

    def _log_event(self, event: Dict[str, Any]) -> None:
        """Log event to file if configured"""
        if self.event_log_path:
            try:
                log_file = Path(self.event_log_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                logger.error(f"Failed to log event: {e}")

    def _process_event(self, event: Dict[str, Any]) -> None:
        """
        Process a single event by notifying all subscribers

        Args:
            event: Event dictionary with id, type, data, timestamp, source
        """
        event_type = event["type"]
        data = event["data"]

        # Get subscribers for this event type
        subscribers = self.subscribers.get(event_type, [])

        if not subscribers:
            logger.debug(f"No subscribers for {event_type}")
            return

        # Notify each subscriber
        for sub in subscribers:
            callback = sub["callback"]
            try:
                callback(data.copy())  # Copy to prevent mutations
                self.stats["delivered"] += 1
            except Exception as e:
                self.stats["failed"] += 1
                logger.error(f"Subscriber {sub['id']} failed: {e}", exc_info=True)

                # Retry if configured
                if self.retry_failed:
                    self._retry_event(event, sub, attempts=1)

    def _retry_event(
        self, event: Dict[str, Any], subscriber: Dict[str, Any], attempts: int = 1
    ) -> None:
        """
        Retry delivering event to a subscriber

        Args:
            event: Event to retry
            subscriber: Subscriber dictionary
            attempts: Current attempt number
        """
        if attempts > self.max_retries:
            logger.error(f"Max retries reached for {subscriber['id']}")
            return

        try:
            # Wait before retry (exponential backoff)
            wait_time = 2**attempts
            time.sleep(wait_time)

            subscriber["callback"](event["data"].copy())
            self.stats["delivered"] += 1
            self.stats["retried"] += 1
            logger.info(f"Retry successful for {subscriber['id']} (attempt {attempts})")

        except Exception as e:
            logger.error(f"Retry {attempts} failed for {subscriber['id']}: {e}")
            self._retry_event(event, subscriber, attempts + 1)

    def _worker_loop(self) -> None:
        """
        Worker thread loop for processing events asynchronously
        """
        logger.info("EventBus worker thread started")

        while self._running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1.0)

                # Process event
                self._process_event(event)

                # Mark task as done
                self.event_queue.task_done()

            except queue.Empty:
                # Timeout is normal, continue loop
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {e}", exc_info=True)

        logger.info("EventBus worker thread stopped")

    def start(self) -> None:
        """Start the background worker thread"""
        if self._running:
            logger.warning("EventBus worker already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop, daemon=True, name="EventBus-Worker"
        )
        self._worker_thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        """
        Stop the background worker thread

        Args:
            timeout: Maximum time to wait for thread to finish
        """
        if not self._running:
            return

        logger.info("Stopping EventBus worker thread...")
        self._running = False

        # Wait for queue to empty
        self.event_queue.join()

        # Wait for thread to finish
        if self._worker_thread:
            self._worker_thread.join(timeout=timeout)
            if self._worker_thread.is_alive():
                logger.warning("Worker thread did not stop gracefully")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get EventBus statistics

        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "subscribers_by_type": {
                evt_type: len(subs) for evt_type, subs in self.subscribers.items()
            },
            "history_size": len(self.event_history),
        }

    def get_history(
        self, event_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get event history

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        with self._history_lock:
            events = self.event_history.copy()

        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e["type"] == event_type]

        # Return most recent events
        return events[-limit:]

    def clear_history(self) -> None:
        """Clear event history"""
        with self._history_lock:
            self.event_history.clear()
        logger.info("Event history cleared")

    def wait_for_event(
        self,
        event_type: str,
        timeout: float = 10.0,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a specific event to be published

        Args:
            event_type: Event type to wait for
            timeout: Maximum time to wait in seconds
            condition: Optional function to test event data

        Returns:
            Event data if event found, None if timeout
        """
        event_found = threading.Event()
        event_data: Optional[Dict[str, Any]] = None

        def handler(data: Dict[str, Any]) -> None:
            nonlocal event_data
            if condition is None or condition(data):
                event_data = data
                event_found.set()

        # Subscribe
        subscription_id = self.subscribe(event_type, handler)

        # Wait
        event_found.wait(timeout=timeout)

        # Unsubscribe
        self.unsubscribe(event_type, subscription_id)

        return event_data


def create_event_bus(config: Optional[Dict[str, Any]] = None) -> EventBus:
    """
    Factory function to create EventBus instance

    Args:
        config: Configuration dictionary

    Returns:
        EventBus instance
    """
    return EventBus(config=config)


# Standard event type constants
class EventTypes:
    """Standard event type constants"""

    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    ERROR_DETECTED = "error.detected"
    FIX_APPLIED = "fix.applied"
    FINDING_FOUND = "finding.found"
    LEARNING_STORED = "learning.stored"
    ACTION_RETRIED = "action.retried"
    ACTION_ESCALATED = "action.escalated"


if __name__ == "__main__":
    # Example usage
    import sys

    print("Event Bus - Event-driven Communication System\n")
    print("=" * 60)

    # Create event bus
    bus = EventBus()

    # Subscribe to events
    def on_task_started(data):
        print(
            f"[Task Started] {data.get('task_id', 'unknown')}: {data.get('description', '')}"
        )

    def on_error(data):
        print(
            f"[Error] {data.get('error', 'Unknown error')} from {data.get('source', 'unknown')}"
        )

    def on_completed(data):
        print(
            f"[Completed] {data.get('task_id', 'unknown')} in {data.get('duration', 0):.2f}s"
        )

    bus.subscribe(EventTypes.TASK_STARTED, on_task_started)
    bus.subscribe(EventTypes.ERROR_DETECTED, on_error)
    bus.subscribe(EventTypes.TASK_COMPLETED, on_completed)

    # Publish events
    print("\nPublishing events...\n")

    bus.publish(
        EventTypes.TASK_STARTED,
        {"task_id": "S01", "description": "Build infrastructure"},
        source="dispatch",
    )

    bus.publish(
        EventTypes.TASK_COMPLETED,
        {"task_id": "S00", "duration": 12.5},
        source="dispatch",
    )

    bus.publish(
        EventTypes.ERROR_DETECTED,
        {"error": "Connection timeout", "source": "browser_agent"},
        source="browser_agent",
    )

    # Wait for async processing
    import time

    time.sleep(0.5)

    # Show stats
    print("\n" + "=" * 60)
    print("Event Bus Statistics:")
    print(json.dumps(bus.get_stats(), indent=2))

    print("\nEvent History:")
    for event in bus.get_history(limit=5):
        print(f"  {event['timestamp']}: {event['type']}")
