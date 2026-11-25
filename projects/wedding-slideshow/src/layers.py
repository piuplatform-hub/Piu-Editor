from math import ceil, floor

import cv2
import numpy as np

from media import HEIGHT, WIDTH


def premultiplied_layer(image):
    pixels = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGRA)
    alpha = pixels[:, :, 3:4].astype(np.uint16)
    colors = pixels[:, :, :3]
    colors[:] = (colors.astype(np.uint16) * alpha + 127) // 255
    return pixels


def paste_fractional(canvas, layer, x, y, opacity=1.):
    height, width = layer.shape[:2]
    left, top = max(0, floor(x)), max(0, floor(y))
    right, bottom = min(WIDTH, ceil(x + width)), min(HEIGHT, ceil(y + height))
    if left >= right or top >= bottom or opacity <= 0:
        return
    matrix = np.array(((1, 0, x - left), (0, 1, y - top)), dtype=np.float32)
    shifted = cv2.warpAffine(layer, matrix, (right - left, bottom - top), flags=cv2.INTER_LINEAR)
    if opacity < 1:
        shifted = cv2.convertScaleAbs(shifted, alpha=opacity)
    blue, green, red, alpha = cv2.split(shifted)
    background = canvas[top:bottom, left:right]
    inverse_alpha = cv2.cvtColor(cv2.bitwise_not(alpha), cv2.COLOR_GRAY2BGR)
    under = cv2.multiply(background, inverse_alpha, scale=1 / 255)
    cv2.add(cv2.merge((blue, green, red)), under, dst=background)
