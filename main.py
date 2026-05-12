import tkinter as tk
from core.database import Database
from core.config import ConfigManager
from ui.login import LoginWindow
from ui.app import AppGestion


def main():
    """Punto de entrada principal de la aplicación."""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal inicialmente

    config_manager = ConfigManager()
    db = Database()

    def on_login_success(user_data):
        """Callback ejecutado tras un login exitoso."""
        # user_data es (id, username, rol)
        root.deiconify()  # Mostrar ventana principal
        AppGestion(root, db, user_data, config_manager)

    LoginWindow(root, db, config_manager, on_login_success)

    root.mainloop()


if __name__ == "__main__":
    main()
