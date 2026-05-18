import io
import math
import random
import time
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    cv2 = None
    np = None

try:
    from rembg import remove as rembg_remove
except Exception:  # pragma: no cover - optional dependency
    rembg_remove = None

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None


STYLE_PRESETS = {
    "realistic": "photorealistic, cinematic lighting, natural skin texture",
    "anime": "anime masterpiece, clean linework, vivid cel shading",
    "cyberpunk": "neon cyberpunk city, holograms, reflective wet streets",
    "fantasy": "epic fantasy concept art, magical atmosphere, ornate details",
    "3d": "high-end 3D render, octane lighting, product-grade details",
    "pixar": "warm family animation style, expressive character, soft lighting",
    "oil": "oil painting, visible brushwork, museum quality composition",
    "sketch": "fine pencil sketch, cross hatching, monochrome paper texture",
}


def _safe_name(prefix, suffix=".png"):
    return f"{prefix}-{int(time.time())}-{uuid.uuid4().hex[:8]}{suffix}"


def _font(size):
    for candidate in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _ratio_to_size(ratio):
    return {
        "1:1": (1024, 1024),
        "16:9": (1344, 768),
        "9:16": (768, 1344),
        "4:3": (1152, 864),
        "3:4": (864, 1152),
    }.get(ratio, (1024, 1024))


def save_placeholder_generation(prompt, style, ratio, output_dir):
    width, height = _ratio_to_size(ratio)
    img = Image.new("RGB", (width, height), "#050714")
    draw = ImageDraw.Draw(img)
    palette = ["#00e5ff", "#8b5cf6", "#ff3ea5", "#38f8a8", "#ffffff"]

    for y in range(height):
        r = int(5 + 20 * y / height)
        g = int(7 + 15 * math.sin(y / 90))
        b = int(20 + 90 * y / height)
        draw.line([(0, y), (width, y)], fill=(r, max(0, g), min(255, b)))

    random.seed(prompt + style)
    for _ in range(34):
        x = random.randint(-80, width)
        y = random.randint(-80, height)
        radius = random.randint(35, 220)
        color = random.choice(palette)
        draw.ellipse((x, y, x + radius, y + radius), outline=color, width=2)

    for x in range(0, width, 64):
        draw.line([(x, 0), (x + height // 3, height)], fill=(20, 229, 255), width=1)
    for y in range(0, height, 64):
        draw.line([(0, y), (width, y + width // 5)], fill=(139, 92, 246), width=1)

    title_font = _font(max(34, width // 25))
    body_font = _font(max(18, width // 50))
    label = f"{style.title()} AI Concept"
    draw.rounded_rectangle((50, height - 220, width - 50, height - 55), radius=28, fill=(8, 12, 32), outline="#00e5ff", width=3)
    draw.text((80, height - 190), label, fill="#ffffff", font=title_font)
    prompt_short = (prompt[:105] + "...") if len(prompt) > 105 else prompt
    draw.text((82, height - 130), prompt_short, fill="#b9c7ff", font=body_font)
    draw.text((82, height - 88), "Preview fallback. Add HF token or local Diffusers model for real generation.", fill="#38f8a8", font=body_font)

    path = Path(output_dir) / _safe_name("generated")
    img.save(path, quality=95)
    return path


def generate_image(prompt, negative_prompt, style, ratio, output_dir, config):
    style_text = STYLE_PRESETS.get(style, STYLE_PRESETS["realistic"])
    full_prompt = f"{prompt}, {style_text}, ultra detailed, premium AI image"

    if config.HUGGINGFACE_API_TOKEN and requests:
        api_url = f"https://api-inference.huggingface.co/models/{config.HUGGINGFACE_IMAGE_MODEL}"
        try:
            response = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {config.HUGGINGFACE_API_TOKEN}"},
                json={"inputs": full_prompt, "parameters": {"negative_prompt": negative_prompt}},
                timeout=120,
            )
            if response.ok and response.headers.get("content-type", "").startswith("image"):
                path = Path(output_dir) / _safe_name("generated")
                Image.open(io.BytesIO(response.content)).save(path)
                return path, "HuggingFace Stable Diffusion"
        except Exception:
            pass

    return save_placeholder_generation(prompt, style, ratio, output_dir), "Pillow preview fallback"


def _opencv_enhance(image, upscale):
    if cv2 is None or np is None:
        return None
    arr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    denoised = cv2.fastNlMeansDenoisingColored(arr, None, 5, 5, 7, 21)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    merged = cv2.merge((clahe.apply(l), a, b))
    corrected = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    h, w = corrected.shape[:2]
    resized = cv2.resize(corrected, (w * upscale, h * upscale), interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(resized, (0, 0), 1.3)
    sharpened = cv2.addWeighted(resized, 1.35, blur, -0.35, 0)
    return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))


def enhance_image(input_path, target, options, output_dir):
    target_scale = {"2k": 2, "3k": 3, "4k": 4}.get(target.lower(), 2)
    image = Image.open(input_path).convert("RGB")
    enhanced = _opencv_enhance(image, target_scale)
    engine = "OpenCV AI sharpening pipeline"

    if enhanced is None:
        width, height = image.size
        enhanced = image.resize((width * target_scale, height * target_scale), Image.Resampling.LANCZOS)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.75)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.12)
        enhanced = ImageEnhance.Color(enhanced).enhance(1.08)
        engine = "Pillow super-resolution fallback"

    if options.get("restore"):
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.08)
    if options.get("denoise"):
        enhanced = enhanced.filter(ImageFilter.MedianFilter(size=3))
    if options.get("faces"):
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.2)

    path = Path(output_dir) / _safe_name(f"enhanced-{target.lower()}")
    enhanced.save(path, quality=96)
    return path, engine


def remove_background(input_path, output_dir):
    image = Image.open(input_path).convert("RGBA")
    if rembg_remove:
        result = rembg_remove(image)
        engine = "rembg U2-Net background remover"
    else:
        result = image
        datas = result.getdata()
        new_data = []
        for r, g, b, a in datas:
            if r > 235 and g > 235 and b > 235:
                new_data.append((r, g, b, 0))
            else:
                new_data.append((r, g, b, a))
        result.putdata(new_data)
        engine = "transparent white-background fallback"
    path = Path(output_dir) / _safe_name("background-removed")
    result.save(path)
    return path, engine
