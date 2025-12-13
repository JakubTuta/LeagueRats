from .account.routes import router as account_router
from .champions.routes import router as champions_router
from .league.routes import router as league_router
from .match.routes import router as match_router
from .pro_players.routes import router as pro_players_router
from .runes.routes import router as runes_router

__all__ = [
    "account_router",
    "champions_router",
    "league_router",
    "match_router",
    "pro_players_router",
    "runes_router",
]
