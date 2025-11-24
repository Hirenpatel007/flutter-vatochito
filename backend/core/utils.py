from uuid import uuid4


def generate_upload_path(instance, filename: str) -> str:
    extension = filename.split(".")[-1]
    return f"uploads/{uuid4().hex}.{extension}"
