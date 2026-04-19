from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None


def pil_to_cv_gray(image: Image.Image):
    if cv2 is None or np is None:
        return None

    rgb = image.convert("RGB")
    arr = np.array(rgb)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return gray


def cv_gray_to_pil(gray):
    if cv2 is None or np is None:
        return None
    return Image.fromarray(gray)


def prepare_base_image(file_path: str) -> Image.Image:
    image = Image.open(file_path)
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    return image


def crop_dark_borders_pil(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    bg = Image.new("L", gray.size, 255)
    diff = ImageChops.difference(gray, bg)
    bbox = diff.getbbox()

    if bbox:
        cropped = image.crop(bbox)
        if cropped.width > 100 and cropped.height > 100:
            return cropped

    return image


def crop_document_cv(image: Image.Image) -> Image.Image:
    if cv2 is None or np is None:
        return image

    gray = pil_to_cv_gray(image)
    if gray is None:
        return image

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    thresh_inv = 255 - thresh

    contours, _ = cv2.findContours(
        thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return image

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    if w < image.width * 0.5 or h < image.height * 0.5:
        return image

    return image.crop((x, y, x + w, y + h))


def deskew_image_cv(image: Image.Image) -> Image.Image:
    if cv2 is None or np is None:
        return image

    gray = pil_to_cv_gray(image)
    if gray is None:
        return image

    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 50:
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    if abs(angle) < 0.3:
        return image

    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(
        np.array(image),
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return Image.fromarray(rotated)


def build_opencv_variants(image: Image.Image) -> list[Image.Image]:
    if cv2 is None or np is None:
        return []

    gray = pil_to_cv_gray(image)
    if gray is None:
        return []

    variants = []

    variants.append(cv_gray_to_pil(gray))

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    variants.append(cv_gray_to_pil(clahe_img))

    adaptive1 = cv2.adaptiveThreshold(
        clahe_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    adaptive2 = cv2.adaptiveThreshold(
        clahe_img,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        31,
        9,
    )
    variants.append(cv_gray_to_pil(adaptive1))
    variants.append(cv_gray_to_pil(adaptive2))

    _, otsu = cv2.threshold(
        clahe_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    variants.append(cv_gray_to_pil(otsu))

    denoised = cv2.fastNlMeansDenoising(clahe_img, None, 20, 7, 21)
    variants.append(cv_gray_to_pil(denoised))

    inverted = 255 - clahe_img
    variants.append(cv_gray_to_pil(inverted))

    inv_adaptive = cv2.adaptiveThreshold(
        inverted,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    variants.append(cv_gray_to_pil(inv_adaptive))

    return [img for img in variants if img is not None]


def extract_dark_value_regions(image: Image.Image) -> list[Image.Image]:
    """
    Ищет тёмные прямоугольные области, где может быть светлый текст
    на тёмном фоне.
    """
    if cv2 is None or np is None:
        return []

    gray = pil_to_cv_gray(image)
    if gray is None:
        return []

    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, dark_mask = cv2.threshold(blur, 90, 255, cv2.THRESH_BINARY_INV)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []
    h_img, w_img = gray.shape[:2]

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h

        if area < 150:
            continue
        if w < 20 or h < 10:
            continue
        if w > w_img * 0.4:
            continue
        if h > h_img * 0.08:
            continue

        pad_x = max(3, int(w * 0.08))
        pad_y = max(2, int(h * 0.15))

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_img, x + w + pad_x)
        y2 = min(h_img, y + h + pad_y)

        crop = gray[y1:y2, x1:x2]

        crop_inv = 255 - crop
        crop_inv = cv2.resize(
            crop_inv, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC
        )
        crop_inv = cv2.GaussianBlur(crop_inv, (3, 3), 0)
        _, crop_bin = cv2.threshold(
            crop_inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        regions.append(Image.fromarray(crop_bin))

    return regions


def extract_colored_value_regions(image: Image.Image) -> list[Image.Image]:
    """
    Ищет цветные насыщенные прямоугольники, например красные плашки
    с белым текстом вроде 38* или 21*.
    """
    if cv2 is None or np is None:
        return []

    rgb = np.array(image.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(hsv, (0, 70, 40), (179, 255, 255))

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    h_img, w_img = mask.shape[:2]

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h

        if area < 120:
            continue
        if w < 20 or h < 10:
            continue
        if w > w_img * 0.45:
            continue
        if h > h_img * 0.08:
            continue

        pad_x = max(3, int(w * 0.08))
        pad_y = max(2, int(h * 0.15))

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_img, x + w + pad_x)
        y2 = min(h_img, y + h + pad_y)

        crop = rgb[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)

        inv = 255 - gray
        inv = cv2.resize(inv, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        regions.append(Image.fromarray(binary))

    return regions


def preprocess_image_variants_for_ocr(image: Image.Image) -> list[Image.Image]:
    variants = []

    image = crop_dark_borders_pil(image)
    image = crop_document_cv(image)
    image = deskew_image_cv(image)

    gray = image.convert("L")
    gray = ImageOps.autocontrast(gray)
    variants.append(gray)

    resized = gray.resize((gray.width * 2, gray.height * 2))
    resized = ImageOps.autocontrast(resized)
    variants.append(resized)

    sharp = resized.filter(ImageFilter.SHARPEN)
    variants.append(sharp)

    contrast = ImageEnhance.Contrast(sharp).enhance(2.0)
    variants.append(contrast)

    soft_binary = contrast.point(lambda x: 0 if x < 180 else 255, mode="1")
    hard_binary = contrast.point(lambda x: 0 if x < 150 else 255, mode="1")
    variants.append(soft_binary)
    variants.append(hard_binary)

    inverted = ImageOps.invert(contrast.convert("L"))
    variants.append(inverted)

    inverted_soft = inverted.point(lambda x: 0 if x < 180 else 255, mode="1")
    inverted_hard = inverted.point(lambda x: 0 if x < 150 else 255, mode="1")
    variants.append(inverted_soft)
    variants.append(inverted_hard)

    variants.extend(build_opencv_variants(image)[:2])

    # Отдельные вырезки для тёмных и цветных плашек
    variants.extend(extract_dark_value_regions(image))
    variants.extend(extract_colored_value_regions(image))

    unique = []
    seen = set()

    for img in variants:
        key = (img.size, img.mode, repr(img.getbands()))
        if key not in seen:
            seen.add(key)
            unique.append(img)

    return unique