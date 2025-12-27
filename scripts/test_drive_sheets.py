"""Test Drive upload and Sheets logging"""
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from scripts.config import load_settings
from scripts.upload_drive import upload_to_drive
from scripts.update_sheet import append_row

load_dotenv()

JST = timezone(timedelta(hours=9))

def main():
    settings = load_settings()
    now = datetime.now(JST)

    print("=" * 60)
    print("Testing Drive and Sheets Integration")
    print("=" * 60)

    # Check configuration
    print("\n[Configuration Check]")
    print(f"Google Refresh Token: {'OK' if settings['google_refresh_token'] else 'NOT SET'}")
    print(f"Drive Folder ID: {settings['drive_folder_id'] or 'NOT SET'}")
    print(f"GCP Service Account: {'OK' if settings['gcp_service_account'] else 'NOT SET'}")
    print(f"Sheets ID: {settings['sheets_id'] or 'NOT SET'}")
    print(f"Sheets Range: {settings['sheets_range']}")

    # Test Drive upload
    print("\n[Drive Upload Test]")
    if settings["google_refresh_token"] and settings["drive_folder_id"]:
        # Create a test file
        test_file = "test_upload.txt"
        with open(test_file, "w") as f:
            f.write(f"Test upload at {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("This is a test file from SleepMusic pipeline.\n")

        try:
            print(f"Uploading test file to folder: {settings['drive_folder_id']}")
            drive_url = upload_to_drive(
                settings["youtube_client_id"],
                settings["youtube_client_secret"],
                settings["google_refresh_token"],
                test_file,
                f"TEST_SleepMusic_{now.strftime('%Y%m%d_%H%M%S')}.txt",
                settings["drive_folder_id"],
            )
            print(f"[SUCCESS] {drive_url}")
        except Exception as e:
            print(f"[FAILED] {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
    else:
        print("[SKIPPED] Configuration missing (GOOGLE_REFRESH_TOKEN or DRIVE_FOLDER_ID)")

    # Test Sheets logging
    print("\n[Sheets Logging Test]")
    if settings["gcp_service_account"] and settings["sheets_id"]:
        test_data = [
            now.strftime("%Y-%m-%d %H:%M:%S"),
            "12345678",  # Test seed
            "Test music prompt",
            "Test bg image prompt",
            "Test thumb prompt",
            "https://drive.google.com/test",
            "https://youtu.be/test",
            "test",
        ]

        try:
            print(f"Appending test row to Sheets: {settings['sheets_id']}")
            print(f"Range: {settings['sheets_range']}")
            append_row(
                settings["gcp_service_account"],
                settings["sheets_id"],
                settings["sheets_range"],
                test_data,
            )
            print("[SUCCESS] Row appended")
        except Exception as e:
            print(f"[FAILED] {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[SKIPPED] Configuration missing")

    print("\n" + "=" * 60)
    print("Test completed. Check Drive and Sheets manually.")
    print("=" * 60)


if __name__ == "__main__":
    main()
