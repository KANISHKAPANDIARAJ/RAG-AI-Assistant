def parse_detections(results) -> dict:
    detections = []

    for result in results:
        boxes = result.boxes
        names = result.names

        for box in boxes:
            cls_id = int(box.cls[0])
            label = names[cls_id]
            confidence = round(float(box.conf[0]), 2)
            bbox = box.xyxy[0].tolist()

            detections.append({
                "label": label,
                "confidence": confidence,
                "bbox": [round(x, 1) for x in bbox]
            })

    labels = list(set([d["label"] for d in detections]))

    return {
        "detections": detections,
        "labels": labels,
        "count": len(detections)
    }