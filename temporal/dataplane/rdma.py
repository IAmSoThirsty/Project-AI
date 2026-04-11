"""
RDMA (Remote Direct Memory Access) Client

Provides ultra-low latency networking using RDMA over Converged Ethernet (RoCE).
This is an optional feature that requires RDMA-capable NICs.

Feature flagged via ENABLE_RDMA environment variable.
"""

import asyncio
import logging
import struct
from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RDMAFeature:
    """Feature flag for RDMA support."""

    @staticmethod
    def is_available() -> bool:
        """Check if RDMA hardware and drivers are available."""
        try:
            import pyverbs
            return True
        except ImportError:
            logger.warning("pyverbs not installed - RDMA support unavailable")
            return False

    @staticmethod
    def check_device(device_name: str) -> bool:
        """Check if specific RDMA device exists."""
        try:
            import pyverbs.device as d
            devices = d.get_device_list()
            return any(dev.name.decode() == device_name for dev in devices)
        except Exception as e:
            logger.error(f"Failed to check RDMA device: {e}")
            return False


class RDMAOpcode(Enum):
    """RDMA operation types."""
    SEND = 0
    RECV = 1
    WRITE = 2
    READ = 3


@dataclass
class RDMAMemoryRegion:
    """Registered memory region for RDMA operations."""
    addr: int
    length: int
    rkey: int  # Remote key for RDMA operations
    lkey: int  # Local key


@dataclass
class RDMATransferStats:
    """Statistics for RDMA transfers."""
    bytes_sent: int = 0
    bytes_received: int = 0
    send_ops: int = 0
    recv_ops: int = 0
    rdma_writes: int = 0
    rdma_reads: int = 0
    avg_latency_us: float = 0.0
    max_latency_us: float = 0.0


class RDMAClient:
    """RDMA client for high-performance data transfers."""

    def __init__(self, config):
        """Initialize RDMA client with configuration."""
        from .config import RDMAConfig
        self.config: RDMAConfig = config
        self.context = None
        self.pd = None  # Protection Domain
        self.cq = None  # Completion Queue
        self.qp = None  # Queue Pair
        self.mr = None  # Memory Region
        self._connected = False
        self.stats = RDMATransferStats()

        # Check if RDMA is enabled
        if not self.config.enabled:
            logger.info("RDMA is disabled via configuration")
            return

        # Check if RDMA hardware is available
        if not RDMAFeature.is_available():
            logger.warning("RDMA hardware/drivers not available - falling back to TCP")
            self.config.enabled = False
            return

        # Check if specified device exists
        if not RDMAFeature.check_device(self.config.device_name):
            logger.warning(f"RDMA device {self.config.device_name} not found - falling back to TCP")
            self.config.enabled = False
            return

    async def connect(self, remote_addr: Optional[str] = None) -> None:
        """Initialize RDMA resources and connect to remote peer."""
        if not self.config.enabled:
            logger.info("RDMA disabled - skipping connection")
            return

        try:
            from pyverbs.device import Context
            from pyverbs.pd import PD
            from pyverbs.cq import CQ
            from pyverbs.qp import QPInitAttr, QPAttr, QPCap, QP
            from pyverbs.enums import IBV_QPT_RC, IBV_ACCESS_LOCAL_WRITE, IBV_ACCESS_REMOTE_WRITE
            from pyverbs.mr import MR

            # Open device
            self.context = Context(name=self.config.device_name)
            logger.info(f"Opened RDMA device: {self.config.device_name}")

            # Allocate Protection Domain
            self.pd = PD(self.context)

            # Create Completion Queue
            self.cq = CQ(self.context, self.config.queue_depth * 2, None, None, 0)

            # Create Queue Pair
            qp_cap = QPCap(
                max_send_wr=self.config.queue_depth,
                max_recv_wr=self.config.queue_depth,
                max_send_sge=self.config.max_send_sge,
                max_recv_sge=self.config.max_recv_sge,
                max_inline_data=self.config.max_inline_data,
            )

            qp_init_attr = QPInitAttr(
                qp_type=IBV_QPT_RC,  # Reliable Connection
                scq=self.cq,
                rcq=self.cq,
                cap=qp_cap,
            )

            self.qp = QP(self.pd, qp_init_attr)

            # Register memory region (example: 1GB buffer)
            buffer_size = 1024 * 1024 * 1024  # 1GB
            access_flags = IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE
            self.mr = MR(self.pd, buffer_size, access_flags)

            logger.info(f"Registered memory region: {buffer_size} bytes")

            self._connected = True
            logger.info("RDMA resources initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RDMA: {e}")
            logger.info("Falling back to standard networking")
            self.config.enabled = False
            raise

    async def disconnect(self) -> None:
        """Clean up RDMA resources."""
        if not self.config.enabled:
            return

        try:
            if self.qp:
                self.qp.close()
            if self.mr:
                self.mr.close()
            if self.cq:
                self.cq.close()
            if self.pd:
                self.pd.close()
            if self.context:
                self.context.close()

            self._connected = False
            logger.info("RDMA resources cleaned up")

        except Exception as e:
            logger.error(f"Error during RDMA cleanup: {e}")

    async def send(self, data: bytes) -> None:
        """Send data using RDMA SEND operation."""
        if not self.config.enabled or not self._connected:
            raise RuntimeError("RDMA not available or not connected")

        try:
            from pyverbs.qp import SendWR, SGE
            import time

            start = time.perf_counter()

            # Create scatter-gather element
            sge = SGE(
                addr=self.mr.buf,
                length=len(data),
                lkey=self.mr.lkey,
            )

            # Copy data to registered memory
            self.mr.write(data, len(data))

            # Create send work request
            send_wr = SendWR(num_sge=1, sg=[sge])

            # Post send
            self.qp.post_send(send_wr)

            # Poll for completion
            # Note: In production, use async completion handlers
            while True:
                nc, wc = self.cq.poll(1)
                if nc > 0:
                    break
                await asyncio.sleep(0.0001)  # 100 microseconds

            end = time.perf_counter()
            latency_us = (end - start) * 1_000_000

            # Update statistics
            self.stats.bytes_sent += len(data)
            self.stats.send_ops += 1
            self.stats.avg_latency_us = (
                (self.stats.avg_latency_us * (self.stats.send_ops - 1) + latency_us) 
                / self.stats.send_ops
            )
            self.stats.max_latency_us = max(self.stats.max_latency_us, latency_us)

            logger.debug(f"RDMA SEND: {len(data)} bytes in {latency_us:.2f} μs")

        except Exception as e:
            logger.error(f"RDMA send failed: {e}")
            raise

    async def recv(self, max_size: int) -> bytes:
        """Receive data using RDMA RECV operation."""
        if not self.config.enabled or not self._connected:
            raise RuntimeError("RDMA not available or not connected")

        try:
            from pyverbs.qp import RecvWR, SGE
            import time

            start = time.perf_counter()

            # Create scatter-gather element
            sge = SGE(
                addr=self.mr.buf,
                length=max_size,
                lkey=self.mr.lkey,
            )

            # Create receive work request
            recv_wr = RecvWR(num_sge=1, sg=[sge])

            # Post receive
            self.qp.post_recv(recv_wr)

            # Poll for completion
            while True:
                nc, wc = self.cq.poll(1)
                if nc > 0:
                    # Read data from registered memory
                    data = self.mr.read(wc[0].byte_len, 0)
                    break
                await asyncio.sleep(0.0001)  # 100 microseconds

            end = time.perf_counter()
            latency_us = (end - start) * 1_000_000

            # Update statistics
            self.stats.bytes_received += len(data)
            self.stats.recv_ops += 1

            logger.debug(f"RDMA RECV: {len(data)} bytes in {latency_us:.2f} μs")
            return data

        except Exception as e:
            logger.error(f"RDMA recv failed: {e}")
            raise

    async def rdma_write(
        self,
        data: bytes,
        remote_addr: int,
        remote_rkey: int,
    ) -> None:
        """Perform RDMA WRITE to remote memory."""
        if not self.config.enabled or not self._connected:
            raise RuntimeError("RDMA not available or not connected")

        try:
            from pyverbs.qp import SendWR, SGE
            from pyverbs.enums import IBV_WR_RDMA_WRITE
            import time

            start = time.perf_counter()

            # Copy data to local buffer
            self.mr.write(data, len(data))

            # Create scatter-gather element
            sge = SGE(
                addr=self.mr.buf,
                length=len(data),
                lkey=self.mr.lkey,
            )

            # Create RDMA WRITE work request
            send_wr = SendWR(
                wr_id=0,
                num_sge=1,
                sg=[sge],
                opcode=IBV_WR_RDMA_WRITE,
            )
            send_wr.set_wr_rdma(raddr=remote_addr, rkey=remote_rkey)

            # Post send
            self.qp.post_send(send_wr)

            # Poll for completion
            while True:
                nc, wc = self.cq.poll(1)
                if nc > 0:
                    break
                await asyncio.sleep(0.0001)

            end = time.perf_counter()
            latency_us = (end - start) * 1_000_000

            # Update statistics
            self.stats.rdma_writes += 1

            logger.debug(f"RDMA WRITE: {len(data)} bytes in {latency_us:.2f} μs")

        except Exception as e:
            logger.error(f"RDMA write failed: {e}")
            raise

    async def rdma_read(
        self,
        length: int,
        remote_addr: int,
        remote_rkey: int,
    ) -> bytes:
        """Perform RDMA READ from remote memory."""
        if not self.config.enabled or not self._connected:
            raise RuntimeError("RDMA not available or not connected")

        try:
            from pyverbs.qp import SendWR, SGE
            from pyverbs.enums import IBV_WR_RDMA_READ
            import time

            start = time.perf_counter()

            # Create scatter-gather element
            sge = SGE(
                addr=self.mr.buf,
                length=length,
                lkey=self.mr.lkey,
            )

            # Create RDMA READ work request
            send_wr = SendWR(
                wr_id=0,
                num_sge=1,
                sg=[sge],
                opcode=IBV_WR_RDMA_READ,
            )
            send_wr.set_wr_rdma(raddr=remote_addr, rkey=remote_rkey)

            # Post send
            self.qp.post_send(send_wr)

            # Poll for completion
            while True:
                nc, wc = self.cq.poll(1)
                if nc > 0:
                    data = self.mr.read(length, 0)
                    break
                await asyncio.sleep(0.0001)

            end = time.perf_counter()
            latency_us = (end - start) * 1_000_000

            # Update statistics
            self.stats.rdma_reads += 1

            logger.debug(f"RDMA READ: {length} bytes in {latency_us:.2f} μs")
            return data

        except Exception as e:
            logger.error(f"RDMA read failed: {e}")
            raise

    def get_memory_region_info(self) -> Optional[RDMAMemoryRegion]:
        """Get registered memory region information for sharing with peers."""
        if not self.config.enabled or not self.mr:
            return None

        return RDMAMemoryRegion(
            addr=self.mr.buf,
            length=self.mr.length,
            rkey=self.mr.rkey,
            lkey=self.mr.lkey,
        )

    def get_stats(self) -> RDMATransferStats:
        """Get RDMA transfer statistics."""
        return self.stats

    def reset_stats(self) -> None:
        """Reset RDMA statistics."""
        self.stats = RDMATransferStats()
