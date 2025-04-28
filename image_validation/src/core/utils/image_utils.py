import numpy as np

from PIL import Image
from io import BytesIO

def compare_image_reversability_by_pixel(bytes1: bytes, bytes2: bytes) -> bool:
    img1 = Image.open(BytesIO(bytes1)); img1.load()
    img2 = Image.open(BytesIO(bytes2)); img2.load()
    
    if img1.size != img2.size or img1.mode != img2.mode:
        raise ValueError("Images differ in size or mode")
    
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())
    
    diff_count = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 != p2)

    return diff_count == 0

def generate_unshuffled_pixel_image(
    img_bytes: bytes,
    seed: int,
    img_extension: str,
    min_pixels: int = 100,
) -> bytes:
    with BytesIO(img_bytes) as buf:
        img = Image.open(buf)
        img.load()

    arr = np.array(img)
    H, W, C = arr.shape
    N = H * W
    flat_shuffled = arr.reshape(N, C)

    rng = np.random.default_rng(seed)
    k = int(rng.integers(min_pixels, N + 1))
    perm = rng.permutation(N)                  
    pick = perm[:k]
    perm_k = rng.permutation(k)

    inv_perm_k = np.empty_like(perm_k)
    inv_perm_k[perm_k] = np.arange(k)

    orig_flat = flat_shuffled.copy()
    orig_flat[pick] = flat_shuffled[pick][inv_perm_k]

    orig_arr = orig_flat.reshape(H, W, C)
    orig_img = Image.fromarray(orig_arr)
    with BytesIO() as out_buf:
        orig_img.save(out_buf, format=Image.EXTENSION.get(img_extension))
        return out_buf.getvalue()