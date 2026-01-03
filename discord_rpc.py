"""
Модуль для работы с Discord Rich Presence
"""

import time
from typing import Optional
from pypresence import Presence, DiscordNotFound, PipeClosed, ActivityType
from media_session import TrackInfo


class DiscordRPC:
    """Класс для управления Discord Rich Presence"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc: Optional[Presence] = None
        self.connected = False
        self._last_track_key = None
    
    def connect(self) -> bool:
        """Подключиться к Discord"""
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            print("✓ Подключено к Discord")
            return True
        except DiscordNotFound:
            print("✗ Discord не найден. Убедитесь, что Discord запущен.")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Ошибка подключения к Discord: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Отключиться от Discord"""
        if self.rpc and self.connected:
            try:
                self.rpc.clear()
                self.rpc.close()
            except Exception:
                pass
            self.connected = False
            print("Отключено от Discord")
    
    def update_presence(self, track: Optional[TrackInfo], show_timestamp: bool = True, 
                        cover_url: Optional[str] = None) -> bool:
        """Обновить статус в Discord"""
        if not self.connected or not self.rpc:
            return False
        
        try:
            if track is None:
                # Нет трека - очищаем статус
                if self._last_track_key is not None:
                    self.rpc.clear()
                    self._last_track_key = None
                    print("Статус очищен (нет активного трека)")
                return True
            
            # Формируем ключ для проверки изменений
            # НЕ включаем position, чтобы не спамить обновлениями
            track_key = f"{track.title}|{track.artist}|{track.is_playing}"
            
            # Обновляем если:
            # 1. Трек изменился
            # 2. Статус воспроизведения изменился  
            # 3. Каждые 15 секунд для обновления таймера
            should_update = (
                track_key != self._last_track_key or
                (show_timestamp and track.is_playing and 
                 int(time.time()) % 15 == 0)  # Обновляем таймер каждые 15 сек
            )
            
            if not should_update:
                return True
            
            self._last_track_key = track_key
            
            # Формируем данные для Discord
            details = track.title[:128] if len(track.title) > 128 else track.title
            state = track.artist[:128] if len(track.artist) > 128 else track.artist
            
            # Используем обложку трека или дефолтную иконку
            large_image = cover_url if cover_url else "yandex_music"
            
            # Маленький текст статуса
            small_text = "Играет" if track.is_playing else "На паузе"
            small_image = "play" if track.is_playing else "pause"
            
            # Параметры для Discord
            presence_data = {
                "details": details,
                "state": state,
                "large_image": large_image,
                "large_text": track.album if track.album else "Yandex Music",
                "small_image": small_image,
                "small_text": "by @nevercr7 | t.me/nevercr7",
                "activity_type": ActivityType.LISTENING,  # Listening to...
            }
            
            # Добавляем время, если трек играет
            if show_timestamp and track.is_playing and track.duration > 0:
                # start = когда трек начался (текущее время минус позиция)
                # end = когда трек закончится (start + длительность)
                start_time = int(time.time()) - track.position
                end_time = start_time + track.duration
                presence_data["start"] = start_time
                presence_data["end"] = end_time
            
            # Добавляем кнопки с ссылками на создателя
            presence_data["buttons"] = [
                {"label": "Telegram", "url": "https://t.me/nevercr7dev"},
                {"label": "GitHub", "url": "https://github.com/Nevercr7/YandexMusicRPC"}
            ]
            
            self.rpc.update(**presence_data)
            
            status = "▶" if track.is_playing else "⏸"
            print(f"{status} {track.artist} - {track.title}")
            if cover_url:
                print(f"  🖼 Обложка: {cover_url[:50]}...")
            
            return True
            
        except PipeClosed:
            print("Соединение с Discord потеряно")
            self.connected = False
            return False
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
            return False
    
    def clear_presence(self):
        """Очистить статус"""
        if self.connected and self.rpc:
            try:
                self.rpc.clear()
                self._last_track_key = None
            except Exception:
                pass


if __name__ == "__main__":
    # Тест модуля
    from config import DISCORD_CLIENT_ID
    
    if DISCORD_CLIENT_ID == "YOUR_DISCORD_CLIENT_ID_HERE":
        print("Сначала укажите DISCORD_CLIENT_ID в config.py!")
    else:
        rpc = DiscordRPC(DISCORD_CLIENT_ID)
        if rpc.connect():
            # Тестовый трек
            test_track = TrackInfo(
                title="Тестовый трек",
                artist="Тестовый исполнитель",
                album="Тестовый альбом",
                is_playing=True,
                duration=180,
                position=60
            )
            rpc.update_presence(test_track)
            print("Статус обновлён! Проверьте Discord...")
            time.sleep(30)
            rpc.disconnect()
