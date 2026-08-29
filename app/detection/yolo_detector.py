from __future__ import annotations

from time import perf_counter_ns

import torch
from ultralytics import YOLO

from app.capture.camera import FramePacket
from app.config import DetectorConfig
from app.detection.base import Detector
from app.detection.types import Detection, DetectionBatch


class YoloDetector(Detector):
    def __init__(
        self,
        config: DetectorConfig,
    ) -> None:
        self._config = config

        self._device = self._resolve_device(
            config.device
        )

        self._precision = self._resolve_precision(
            config.precision
        )

        self._model = YOLO(
            config.model
        )

    @property
    def device(self) -> str:
        return self._device

    @property
    def precision(self) -> str:
        return self._precision
        

    def detect(
        self,
        packet: FramePacket,
    ) -> DetectionBatch:
        started_ns = perf_counter_ns()
        results = self._model.predict(
            source=packet.image,
            device=self._device,
            imgsz=self._config.imgsz,
            conf=self._config.confidence,
            max_det=self._config.max_det,
            quantize=self._precision,
            verbose=False,
        )

        finished_ns = perf_counter_ns()

        total_ms = (
            finished_ns - started_ns
        ) / 1_000_000

        if not results:
            return DetectionBatch(
                frame_id=packet.frame_id,
                preprocess_ms=0.0,
                inference_ms=0.0,
                postprocess_ms=0.0,
                total_ms=total_ms,
                detections=(),
            )

        result = results[0]

        preprocess_ms = float(
            result.speed.get(
                "preprocess",
                0.0,
            )
        )

        inference_ms = float(
            result.speed.get(
                "inference",
                0.0,
            )
        )

        postprocess_ms = float(
            result.speed.get(
                "postprocess",
                0.0,
            )
        )

        detections: list[Detection] = []

        boxes = result.boxes

        if boxes is not None:
            xyxy = (
                boxes.xyxy
                .detach()
                .cpu()
                .numpy()
            )

            confidences = (
                boxes.conf
                .detach()
                .cpu()
                .numpy()
            )

            class_ids = (
                boxes.cls
                .detach()
                .cpu()
                .numpy()
                .astype(int)
            )

            for (
                coords,
                confidence,
                class_id,
            ) in zip(
                xyxy,
                confidences,
                class_ids,
                strict=True,
            ):
                x1, y1, x2, y2 = coords

                detections.append(
                    Detection(
                        class_id=int(class_id),
                        class_name=str(
                            result.names[
                                class_id
                            ]
                        ),
                        confidence=float(
                            confidence
                        ),
                        x1=float(x1),
                        y1=float(y1),
                        x2=float(x2),
                        y2=float(y2),
                    )
                )

        return DetectionBatch(
            frame_id=packet.frame_id,
            preprocess_ms=preprocess_ms,
            inference_ms=inference_ms,
            postprocess_ms=postprocess_ms,
            total_ms=total_ms,
            detections=tuple(
                detections
            ),
        )

    @staticmethod
    def _resolve_device(
        requested: str,
    ) -> str:
        if requested == "auto":
            return (
                "0"
                if torch.cuda.is_available()
                else "cpu"
            )

        if requested == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA requested but "
                    "torch.cuda.is_available() "
                    "is False."
                )

            return "0"

        if requested == "cpu":
            return "cpu"

        return requested

    def _resolve_precision(
        self,
        requested: str,
    ) -> str:
        if requested == "auto":
            return (
                "fp16"
                if self._device != "cpu"
                else "fp32"
            )

        if requested == "fp16":
            if self._device == "cpu":
                raise ValueError(
                    "FP16 was requested, "
                    "but the current device is CPU."
                )

            return "fp16"

        if requested == "fp32":
            return "fp32"

        raise ValueError(
            "precision must be one of: "
            "auto, fp16, fp32"
        )