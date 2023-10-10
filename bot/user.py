from dataclasses import dataclass

from secret import DEFAULT_LOCATION

# user type
@dataclass(init=True, repr=True)
class User:
    id: int
    display_name: str
    display_avatar: str
    location: str = DEFAULT_LOCATION
    is_signed_up: bool = False