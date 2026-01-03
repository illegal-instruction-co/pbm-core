import cv2
import numpy as np
import os
def create_grid(size, spacing, angle_deg, thickness=1, label=""):
    padding = int(size * 0.2)
    full_size = size + 2 * padding
    img = np.zeros((full_size, full_size), dtype=np.uint8)
    img.fill(255)
    for x in range(0, full_size, spacing):
        cv2.line(img, (x, 0), (x, full_size), (0, 0, 0), thickness)
    for y in range(0, full_size, spacing):
        cv2.line(img, (0, y), (full_size, y), (0, 0, 0), thickness)
    center = (full_size // 2, full_size // 2)
    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(img, M, (full_size, full_size), borderValue=255)
    start = padding
    end = start + size
    crop = rotated[start:end, start:end]
    cv2.rectangle(crop, (0,0), (size-1, size-1), (0,0,0), 6)
    if label:
        cv2.putText(crop, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    return crop
def main():
    canvas_w, canvas_h = 1240, 1754
    canvas = np.ones((canvas_h, canvas_w), dtype=np.uint8) * 255
    cv2.putText(canvas, "PBM HOME TEST KIT (A4/INKJET)", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 3)
    instructions = [
        "1. Print this image on A4 paper (Set Scale to 100%).",
        "2. Cut out Square A and Square B.",
        "3. Make Square B translucent: Apply a tiny drop of cooking oil to the back.",
        "4. Place a 5-10mm clear spacer (e.g. CD case) between them.",
        "5. Tape Square A to the back and Square B to the front.",
        "6. Run 'python pbm_mvp/enroll.py' and show this to the camera."
    ]
    for i, line in enumerate(instructions):
        cv2.putText(canvas, line, (100, 180 + i*40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50,50,50), 2)
    square_size = 400
    layer_a = create_grid(square_size, 16, 0, label="SQUARE A (BASE/FAR)")
    layer_b = create_grid(square_size, 8, 7, label="SQUARE B (TOP/NEAR)")
    canvas[500:500+square_size, 100:100+square_size] = layer_a
    canvas[500:500+square_size, 600:600+square_size] = layer_b
    output_path = "assets/test_kit_a4.png"
    cv2.imwrite(output_path, canvas)
    print(f"SUCCESS: Generated {output_path}")
if __name__ == "__main__":
    main()
