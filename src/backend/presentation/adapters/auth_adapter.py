from PySide6.QtCore import QObject, Signal, Slot

from ...domain.services.auth_service import AuthService


class AuthAdapter(QObject):
    loggedinChanged = Signal()
    userInfoChanged = Signal()
    loginResult = Signal(bool, str)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self._auth_service = auth_service

    @property
    def loggedin(self) -> bool:
        return self._auth_service.is_logged_in

    @property
    def current_user(self) -> str:
        return self._auth_service.current_username

    @property
    def user_nickname(self) -> str:
        return self._auth_service.current_nickname

    @Slot(str, str)
    def login(self, username: str, password: str) -> None:
        success, message, _ = self._auth_service.login(username, password)
        if success:
            self.loggedinChanged.emit()
            self.userInfoChanged.emit()
        self.loginResult.emit(success, message)

    @Slot()
    def logout(self) -> None:
        self._auth_service.logout()
        self.loggedinChanged.emit()
        self.userInfoChanged.emit()

    def initialize_login_state(self) -> None:
        self._auth_service.initialize()
        if self._auth_service.is_logged_in:
            self.loggedinChanged.emit()
            self.userInfoChanged.emit()
