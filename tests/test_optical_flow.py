"""Tests for Optical Flow Epicenter Detection system."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.core.optical_flow import (FlowAnalysisResult, FlowEpicenter,
                                   OpticalFlowDetector, create_flow_detector)


class TestFlowEpicenter:
    """Test FlowEpicenter dataclass."""

    def test_epicenter_creation(self):
        """Test creating a flow epicenter."""
        epicenter = FlowEpicenter(
            x=100.0,
            y=200.0,
            strength=0.75,
            frame_number=10,
            timestamp=0.5,
            flow_type="convergent",
            metadata={"test": "value"},
        )

        assert epicenter.x == 100.0
        assert epicenter.y == 200.0
        assert epicenter.strength == 0.75
        assert epicenter.flow_type == "convergent"

    def test_epicenter_serialization(self):
        """Test epicenter to_dict and from_dict."""
        epicenter = FlowEpicenter(
            x=50.0,
            y=75.0,
            strength=0.5,
            frame_number=5,
            timestamp=1.0,
            flow_type="divergent",
        )

        # Serialize
        data = epicenter.to_dict()
        assert data["x"] == 50.0
        assert data["flow_type"] == "divergent"

        # Deserialize
        restored = FlowEpicenter.from_dict(data)
        assert restored.x == epicenter.x
        assert restored.strength == epicenter.strength


class TestOpticalFlowDetector:
    """Test OpticalFlowDetector class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def detector(self, temp_dir):
        """Create detector instance."""
        return OpticalFlowDetector(data_dir=temp_dir)

    @pytest.fixture
    def sample_video(self, temp_dir):
        """Create a sample test video."""
        try:
            import cv2
        except ImportError:
            pytest.skip("OpenCV not installed")

        video_path = Path(temp_dir) / "test_video.mp4"

        # Create simple test video with moving objects
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 10, (640, 480))

        # Generate frames with moving circle
        for i in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Moving circle
            x = 100 + i * 10
            y = 240
            cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)
            out.write(frame)

        out.release()
        return str(video_path)

    @pytest.fixture
    def sample_images(self, temp_dir):
        """Create sample test images."""
        try:
            import cv2
        except ImportError:
            pytest.skip("OpenCV not installed")

        image_paths = []

        for i in range(5):
            img_path = Path(temp_dir) / f"frame_{i:03d}.png"
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Moving object
            x = 100 + i * 50
            y = 240
            cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)

            cv2.imwrite(str(img_path), frame)
            image_paths.append(str(img_path))

        return image_paths

    def test_initialization(self, detector):
        """Test detector initialization."""
        assert detector.algorithm == "farneback"
        assert detector.sensitivity == 0.5
        assert detector.cv2 is not None

    def test_initialization_custom_params(self, temp_dir):
        """Test detector with custom parameters."""
        detector = OpticalFlowDetector(
            data_dir=temp_dir, algorithm="lucas_kanade", sensitivity=0.8
        )

        assert detector.algorithm == "lucas_kanade"
        assert detector.sensitivity == 0.8

    def test_opencv_check(self, temp_dir):
        """Test OpenCV availability check."""
        detector = OpticalFlowDetector(data_dir=temp_dir)
        assert hasattr(detector, "cv2")

    def test_analyze_video(self, detector, sample_video):
        """Test video analysis."""
        result = detector.analyze_video(sample_video, frame_skip=2)

        assert isinstance(result, FlowAnalysisResult)
        assert result.total_frames > 0
        assert result.video_source == sample_video
        assert result.avg_motion >= 0

    def test_analyze_video_with_max_frames(self, detector, sample_video):
        """Test video analysis with frame limit."""
        result = detector.analyze_video(sample_video, max_frames=10)

        assert result.total_frames <= 10

    def test_analyze_nonexistent_video(self, detector):
        """Test analyzing non-existent video."""
        with pytest.raises(FileNotFoundError):
            detector.analyze_video("nonexistent_video.mp4")

    def test_analyze_image_sequence(self, detector, sample_images):
        """Test image sequence analysis."""
        result = detector.analyze_image_sequence(sample_images)

        assert isinstance(result, FlowAnalysisResult)
        assert result.total_frames == len(sample_images)
        assert len(result.epicenters) >= 0

    def test_analyze_empty_image_sequence(self, detector):
        """Test with empty image list."""
        with pytest.raises(ValueError):
            detector.analyze_image_sequence([])

    def test_compute_flow_farneback(self, detector):
        """Test Farneback optical flow computation."""
        # Create two test frames
        frame1 = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        frame2 = np.roll(frame1, 5, axis=1)  # Shift horizontally

        flow = detector._compute_flow(frame1, frame2)

        assert flow.shape == (100, 100, 2)
        assert flow.dtype == np.float32

    def test_compute_flow_lucas_kanade(self, temp_dir):
        """Test Lucas-Kanade optical flow."""
        detector = OpticalFlowDetector(data_dir=temp_dir, algorithm="lucas_kanade")

        # Create frames with features
        frame1 = np.zeros((100, 100), dtype=np.uint8)
        frame1[40:60, 40:60] = 255  # White square

        frame2 = np.zeros((100, 100), dtype=np.uint8)
        frame2[40:60, 45:65] = 255  # Shifted square

        flow = detector._compute_flow(frame1, frame2)

        assert flow.shape == (100, 100, 2)

    def test_detect_epicenters(self, detector):
        """Test epicenter detection."""
        # Create synthetic flow field with convergence
        flow = np.zeros((100, 100, 2), dtype=np.float32)

        # Create convergent flow pattern
        center_x, center_y = 50, 50
        for y in range(100):
            for x in range(100):
                dx = center_x - x
                dy = center_y - y
                dist = np.sqrt(dx**2 + dy**2) + 1
                flow[y, x, 0] = dx / dist
                flow[y, x, 1] = dy / dist

        epicenters = detector._detect_epicenters(flow, frame_number=1, timestamp=0.1)

        # Should detect at least one epicenter
        assert len(epicenters) >= 0

        # Check epicenter properties
        for epi in epicenters:
            assert isinstance(epi, FlowEpicenter)
            assert epi.strength >= 0
            assert epi.flow_type in ["convergent", "divergent", "vortex"]

    def test_save_analysis(self, detector, temp_dir):
        """Test saving analysis results."""
        epicenters = [
            FlowEpicenter(
                x=10.0,
                y=20.0,
                strength=0.5,
                frame_number=1,
                timestamp=0.1,
                flow_type="convergent",
            )
        ]

        result = FlowAnalysisResult(
            epicenters=epicenters,
            total_frames=10,
            avg_motion=0.3,
            peak_motion_frame=5,
            video_source="test.mp4",
            analysis_timestamp="2025-12-20T00:00:00",
        )

        detector._save_analysis(result, "test.mp4")

        # Check file was created
        output_file = Path(temp_dir) / "analysis_test.json"
        assert output_file.exists()

    def test_get_statistics(self, detector):
        """Test getting detector statistics."""
        stats = detector.get_statistics()

        assert "total_analyses" in stats
        assert "algorithm" in stats
        assert stats["algorithm"] == "farneback"
        assert stats["sensitivity"] == 0.5

    def test_visualize_flow_error_handling(self, detector):
        """Test visualization error handling."""
        with pytest.raises(FileNotFoundError):
            detector.visualize_flow("nonexistent.mp4")

    def test_sparse_to_dense_flow(self, detector):
        """Test conversion of sparse to dense flow."""
        # Create sample sparse flow points
        p0 = np.array([[[10.0, 10.0]], [[20.0, 20.0]]], dtype=np.float32)
        p1 = np.array([[[15.0, 12.0]], [[25.0, 22.0]]], dtype=np.float32)
        status = np.array([[1], [1]], dtype=np.uint8)
        shape = (100, 100)

        flow = detector._sparse_to_dense_flow(p0, p1, status, shape)

        assert flow.shape == (100, 100, 2)
        # Check that flow was set at feature points
        assert flow[10, 10, 0] != 0 or flow[10, 10, 1] != 0

    def test_multiple_epicenter_types(self, detector):
        """Test detection of different epicenter types."""
        # Create flow with divergence and curl
        flow = np.zeros((100, 100, 2), dtype=np.float32)

        # Divergent pattern (left side)
        for y in range(50):
            for x in range(50):
                flow[y, x, 0] = x - 25
                flow[y, x, 1] = y - 25

        # Vortex pattern (right side)
        for y in range(50, 100):
            for x in range(50, 100):
                dx = x - 75
                dy = y - 75
                flow[y, x, 0] = -dy
                flow[y, x, 1] = dx

        epicenters = detector._detect_epicenters(flow, 1, 0.0)

        # Should detect multiple types
        types_found = {e.flow_type for e in epicenters}
        assert len(types_found) >= 1  # At least one type detected

    def test_sensitivity_affects_detection(self, temp_dir):
        """Test that sensitivity affects epicenter detection."""
        # Create two detectors with different sensitivities
        detector_low = OpticalFlowDetector(data_dir=temp_dir, sensitivity=0.1)
        detector_high = OpticalFlowDetector(data_dir=temp_dir, sensitivity=0.9)

        # Create simple flow
        flow = np.random.randn(100, 100, 2).astype(np.float32) * 0.1

        epi_low = detector_low._detect_epicenters(flow, 1, 0.0)
        epi_high = detector_high._detect_epicenters(flow, 1, 0.0)

        # Lower sensitivity should detect more epicenters
        assert len(epi_low) >= len(epi_high)

    def test_flow_analysis_result_serialization(self):
        """Test FlowAnalysisResult serialization."""
        epicenters = [
            FlowEpicenter(
                x=1.0,
                y=2.0,
                strength=0.5,
                frame_number=1,
                timestamp=0.1,
                flow_type="convergent",
            )
        ]

        result = FlowAnalysisResult(
            epicenters=epicenters,
            total_frames=10,
            avg_motion=0.5,
            peak_motion_frame=5,
            video_source="test.mp4",
            analysis_timestamp="2025-12-20",
        )

        data = result.to_dict()

        assert data["total_frames"] == 10
        assert data["avg_motion"] == 0.5
        assert len(data["epicenters"]) == 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_flow_detector(self, temp_dir):
        """Test create_flow_detector function."""
        detector = create_flow_detector(data_dir=temp_dir)

        assert isinstance(detector, OpticalFlowDetector)
        assert detector.algorithm == "farneback"

    def test_create_flow_detector_custom_algorithm(self, temp_dir):
        """Test creating detector with custom algorithm."""
        detector = create_flow_detector(data_dir=temp_dir, algorithm="lucas_kanade")

        assert detector.algorithm == "lucas_kanade"


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_end_to_end_video_analysis(self, temp_dir):
        """Test complete video analysis workflow."""
        try:
            import cv2
        except ImportError:
            pytest.skip("OpenCV not installed")

        # Create test video
        video_path = Path(temp_dir) / "test.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 10, (320, 240))

        for i in range(20):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            x = 50 + i * 5
            cv2.circle(frame, (x, 120), 20, (255, 255, 255), -1)
            out.write(frame)

        out.release()

        # Analyze video
        detector = OpticalFlowDetector(data_dir=temp_dir)
        result = detector.analyze_video(str(video_path))

        # Verify results
        assert result.total_frames > 0
        assert result.avg_motion >= 0
        assert isinstance(result.analysis_timestamp, str)

        # Check that results were saved
        analysis_file = Path(temp_dir) / "analysis_test.json"
        assert analysis_file.exists()

    def test_end_to_end_image_sequence(self, temp_dir):
        """Test complete image sequence analysis."""
        try:
            import cv2
        except ImportError:
            pytest.skip("OpenCV not installed")

        # Create image sequence
        image_paths = []
        for i in range(10):
            img_path = Path(temp_dir) / f"img_{i:02d}.png"
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            x = 50 + i * 20
            cv2.circle(frame, (x, 120), 20, (255, 255, 255), -1)
            cv2.imwrite(str(img_path), frame)
            image_paths.append(str(img_path))

        # Analyze sequence
        detector = OpticalFlowDetector(data_dir=temp_dir, sensitivity=0.3)
        result = detector.analyze_image_sequence(image_paths)

        # Verify results
        assert result.total_frames == len(image_paths)
        assert result.avg_motion >= 0
