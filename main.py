from app import UltimateRegistrationApp
from logging_config import setup_logging


def main():
    """Main function for running the face recognition system."""
    setup_logging()
    app = UltimateRegistrationApp()

    while True:
        print("\n" + "=" * 30)
        print("Ultimate Face Recognition System")
        print("1. Start live recognition with registration")
        print("2. Register employee (multi-pose webcam)")
        print("3. Register employee from photos")
        print("4. List employees")
        print("5. Mark attendance")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            app.run_webcam()
        elif choice == '2':
            app.register_multi_pose_webcam()
        elif choice == '3':
            app.register_from_photos()
        elif choice == '4':
            app.list_all_employees()
        elif choice == '5':
            app.mark_attendance()
        else:
            print("Invalid choice")
            break


if __name__ == "__main__":
    main()
