from typing import Tuple, Optional, Set, Pattern, Union, Final
from enum import Enum
from functools import lru_cache
import os
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime
from pathlib import Path

class ContentType(Enum):
    HTML = 'text/html'
    JPEG = 'image/jpeg'

WORD_PATTERN: Final[Pattern] = re.compile(r'\b\w+\b')
HTML_CLEANER: Final[Pattern] = re.compile('<[^<]+?>')
DANGEROUS_WORDS: Final[Set[str]] = frozenset({
    "bomb", "kill", "murder", "terror", 
    "terrorist", "terrorists", "terrorism"
})
VALID_BINARY_EXT: Final[Set[str]] = frozenset({'.jpg', '.png', '.bin'})
VALID_TEXT_EXT: Final[Set[str]] = frozenset({'.txt', '.html'})
USER_AGENT: Final[str] = 'Mozilla/5.0'

class URLFetcherError(Exception):
    pass

@lru_cache(maxsize=128)
def generate_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_filename(content_type: str) -> str:
    timestamp = generate_timestamp()
    return f"image_{timestamp}.jpg" if content_type == ContentType.JPEG.value else f"content_{timestamp}.txt"

def save_content(content: Union[bytes, str], path: str, is_binary: bool = True) -> None:

    try:
        path = Path(path.strip('"\''))
        
        if path.is_dir():
            content_type = ContentType.JPEG.value if is_binary else ContentType.HTML.value
            path = path / generate_filename(content_type)
        
        if not path.suffix:
            path = path.with_suffix('.bin' if is_binary else '.txt')
        
        if is_binary and path.suffix not in VALID_BINARY_EXT:
            raise URLFetcherError(f"Invalid binary extension: {path.suffix}. Expected: {', '.join(VALID_BINARY_EXT)}")
        if not is_binary and path.suffix not in VALID_TEXT_EXT:
            raise URLFetcherError(f"Invalid text extension: {path.suffix}. Expected: {', '.join(VALID_TEXT_EXT)}")
        
        mode = 'wb' if is_binary else 'w'
        encoding = None if is_binary else 'utf-8'
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode=mode, encoding=encoding) as file:
            file.write(content if isinstance(content, (bytes, str)) else 
                      str(content).encode('utf-8') if is_binary else str(content))
        print(f"Saving succeeded to: {path}")
    except OSError as e:
        raise URLFetcherError(f"File operation failed: {e}")

def load_url(url: str, binary: bool = False) -> Union[bytes, str]:
    try:
        with urlopen(url) as response:
            content = response.read()
            return content if binary else content.decode('utf-8')
    except (URLError, HTTPError) as e:
        raise URLFetcherError(f"Failed to load URL: {e}")

@lru_cache(maxsize=1024)
def count_words(text: str) -> Set[str]:
    return {word.lower() for word in WORD_PATTERN.findall(text)} & DANGEROUS_WORDS

def check_url(url: str) -> Tuple[bool, Optional[str]]:
    try:
        url = f"{'http://' if not url.startswith(('http://', 'https://')) else ''}{url}"
        req = Request(url, headers={'User-Agent': USER_AGENT})
        
        with urlopen(req) as response:
            content_type = response.headers.get_content_type()
            return (True, ContentType.JPEG.value) if content_type == ContentType.JPEG.value else \
                   (True, ContentType.HTML.value) if response.read().decode('utf-8') else \
                   (False, None)
    except Exception as e:
        raise URLFetcherError(f"URL validation failed: {e}")

def get_user_input(prompt: str) -> str:
    return input(prompt)

def save_dangerous_words(dangerous_words: Set[str], path: str) -> None:
    try:
        path = Path(path.strip('"\''))
        
        if path.is_dir():
            path = path / f"dangerous_words_{generate_timestamp()}.txt"
        elif not path.suffix:
            path = path.with_suffix('.txt')
            
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(sorted(dangerous_words)) if dangerous_words else "No dangerous words found",
                       encoding='utf-8')
        print(f"Dangerous words saved to: {path}")
    except OSError as e:
        raise URLFetcherError(f"File operation failed: {e}")

def main() -> None:
    try:
        url = input("Give me a valid URL to download? ").strip()
        is_valid, content_type = check_url(url)
        
        if not is_valid or content_type is None:
            raise URLFetcherError("Invalid URL or unsupported content type")
            
        content = load_url(url, binary=content_type == ContentType.JPEG.value)
        path = input("Give me a valid path to save the contents? ").strip('"\'')
        
        if content_type == ContentType.HTML.value:
            text_content = HTML_CLEANER.sub('', content)
            dangerous_words = count_words(text_content)
            if dangerous_words:
                print("Dangerous words found:", ", ".join(sorted(dangerous_words)))
            save_dangerous_words(dangerous_words, path)
        else:
            save_content(content, f"{path}.jpg" if not path.endswith('.jpg') else path, is_binary=True)
            
    except URLFetcherError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")

if __name__ == "__main__":
    main()
