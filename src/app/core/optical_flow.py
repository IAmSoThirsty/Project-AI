"""
Optical Flow Epicenter Detection System for Project-AI.

This module implements optical flow analysis to detect motion epicenters in video
sequences. It can be used for:
- Motion pattern analysis
- Crowd flow detection
- Activity hotspot identification
- Anomaly detection in video streams
- Security and surveillance applications

The system uses OpenCV's optical flow algorithms (Farneback, Lucas-Kanade) to
compute motion vectors and identifies epicenters where motion converges or
originates.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FlowEpicenter:
    """Represents a detected motion epicenter."""

    x: float
    y: float
    strength: float
    frame_number: int
    timestamp: float
    flow_type: str  # 'convergent', 'divergent', or 'vortex'
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "strength": self.strength,
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "flow_type": self.flow_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FlowEpicenter":
        """Create from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            strength=data["strength"],
            frame_number=data["frame_number"],
            timestamp=data["timestamp"],
            flow_type=data["flow_type"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class FlowAnalysisResult:
    """Results from optical flow analysis."""

    epicenters: list[FlowEpicenter]
    total_frames: int
    avg_motion: float
    peak_motion_frame: int
    video_source: str
    analysis_timestamp: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "epicenters": [e.to_dict() for e in self.epicenters],
            "total_frames": self.total_frames,
            "avg_motion": self.avg_motion,
            "peak_motion_frame": self.peak_motion_frame,
            "video_source": self.video_source,
            "analysis_timestamp": self.analysis_timestamp,
        }


class OpticalFlowDetector:
    """
    Optical flow epicenter detection system.

    Uses OpenCV's optical flow algorithms to analyze video frames and detect
    motion epicenters - points where motion converges, diverges, or rotates.
    """

    def __init__(
        self,
        data_dir: str = "data/optical_flow",
        algorithm: str = "farneback",
        sensitivity: float = 0.5,
    ):
        """
        Initialize optical flow detector.

        Args:
            data_dir: Directory for storing analysis results
            algorithm: Optical flow algorithm ('farneback' or 'lucas_kanade')
            sensitivity: Detection sensitivity (0.0-1.0)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.algorithm = algorithm
        self.sensitivity = sensitivity

        self._check_opencv()

    def _check_opencv(self):
        """Check if OpenCV is available."""
        try:
            import cv2

            self.cv2 = cv2
            logger.info(f"OpenCV version: {cv2.__version__}")
        except ImportError as e:
            logger.error(
                "OpenCV not installed. Install with: pip install opencv-python"
            )
            raise ImportError("opencv-python required for optical flow") from e

    def analyze_video(
        self,
        video_path: str,
        frame_skip: int = 1,
        max_frames: int = None,
    ) -> FlowAnalysisResult:
        """
        Analyze video to detect motion epicenters.

        Args:
            video_path: Path to video file
            frame_skip: Process every Nth frame (1 = all frames)
            max_frames: Maximum frames to process (None = all)

        Returns:
            FlowAnalysisResult with detected epicenters
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info(f"Analyzing video: {video_path}")

        cap = self.cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        epicenters = []
        frame_count = 0
        processed_frames = 0
        motion_magnitudes = []

        ret, prev_frame = cap.read()
        if not ret:
            raise ValueError("Cannot read first frame")

        prev_gray = self.cv2.cvtColor(prev_frame, self.cv2.COLOR_BGR2GRAY)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Skip frames if needed
            if frame_count % frame_skip != 0:
                continue

            # Check max frames limit
            if max_frames and processed_frames >= max_frames:
                break

            # Convert to grayscale
            gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)

            # Compute optical flow
            flow = self._compute_flow(prev_gray, gray)

            # Analyze flow for epicenters
            frame_epicenters = self._detect_epicenters(
                flow, frame_count, cap.get(self.cv2.CAP_PROP_POS_MSEC) / 1000.0
            )
            epicenters.extend(frame_epicenters)

            # Calculate motion magnitude
            magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
            motion_magnitudes.append(np.mean(magnitude))

            prev_gray = gray
            processed_frames += 1

        cap.release()

        # Find peak motion frame
        peak_frame = int(np.argmax(motion_magnitudes)) if motion_magnitudes else 0

        result = FlowAnalysisResult(
            epicenters=epicenters,
            total_frames=processed_frames,
            avg_motion=float(np.mean(motion_magnitudes)) if motion_magnitudes else 0.0,
            peak_motion_frame=peak_frame,
            video_source=video_path,
            analysis_timestamp=datetime.now().isoformat(),
        )

        # Save results
        self._save_analysis(result, video_path)

        logger.info(
            f"Analysis complete: {len(epicenters)} epicenters detected "
            f"in {processed_frames} frames"
        )

        return result

    def _compute_flow(self, prev_gray: np.ndarray, gray: np.ndarray) -> np.ndarray:
        """
        Compute optical flow between two frames.

        Args:
            prev_gray: Previous frame (grayscale)
            gray: Current frame (grayscale)

        Returns:
            Flow field as numpy array
        """
        if self.algorithm == "farneback":
            flow = self.cv2.calcOpticalFlowFarneback(
                prev_gray,
                gray,
                None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0,
            )
        elif self.algorithm == "lucas_kanade":
            # For Lucas-Kanade, we need feature points
            # Use Shi-Tomasi corner detection
            feature_params = {
                "maxCorners": 100,
                "qualityLevel": 0.3,
                "minDistance": 7,
                "blockSize": 7,
            }
            p0 = self.cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)

            if p0 is not None:
                lk_params = {
                    "winSize": (15, 15),
                    "maxLevel": 2,
                    "criteria": (
                        self.cv2.TERM_CRITERIA_EPS | self.cv2.TERM_CRITERIA_COUNT,
                        10,
                        0.03,
                    ),
                }

                p1, st, err = self.cv2.calcOpticalFlowPyrLK(
                    prev_gray, gray, p0, None, **lk_params
                )

                # Create dense flow field from sparse points
                flow = self._sparse_to_dense_flow(p0, p1, st, prev_gray.shape)
            else:
                # No features found, return zero flow
                flow = np.zeros((prev_gray.shape[0], prev_gray.shape[1], 2))
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

        return flow

    def _sparse_to_dense_flow(
        self, p0: np.ndarray, p1: np.ndarray, status: np.ndarray, shape: tuple
    ) -> np.ndarray:
        """Convert sparse optical flow to dense flow field."""
        flow = np.zeros((shape[0], shape[1], 2), dtype=np.float32)

        # Use valid points only
        good_old = p0[status == 1]
        good_new = p1[status == 1]

        # Compute flow vectors
        for old, new in zip(good_old, good_new, strict=False):
            x, y = old.ravel()
            flow[int(y), int(x)] = new.ravel() - old.ravel()

        return flow

    def _detect_epicenters(
        self, flow: np.ndarray, frame_number: int, timestamp: float
    ) -> list[FlowEpicenter]:
        """
        Detect epicenters in optical flow field.

        Args:
            flow: Optical flow field
            frame_number: Current frame number
            timestamp: Video timestamp in seconds

        Returns:
            List of detected epicenters
        """
        epicenters = []

        # Calculate flow properties
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        angle = np.arctan2(flow[..., 1], flow[..., 0])

        # Compute divergence (convergence/divergence points)
        dx = np.gradient(flow[..., 0], axis=1)
        dy = np.gradient(flow[..., 1], axis=0)
        divergence = dx + dy

        # Compute curl (vorticity/rotation points)
        curl = np.gradient(flow[..., 1], axis=1) - np.gradient(flow[..., 0], axis=0)

        # Find local extrema in divergence (convergent/divergent epicenters)
        threshold = self.sensitivity * np.std(divergence)

        # Apply spatial filtering to reduce number of candidates
        # Use non-maximum suppression approach with larger neighborhoods
        kernel_size = 15

        # Helper function to find local maxima with spatial suppression
        def find_local_maxima(field, is_minimum=False):
            """Find local maxima/minima in field with spatial suppression."""
            candidates = []
            abs_field = np.abs(field)

            # Find pixels above threshold
            mask = field < -threshold if is_minimum else field > threshold

            y_coords, x_coords = np.where(mask)

            # Sort by strength
            strengths = abs_field[y_coords, x_coords]
            sorted_indices = np.argsort(strengths)[::-1]

            # Apply non-maximum suppression
            for idx in sorted_indices:
                y, x = y_coords[idx], x_coords[idx]

                # Check if this location is too close to existing candidates
                is_too_close = False
                for cy, cx in candidates:
                    if abs(y - cy) < kernel_size and abs(x - cx) < kernel_size:
                        is_too_close = True
                        break

                if not is_too_close:
                    candidates.append((y, x))

                # Limit candidates
                if len(candidates) >= 10:
                    break

            return candidates

        # Convergent points (negative divergence) with spatial filtering
        convergent_candidates = find_local_maxima(divergence, is_minimum=True)
        for y, x in convergent_candidates:
            strength = abs(float(divergence[y, x]))
            epicenters.append(
                FlowEpicenter(
                    x=float(x),
                    y=float(y),
                    strength=strength,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    flow_type="convergent",
                    metadata={
                        "magnitude": float(magnitude[y, x]),
                        "angle": float(angle[y, x]),
                    },
                )
            )

        # Divergent points (positive divergence) with spatial filtering
        divergent_candidates = find_local_maxima(divergence, is_minimum=False)
        for y, x in divergent_candidates:
            strength = float(divergence[y, x])
            epicenters.append(
                FlowEpicenter(
                    x=float(x),
                    y=float(y),
                    strength=strength,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    flow_type="divergent",
                    metadata={
                        "magnitude": float(magnitude[y, x]),
                        "angle": float(angle[y, x]),
                    },
                )
            )

        # Vortex points (high curl) with spatial filtering
        curl_threshold = self.sensitivity * np.std(curl)

        # Find vortex candidates
        vortex_candidates = []
        abs_curl = np.abs(curl)
        mask = abs_curl > curl_threshold
        y_coords, x_coords = np.where(mask)

        if len(y_coords) > 0:
            strengths = abs_curl[y_coords, x_coords]
            sorted_indices = np.argsort(strengths)[::-1]

            for idx in sorted_indices:
                y, x = y_coords[idx], x_coords[idx]

                # Check spatial suppression
                is_too_close = False
                for cy, cx in vortex_candidates:
                    if abs(y - cy) < kernel_size and abs(x - cx) < kernel_size:
                        is_too_close = True
                        break

                if not is_too_close:
                    vortex_candidates.append((y, x))

                if len(vortex_candidates) >= 10:
                    break

        for y, x in vortex_candidates:
            strength = abs(float(curl[y, x]))
            epicenters.append(
                FlowEpicenter(
                    x=float(x),
                    y=float(y),
                    strength=strength,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    flow_type="vortex",
                    metadata={
                        "magnitude": float(magnitude[y, x]),
                        "angle": float(angle[y, x]),
                        "curl": float(curl[y, x]),
                    },
                )
            )

        # Final limit to top epicenters by strength (should already be limited)
        if len(epicenters) > 30:
            epicenters.sort(key=lambda e: e.strength, reverse=True)
            epicenters = epicenters[:30]

        return epicenters

    def analyze_image_sequence(self, image_paths: list[str]) -> FlowAnalysisResult:
        """
        Analyze sequence of images for optical flow.

        Args:
            image_paths: List of image file paths in order

        Returns:
            FlowAnalysisResult with detected epicenters
        """
        if not image_paths:
            raise ValueError("No images provided")

        logger.info(f"Analyzing {len(image_paths)} images")

        epicenters = []
        motion_magnitudes = []

        prev_img = self.cv2.imread(image_paths[0])
        if prev_img is None:
            raise ValueError(f"Cannot read image: {image_paths[0]}")

        prev_gray = self.cv2.cvtColor(prev_img, self.cv2.COLOR_BGR2GRAY)

        for i, img_path in enumerate(image_paths[1:], start=1):
            img = self.cv2.imread(img_path)
            if img is None:
                logger.warning(f"Cannot read image: {img_path}, skipping")
                continue

            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

            # Compute optical flow
            flow = self._compute_flow(prev_gray, gray)

            # Detect epicenters
            frame_epicenters = self._detect_epicenters(flow, i, float(i))
            epicenters.extend(frame_epicenters)

            # Calculate motion
            magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
            motion_magnitudes.append(np.mean(magnitude))

            prev_gray = gray

        peak_frame = int(np.argmax(motion_magnitudes)) if motion_magnitudes else 0

        result = FlowAnalysisResult(
            epicenters=epicenters,
            total_frames=len(image_paths),
            avg_motion=float(np.mean(motion_magnitudes)) if motion_magnitudes else 0.0,
            peak_motion_frame=peak_frame,
            video_source=f"image_sequence_{len(image_paths)}_frames",
            analysis_timestamp=datetime.now().isoformat(),
        )

        logger.info(f"Analysis complete: {len(epicenters)} epicenters detected")

        return result

    def _save_analysis(self, result: FlowAnalysisResult, video_path: str):
        """Save analysis results to disk."""
        output_file = self.data_dir / f"analysis_{Path(video_path).stem}.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def visualize_flow(
        self, video_path: str, output_path: str = None, show_epicenters: bool = True
    ):
        """
        Create visualization of optical flow with epicenters.

        Args:
            video_path: Input video path
            output_path: Output video path (None = display with cv2.imshow)
            show_epicenters: Whether to mark epicenters
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = self.cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        # Get video properties
        fps = int(cap.get(self.cv2.CAP_PROP_FPS))
        width = int(cap.get(self.cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(self.cv2.CAP_PROP_FRAME_HEIGHT))

        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = self.cv2.VideoWriter_fourcc(*"mp4v")
            writer = self.cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        ret, prev_frame = cap.read()
        if not ret:
            raise ValueError("Cannot read first frame")

        prev_gray = self.cv2.cvtColor(prev_frame, self.cv2.COLOR_BGR2GRAY)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)

            # Compute flow
            flow = self._compute_flow(prev_gray, gray)

            # Detect epicenters
            if show_epicenters:
                epicenters = self._detect_epicenters(flow, frame_count, 0.0)

                # Draw epicenters
                for epi in epicenters:
                    color = (
                        (0, 255, 0)
                        if epi.flow_type == "convergent"
                        else (
                            (0, 0, 255)
                            if epi.flow_type == "divergent"
                            else (255, 0, 255)
                        )
                    )
                    self.cv2.circle(frame, (int(epi.x), int(epi.y)), 5, color, -1)
                    self.cv2.putText(
                        frame,
                        epi.flow_type[0].upper(),
                        (int(epi.x) + 10, int(epi.y)),
                        self.cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                    )

            # Draw flow field
            step = 16
            for y in range(0, gray.shape[0], step):
                for x in range(0, gray.shape[1], step):
                    fx, fy = flow[y, x]
                    magnitude = np.sqrt(fx**2 + fy**2)
                    if magnitude > 0.5:  # Only draw significant motion
                        self.cv2.arrowedLine(
                            frame,
                            (x, y),
                            (int(x + fx * 3), int(y + fy * 3)),
                            (0, 255, 255),
                            1,
                            tipLength=0.3,
                        )

            if writer:
                writer.write(frame)
            else:
                # Display mode when no output path provided
                self.cv2.imshow("Optical Flow Visualization", frame)
                # Wait 1ms and check if user pressed 'q' to quit
                if self.cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            prev_gray = gray

        cap.release()
        if writer:
            writer.release()
            logger.info(f"Visualization saved to: {output_path}")
        else:
            self.cv2.destroyAllWindows()
            logger.info("Visualization display closed")

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about stored analyses."""
        analysis_files = list(self.data_dir.glob("analysis_*.json"))

        return {
            "total_analyses": len(analysis_files),
            "data_directory": str(self.data_dir),
            "algorithm": self.algorithm,
            "sensitivity": self.sensitivity,
        }


# Convenience functions


def analyze_video(
    video_path: str,
    algorithm: str = "farneback",
    sensitivity: float = 0.5,
) -> FlowAnalysisResult:
    """
    Quick helper to analyze a video file.

    Args:
        video_path: Path to video file
        algorithm: 'farneback' or 'lucas_kanade'
        sensitivity: Detection sensitivity (0.0-1.0)

    Returns:
        FlowAnalysisResult
    """
    detector = OpticalFlowDetector(algorithm=algorithm, sensitivity=sensitivity)
    return detector.analyze_video(video_path)


def create_flow_detector(
    data_dir: str = "data/optical_flow",
    algorithm: str = "farneback",
) -> OpticalFlowDetector:
    """Create optical flow detector with default settings."""
    return OpticalFlowDetector(data_dir=data_dir, algorithm=algorithm)
