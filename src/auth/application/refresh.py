from src.auth.application.login import TokensOutput
from src.auth.domain.errors import InvalidRefreshTokenError
from src.auth.domain.ports import IJwtAdapter, TokenPayload
from src.users.domain.ports import IUserRepository


class RefreshToken:
    def __init__(
        self,
        user_repository: IUserRepository,
        jwt_adapter: IJwtAdapter,
    ) -> None:
        self._user_repository = user_repository
        self._jwt_adapter = jwt_adapter

    async def execute(self, payload: TokenPayload) -> TokensOutput:
        user = await self._user_repository.find_by_id(payload.sub)
        if user is None:
            raise InvalidRefreshTokenError()

        new_payload = TokenPayload(sub=user.id.value, email=user.email.value, role=user.role)

        return TokensOutput(
            access_token=self._jwt_adapter.sign(new_payload),
            refresh_token=self._jwt_adapter.sign_refresh(new_payload),
        )
