import time
from urllib.parse import urljoin

import requests

from scripts.utils import request_with_retry


class KieAIClient:
    def __init__(self, api_key, api_base, suno_endpoint, nanobanana_endpoint):
        self.api_key = api_key
        self.api_base = api_base
        self.suno_endpoint = suno_endpoint
        self.nanobanana_endpoint = nanobanana_endpoint

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def _extract_url(self, payload):
        if not isinstance(payload, dict):
            return None
        for key in ("audio_url", "audioUrl", "image_url", "imageUrl", "url", "file_url", "result_url"):
            if key in payload:
                return payload[key]
        return None

    def generate_suno(self, prompt, seed, model="V4", custom_mode=False, instrumental=False):
        """Generate music using Suno API (async)"""
        url = urljoin(self.api_base, self.suno_endpoint)

        payload = {
            "prompt": prompt,
            "customMode": custom_mode,
            "instrumental": instrumental,
            "model": model,
            "callBackUrl": "http://localhost:8000/callback",  # Required but not used for polling
        }

        # Submit generation task
        response = request_with_retry(
            "POST",
            url,
            headers=self._headers(),
            json_payload=payload,
        )
        data = response.json()

        if data.get("code") != 200:
            raise RuntimeError(f"Suno API error: {data}")

        task_id = data.get("data", {}).get("taskId")
        if not task_id:
            raise RuntimeError(f"No taskId in response: {data}")

        # Poll for completion
        return self._poll_suno_task(task_id)

    def _poll_suno_task(self, task_id, max_wait=600, poll_interval=10):
        """Poll Suno task until completion"""
        query_url = urljoin(self.api_base, "/api/v1/generate/record-info")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = requests.get(
                query_url,
                headers=self._headers(),
                params={"taskId": task_id},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise RuntimeError(f"Query error: {data}")

            status = data.get("data", {}).get("status")
            print(f"Task {task_id} status: {status}")

            if status == "SUCCESS":
                response_data = data.get("data", {}).get("response", {})
                suno_data = response_data.get("sunoData", [])
                if suno_data and len(suno_data) > 0:
                    audio_url = suno_data[0].get("audioUrl")
                    if audio_url:
                        return audio_url
                raise RuntimeError(f"No audio URL in completed task: {data}")

            if status in ("FAILED", "ERROR"):
                raise RuntimeError(f"Task failed: {data}")

            time.sleep(poll_interval)

        raise RuntimeError(f"Task {task_id} timed out after {max_wait}s")

    def generate_nanobanana(self, prompt, seed=None, with_text=False, model="google/nano-banana"):
        """Generate image using Nano Banana API (async)"""
        url = urljoin(self.api_base, self.nanobanana_endpoint)

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "output_format": "png",
                "image_size": "16:9",
            },
        }

        # Submit generation task
        response = request_with_retry(
            "POST",
            url,
            headers=self._headers(),
            json_payload=payload,
        )
        data = response.json()

        if data.get("code") != 200:
            raise RuntimeError(f"Nano Banana API error: {data}")

        task_id = data.get("data", {}).get("taskId")
        if not task_id:
            raise RuntimeError(f"No taskId in response: {data}")

        # Poll for completion
        return self._poll_nanobanana_task(task_id)

    def _poll_nanobanana_task(self, task_id, max_wait=600, poll_interval=10):
        """Poll Nano Banana task until completion"""
        query_url = urljoin(self.api_base, "/api/v1/jobs/recordInfo")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = requests.get(
                query_url,
                headers=self._headers(),
                params={"taskId": task_id},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise RuntimeError(f"Query error: {data}")

            # Debug: print full response on first iteration
            if time.time() - start_time < poll_interval + 5:
                print(f"[DEBUG] Nano Banana full response: {data}")

            # Nano Banana uses 'state' not 'status'
            status = data.get("data", {}).get("state")
            print(f"Task {task_id} status: {status}")

            if status == "success":  # Nano Banana uses lowercase
                # Parse resultJson field
                import json as json_lib
                result_json_str = data.get("data", {}).get("resultJson", "{}")
                try:
                    result_json = json_lib.loads(result_json_str)
                    result_urls = result_json.get("resultUrls", [])
                    if result_urls and len(result_urls) > 0:
                        return result_urls[0]
                except (json_lib.JSONDecodeError, KeyError):
                    pass
                raise RuntimeError(f"No image URL in completed task: {data}")

            if status in ("FAILED", "ERROR"):
                raise RuntimeError(f"Task failed: {data}")

            time.sleep(poll_interval)

        raise RuntimeError(f"Task {task_id} timed out after {max_wait}s")
