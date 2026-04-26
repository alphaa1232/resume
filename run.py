import requests
import time

RUNWAY_API_KEY = "key_6c8415b7a2ca90b0e4deed3c4ca34f03c01f78906bbff93a0bd06f5cde5ac0b6b38e84f266af3cfbcffadbXXXX81cd1517b344b1bafeeefdf55398f0f0d266c"

url = "https://api.dev.runwayml.com/v1/text_to_video"

headers = {
    "Authorization": f"Bearer {RUNWAY_API_KEY}",
    "Content-Type": "application/json",
    "X-Runway-Version": "2024-11-06"
}

data = {
    "model": "veo3.1_fast",  # change if needed
    "promptText": "A futuristic city with flying cars at sunset, cinematic lighting, camera slowly zooming in",
    "ratio": "1280:720"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code != 200:
    print("❌ Error:", response.text)
    exit()

result = response.json()
job_id = result.get("id")

print("⏳ Job started:", job_id)

# -----------------------------
# 2. Poll for Status
# -----------------------------
status_url = f"https://api.dev.runwayml.com/v1/tasks/{job_id}"

while True:
    status_response = requests.get(status_url, headers={
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": "2024-11-06"
    })

    if status_response.status_code != 200:
        print("❌ Status Error:", status_response.text)
        break

    status_data = status_response.json()
    status = status_data.get("status")

    print("Status:", status)

    if status == "SUCCEEDED":
        output = status_data.get("output")
        video_url = None

        # 🔥 HANDLE ALL POSSIBLE OUTPUT FORMATS

        # Case 1: output is string
        if isinstance(output, str):
            video_url = output

        # Case 2: output is list
        elif isinstance(output, list):
            if len(output) > 0:
                first = output[0]

                if isinstance(first, str):
                    video_url = first

                elif isinstance(first, dict):
                    video_url = first.get("video_url") or first.get("url")

        # Case 3: output is dict
        elif isinstance(output, dict):
            video_url = output.get("video_url") or output.get("url")

        # ✅ Final result
        if video_url:
            print("\n🎉 Video URL:", video_url)

            # OPTIONAL: Auto-download video
            try:
                video_data = requests.get(video_url).content
                with open("output.mp4", "wb") as f:
                    f.write(video_data)
                print("📥 Video saved as output.mp4")
            except Exception as e:
                print("⚠️ Could not download video:", e)

        else:
            print("\n⚠️ Unknown output format:", output)

        break

    elif status == "FAILED":
        print("❌ Generation failed")
        break

    time.sleep(5)