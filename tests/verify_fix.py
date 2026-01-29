import os
import traceback
from PIL import Image
from win10toast import ToastNotifier


def verify_ico_toast():
    icon_png = "icon.png"
    icon_ico = "icon.ico"

    # Ensure starting clean or using existing if present
    if os.path.exists(icon_png) and not os.path.exists(icon_ico):
        print("Creating ICO for test...")
        try:
            img = Image.open(icon_png)
            img.save(icon_ico, format="ICO")
        except Exception as e:
            print(f"Failed to create ICO: {e}")
            return

    if not os.path.exists(icon_ico):
        print("icon.ico not found, cannot test.")
        return

    toaster = ToastNotifier()
    print(f"Testing toast with: {os.path.abspath(icon_ico)}")
    try:
        toaster.show_toast(
            "Verification Test",
            "This toast uses the .ico file.",
            icon_path=os.path.abspath(icon_ico),
            duration=5,
            threaded=True,
        )
        print("Toast initiated successfully with ICO.")
    except Exception as e:
        print(f"Toast failed with ICO: {e}")

        traceback.print_exc()


if __name__ == "__main__":
    verify_ico_toast()
