import cv2
import numpy as np
import os

def create_grid(size, spacing, angle_deg, thickness=1):
    padding = int(size * 0.5)
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
    
    cv2.rectangle(crop, (0,0), (size-1, size-1), (0,0,0), 10)
    
    return crop

def main():
    output_dir = "pattern_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    size = 1000
    spacing = 20 
    
    layer_a = create_grid(size, spacing, 0)
    cv2.imwrite(os.path.join(output_dir, "layer_a.png"), layer_a)
    print(f"Generated {output_dir}/layer_a.png")
    
    layer_b = create_grid(size, spacing, 5)
    cv2.imwrite(os.path.join(output_dir, "layer_b.png"), layer_b)
    print(f"Generated {output_dir}/layer_b.png")

if __name__ == "__main__":
    main()
