import os
import configparser

class ConfigManager:
    """Maneja la configuración de la aplicación (config.ini)."""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            self._create_default_config()
        self.config.read(self.config_file)

    def _create_default_config(self) -> None:
        """Crea la configuración por defecto si no existe."""
        self.config['General'] = {'logo_path': ''}
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get_logo_path(self) -> str:
        """Obtiene la ruta del logo de la empresa."""
        return self.config.get('General', 'logo_path', fallback='')

    def set_logo_path(self, path: str) -> None:
        """Establece y guarda la ruta del logo de la empresa."""
        self.config.set('General', 'logo_path', path)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
