from win10toast import ToastNotifier
import os


def test_toast():
    toaster = ToastNotifier()
    icon_path = os.path.abspath("icon.png")
    print(f"Testing with icon: {icon_path}")
    try:
        toaster.show_toast(
            "Test Notification",
            "This is a test.",
            icon_path=icon_path,
            duration=5,
            threaded=True,
        )
        print("Toast initiated successfully.")
    except Exception as e:
        print(f"Toast failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_toast()
