"""
Модуль для получения информации о треках из Yandex Music API
Используется для получения обложек альбомов
"""

from typing import Optional
from yandex_music import Client


class YandexMusicAPI:
    """Класс для работы с Yandex Music API"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация клиента Yandex Music
        
        Args:
            token: OAuth токен Yandex Music (опционально, без него работает с ограничениями)
        """
        self.token = token
        self._client: Optional[Client] = None
        self._cover_cache: dict = {}  # Кэш обложек
    
    def _get_client(self) -> Client:
        """Получить или создать клиент"""
        if self._client is None:
            try:
                if self.token:
                    self._client = Client(self.token).init()
                else:
                    # Без токена - ограниченный функционал, но поиск работает
                    self._client = Client().init()
            except Exception as e:
                print(f"Ошибка инициализации Yandex Music API: {e}")
                raise
        return self._client
    
    def search_track(self, title: str, artist: str) -> Optional[dict]:
        """
        Поиск трека по названию и исполнителю
        
        Returns:
            dict с информацией о треке или None
        """
        try:
            client = self._get_client()
            
            # Формируем поисковый запрос
            query = f"{artist} - {title}"
            
            # Ищем
            search_result = client.search(query, type_='track')
            
            if search_result and search_result.tracks and search_result.tracks.results:
                track = search_result.tracks.results[0]
                return {
                    'id': track.id,
                    'title': track.title,
                    'artist': ', '.join([a.name for a in track.artists]) if track.artists else '',
                    'album': track.albums[0].title if track.albums else '',
                    'cover_uri': track.cover_uri,
                    'duration_ms': track.duration_ms,
                }
            
            return None
            
        except Exception as e:
            print(f"Ошибка поиска трека: {e}")
            return None
    
    def get_cover_url(self, title: str, artist: str, size: str = "400x400") -> Optional[str]:
        """
        Получить URL обложки для трека
        
        Args:
            title: Название трека
            artist: Исполнитель
            size: Размер обложки (например, "200x200", "400x400", "1000x1000")
            
        Returns:
            URL обложки или None
        """
        # Проверяем кэш
        cache_key = f"{artist}|{title}"
        if cache_key in self._cover_cache:
            return self._cover_cache[cache_key]
        
        try:
            track_info = self.search_track(title, artist)
            
            if track_info and track_info.get('cover_uri'):
                # Формируем URL обложки
                cover_uri = track_info['cover_uri']
                # Заменяем %%  на размер
                cover_url = f"https://{cover_uri.replace('%%', size)}"
                
                # Сохраняем в кэш
                self._cover_cache[cache_key] = cover_url
                
                return cover_url
            
            return None
            
        except Exception as e:
            print(f"Ошибка получения обложки: {e}")
            return None
    
    def clear_cache(self):
        """Очистить кэш обложек"""
        self._cover_cache.clear()


# Синглтон для использования во всём приложении
_api_instance: Optional[YandexMusicAPI] = None


def get_yandex_api(token: Optional[str] = None) -> YandexMusicAPI:
    """Получить инстанс API"""
    global _api_instance
    if _api_instance is None:
        _api_instance = YandexMusicAPI(token)
    return _api_instance


if __name__ == "__main__":
    # Тест модуля
    api = YandexMusicAPI()
    
    # Тестовый поиск
    test_artist = "zxcursed"
    test_title = "waste"
    
    print(f"Поиск: {test_artist} - {test_title}")
    
    track = api.search_track(test_title, test_artist)
    if track:
        print(f"Найдено: {track['artist']} - {track['title']}")
        print(f"Альбом: {track['album']}")
        
        cover_url = api.get_cover_url(test_title, test_artist)
        if cover_url:
            print(f"Обложка: {cover_url}")
    else:
        print("Трек не найден")
