from ...integration.leaderboard_fetcher import LeaderboardFetcher


class LeaderboardGateway:
    def __init__(self, leaderboard_fetcher: LeaderboardFetcher):
        self._leaderboard_fetcher = leaderboard_fetcher

    def get_catalog(self) -> list[dict] | None:
        return self._leaderboard_fetcher.get_catalog()

    def get_latest_text_by_source(self, source_key: str) -> dict | None:
        return self._leaderboard_fetcher.get_latest_text_by_source(source_key)

    def get_texts_by_source(self, source_key: str) -> list[dict] | None:
        return self._leaderboard_fetcher.get_texts_by_source(source_key)

    def get_text_by_id(self, text_id: int) -> dict | None:
        return self._leaderboard_fetcher.get_text_by_id(text_id)

    def get_leaderboard(
        self, text_id: int, page: int = 1, size: int = 50
    ) -> dict | None:
        return self._leaderboard_fetcher.get_leaderboard(text_id, page, size)
