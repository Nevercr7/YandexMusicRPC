"""
Модуль авторизации Yandex Music
Получение токена через браузер (ручной способ)
"""

import webbrowser
from typing import Optional

# OAuth параметры Yandex Music
CLIENT_ID = "23cabbbdc6cd418abb4b39c32c41195d"

# URL для авторизации (без redirect_uri - токен будет показан в URL)
OAUTH_URL = (
    f"https://oauth.yandex.ru/authorize?"
    f"response_type=token&"
    f"client_id={CLIENT_ID}"
)


def open_auth_page():
    """Открыть страницу авторизации в браузере"""
    webbrowser.open(OAUTH_URL)


def extract_token_from_url(url: str) -> Optional[str]:
    """
    Извлечь токен из URL после авторизации.
    
    URL будет выглядеть как:
    https://oauth.yandex.ru/verification_code#access_token=AQAEA...&token_type=bearer&expires_in=31535645
    
    Args:
        url: URL из адресной строки браузера или сам токен
        
    Returns:
        Токен или None
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Ищем access_token в URL
    if "access_token=" in url:
        # Может быть в fragment (#) или query (?)
        for separator in ['#', '?']:
            if separator in url:
                fragment = url.split(separator, 1)[-1]
                params = {}
                for param in fragment.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                
                if 'access_token' in params:
                    return params['access_token']
    
    # Если передан просто токен без URL (начинается с y0_, y1_, AQ или другой длинной строки)
    if url.startswith('y0_') or url.startswith('y1_') or url.startswith('AQ') or \
       (len(url) > 30 and ' ' not in url and '/' not in url and '.' not in url):
        return url
    
    return None


if __name__ == "__main__":
    print("="*50)
    print("  Yandex Music RPC - Получение токена")
    print("="*50)
    print("\nОткрываю страницу авторизации...")
    open_auth_page()
    print("\n" + "-"*50)
    print("После авторизации:")
    print("1. Скопируйте URL из адресной строки браузера")
    print("2. Вставьте его сюда и нажмите Enter")
    print("-"*50 + "\n")
    
    url = input("URL или токен: ")
    
    token = extract_token_from_url(url)
    if token:
        print(f"\n✓ Токен успешно извлечён!")
        print(f"  Токен: {token[:30]}...")
        print(f"\nСохраните этот токен в приложение.")
    else:
        print("\n✗ Не удалось извлечь токен.")
        print("  Попробуйте скопировать полный URL из адресной строки.")
