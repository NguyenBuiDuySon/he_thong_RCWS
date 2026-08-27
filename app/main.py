import cv2

from app.capture.camera import Camera
from app.config import load_camera_config


def main() -> None:
    config = load_camera_config(
        "configs/default.yaml"
    )

    camera = Camera(config)

    print("Camera started")
    print("Press Q or ESC to exit")

    try:
        while True:
            packet = camera.read()

            if packet is None:
                print("Failed to read frame")
                break

            image = packet.image

            cv2.putText(
                image,
                f"FRAME: {packet.frame_id}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "Vision System - Camera Test",
                image,
            )

            key = cv2.waitKey(1) & 0xFF

            if key in (
                ord("q"),
                27,
            ):
                break

    finally:
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()