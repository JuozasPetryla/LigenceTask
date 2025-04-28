import numpy as np
from PIL import Image
from io import BytesIO

def generate_shuffled_pixel_image(
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
    flat = arr.reshape(N, C)

    rng = np.random.default_rng(seed)
    k = int(rng.integers(min_pixels, N+1))

    perm = rng.permutation(N)
    pick = perm[:k]

    out_flat = flat.copy()
    out_flat[pick] = flat[pick][rng.permutation(k)]
    out_arr = out_flat.reshape(H, W, C)
    out_img = Image.fromarray(out_arr)
    with BytesIO() as out_buf:
        out_img.save(out_buf, format=Image.EXTENSION.get(img_extension))
        return out_buf.getvalue()