import cv2

def draw_boxes(image_path: str, detections: list, save_path: str) -> str:
    image = cv2.imread(image_path)

    for det in detections:
        bbox = det["bbox"]
        label = det["label"]
        conf = det["confidence"]

        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image,
            f"{label} {conf}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    cv2.imwrite(save_path, image)
    return save_path