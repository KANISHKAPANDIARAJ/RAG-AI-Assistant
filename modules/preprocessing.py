import cv2
import numpy as np
import os

def load_image(path: str) -> np.ndarray:
    image = cv2.imread(path)
    return image

def resize_image(image: np.ndarray, width: int = 1600) -> np.ndarray:
    h, w = image.shape[:2]
    if w <= width:
        return image
    ratio = width / w
    new_h = int(h * ratio)
    return cv2.resize(image, (width, new_h), interpolation=cv2.INTER_CUBIC)

def to_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image: str) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image, h=3)

def sharpen(image: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

def preprocess(image_path: str, save_dir: str = "uploads") -> str:
    image = load_image(image_path)
    image = resize_image(image)
    image = to_grayscale(image)
    image = remove_noise(image)
    image = sharpen(image)

    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    save_path = os.path.join(save_dir, f"{name}_processed.jpg")

    cv2.imwrite(save_path, image)
    return save_path