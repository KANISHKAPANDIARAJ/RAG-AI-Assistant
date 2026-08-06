def parse_ocr_result(raw_result: list) -> dict:
    lines = []
    full_text = []

    for detection in raw_result:
        bbox = detection[0]
        text = detection[1]
        confidence = round(float(detection[2]), 2)

        # convert bbox numpy values to plain python ints
        bbox_clean = [[int(point[0]), int(point[1])] for point in bbox]

        lines.append({
            "text": text,
            "confidence": confidence,
            "bbox": bbox_clean
        })
        full_text.append(text)

    return {
        "lines": lines,
        "full_text": "\n".join(full_text)
    }