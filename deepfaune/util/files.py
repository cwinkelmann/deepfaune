from pathlib import Path


def find_images(images_dir: Path):
    """
    Find all images in the test directory
    """
    assert images_dir.exists(), f"Directory {images_dir} does not exist"

    return sorted(
        [f for f in images_dir.rglob('*.[Jj][Pp][Gg]')] +
        [f for f in images_dir.rglob('*.[Jj][Pp][Ee][Gg]')] +
        [f for f in images_dir.rglob('*.[Bb][Mm][Pp]')] +
        [f for f in images_dir.rglob('*.[Tt][Ii][Ff]')] +
        [f for f in images_dir.rglob('*.[Gg][Ii][Ff]')] +
        [f for f in images_dir.rglob('*.[Pp][Nn][Gg]')]
    )