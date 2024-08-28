from enum import Enum
from dataclasses import dataclass


class RegistrationStatus(Enum):
    UNREGISTERED = 0
    REGISTERED_INACTIVE = 1
    REGISTERED_ACTIVE = 2
    REGISTRATION_ERROR = 3


class UsernameStatus(Enum):
    NAME_AVAILABLE = 0
    NAME_TAKEN_THIS_USER = 1
    NAME_TAKEN_OTHER_USER = 2
    NAME_ERROR = 3


@dataclass
class User:
    mUserId: int
    mDiscordId: int
    mDiscordUsername: str
    mUsername: str
    mActive: bool


@dataclass
class Queue:
    mUserId : int
    mUsername: str


@dataclass
class Matchup:
    mUserId: int
    mOpponentUserId: int
    mGamesSinceLast: int
    mWins: int
    mLosses: int


@dataclass
class PairingsMatch:
    mUserIdOne: int
    mUserIdTwo: int
    mPairingScore: int
