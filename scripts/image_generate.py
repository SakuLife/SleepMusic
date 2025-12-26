import requests

from scripts.kieai_client import KieAIClient


def download_image(url, output_path):
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def generate_images(
    client: KieAIClient,
    bg_prompt,
    thumb_prompt,
    seed,
    bg_path,
    thumb_path,
):
    bg_url = client.generate_nanobanana(bg_prompt, seed=seed, with_text=False)
    download_image(bg_url, bg_path)

    thumb_url = client.generate_nanobanana(thumb_prompt, seed=seed, with_text=True)
    download_image(thumb_url, thumb_path)

    return bg_path, thumb_path
