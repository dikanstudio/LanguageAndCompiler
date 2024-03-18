from typing import Literal, cast

COMPILE_ERROR_EXIT_CODE = 3
RUN_ERROR_EXIT_CODE = 100

type Language = Literal['var', 'loop', 'array', 'fun']
ALL_LANGUAGES = ['var', 'loop', 'array', 'fun']

def asLanguage(s: str) -> Language:
    if s in ALL_LANGUAGES:
        return cast(Language, s)
    else:
        raise ValueError(f'Not a valid language: {s}')
