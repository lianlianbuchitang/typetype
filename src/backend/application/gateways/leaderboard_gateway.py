from ...ports.leaderboard_provider import LeaderboardProvider


class LeaderboardGateway:
    def __init__(self, leaderboard_provider: LeaderboardProvider):
        self._leaderboard_provider = leaderboard_provider

    def get_catalog(self) -> list[dict] | None:
        return self._leaderboard_provider.get_catalog()

    def get_latest_text_by_source(self, source_key: str) -> dict | None:
        return self._leaderboard_provider.get_latest_text_by_source(source_key)

    def get_texts_by_source(self, source_key: str) -> list[dict] | None:
        return self._leaderboard_provider.get_texts_by_source(source_key)

    def get_text_by_id(self, text_id: int) -> dict | None:
        return self._leaderboard_provider.get_text_by_id(text_id)

    def get_leaderboard(
        self, text_id: int, page: int = 1, size: int = 50
    ) -> dict | None:
        return self._leaderboard_provider.get_leaderboard(text_id, page, size)
