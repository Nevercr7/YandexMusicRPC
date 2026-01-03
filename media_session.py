"""
Модуль для получения информации о текущем треке через Windows Media Session API
"""

import asyncio
from dataclasses import dataclass
from typing import Optional

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)


@dataclass
class TrackInfo:
    """Информация о текущем треке"""
    title: str
    artist: str
    album: str = ""
    thumbnail: Optional[bytes] = None
    is_playing: bool = False
    duration: int = 0  # в секундах
    position: int = 0  # в секундах


class MediaSessionManager:
    """Класс для работы с Windows Media Session"""
    
    def __init__(self, app_name: str = "Yandex Music"):
        self.app_name = app_name.lower()
        self._session_manager = None
    
    async def _get_session_manager(self):
        """Получить менеджер сессий"""
        if self._session_manager is None:
            self._session_manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        return self._session_manager
    
    async def _get_yandex_session(self):
        """Найти сессию Yandex Music"""
        manager = await self._get_session_manager()
        sessions = manager.get_sessions()
        
        for session in sessions:
            source_app_id = session.source_app_user_model_id.lower()
            # Проверяем разные варианты названия приложения
            if any(name in source_app_id for name in ['yandex', 'яндекс', 'music']):
                return session
        
        return None
    
    async def get_current_track(self) -> Optional[TrackInfo]:
        """Получить информацию о текущем треке"""
        try:
            session = await self._get_yandex_session()
            if not session:
                return None
            
            # Получаем информацию о медиа
            media_properties = await session.try_get_media_properties_async()
            if not media_properties:
                return None
            
            # Получаем информацию о воспроизведении
            playback_info = session.get_playback_info()
            is_playing = playback_info.playback_status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
            
            # Получаем таймлайн
            timeline = session.get_timeline_properties()
            position = int(timeline.position.total_seconds()) if timeline else 0
            duration = int(timeline.end_time.total_seconds()) if timeline else 0
            
            # Получаем обложку (если доступна)
            thumbnail = None
            # Обложку пока пропускаем - требует дополнительных зависимостей
            
            return TrackInfo(
                title=media_properties.title or "Неизвестный трек",
                artist=media_properties.artist or "Неизвестный исполнитель",
                album=media_properties.album_title or "",
                thumbnail=thumbnail,
                is_playing=is_playing,
                duration=duration,
                position=position
            )
            
        except Exception as e:
            print(f"Ошибка получения трека: {e}")
            return None
    
    async def get_all_sessions(self) -> list:
        """Получить список всех медиа сессий (для отладки)"""
        manager = await self._get_session_manager()
        sessions = manager.get_sessions()
        return [session.source_app_user_model_id for session in sessions]


def get_track_sync() -> Optional[TrackInfo]:
    """Синхронная обёртка для получения информации о треке"""
    manager = MediaSessionManager()
    return asyncio.run(manager.get_current_track())


def list_sessions_sync() -> list:
    """Синхронная обёртка для получения списка сессий"""
    manager = MediaSessionManager()
    return asyncio.run(manager.get_all_sessions())


if __name__ == "__main__":
    # Тест модуля
    print("Доступные медиа сессии:")
    sessions = list_sessions_sync()
    for session in sessions:
        print(f"  - {session}")
    
    print("\nТекущий трек:")
    track = get_track_sync()
    if track:
        print(f"  Название: {track.title}")
        print(f"  Исполнитель: {track.artist}")
        print(f"  Альбом: {track.album}")
        print(f"  Играет: {'Да' if track.is_playing else 'Нет'}")
        print(f"  Позиция: {track.position}с / {track.duration}с")
    else:
        print("  Трек не найден. Убедитесь, что Yandex Music запущен.")
