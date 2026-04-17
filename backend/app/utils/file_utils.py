import csv
import io


def decode_bytes_safely(data: bytes) -> str:
    """
    Пробуем несколько популярных кодировок.
    Это полезно для txt/csv файлов.
    """
    encodings_to_try = ["utf-8", "utf-8-sig", "cp1251", "latin-1"]

    for enc in encodings_to_try:
        try:
            return data.decode(enc)
        except Exception:
            continue

    return data.decode("utf-8", errors="ignore")


def csv_text_from_bytes(data: bytes) -> str:
    """
    Превращает CSV байты в обычный текст,
    чтобы потом отправить в AI.
    """
    decoded_text = decode_bytes_safely(data)
    csv_reader = csv.reader(io.StringIO(decoded_text))

    rows = []
    for row in csv_reader:
        cleaned = [str(cell).strip() for cell in row if str(cell).strip()]
        if cleaned:
            rows.append(" | ".join(cleaned))

    return "\n".join(rows).strip()