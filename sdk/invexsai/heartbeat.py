import threading
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 60   # seconds
DEAD_THRESHOLD = 180      # 3 missed = dead


class HeartbeatManager:
    def __init__(self, client, agent_id: str):
        self.client = client
        self.agent_id = agent_id
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name=f"invexsai-heartbeat-{self.agent_id[:8]}",
        )
        self._thread.start()
        logger.debug(f"INVEXSAI: heartbeat started for {self.agent_id}")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        while not self._stop_event.wait(HEARTBEAT_INTERVAL):
            try:
                self._loop.run_until_complete(
                    self.client.send_heartbeat(self.agent_id, "healthy")
                )
            except Exception as e:
                logger.warning(f"INVEXSAI: heartbeat error: {e}")
        self._loop.close()
