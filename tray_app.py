"""
Yandex Music Discord Rich Presence - Tray Version
Работает в фоне с иконкой в системном трее
by @nevercr7
"""

import time
import threading
import asyncio
from typing import Optional, Callable
import os
import sys

# Для трея
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from settings import DISCORD_CLIENT_ID, get_token, get_update_interval, load_settings
from media_session import MediaSessionManager, TrackInfo
from discord_rpc import DiscordRPC
from yandex_api import get_yandex_api


class YandexMusicRPCTray:
    """Приложение с иконкой в трее"""
    
    def __init__(self, on_quit: Optional[Callable] = None, on_open: Optional[Callable] = None):
        self.media_manager = MediaSessionManager()
        self.discord = DiscordRPC(DISCORD_CLIENT_ID)
        
        token = get_token()
        self.yandex_api = get_yandex_api(token if token else None)
        
        self.running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._last_cover_key = None
        self._last_cover_url = None
        self._current_track = None
        self.icon = None
        self._update_thread = None
        self._on_quit = on_quit
        self._on_open = on_open
        self._update_interval = get_update_interval()
    
    def create_icon_image(self, color="green"):
        """Создать изображение для иконки в трее"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        if color == "green":
            fill_color = (76, 175, 80, 255)
        elif color == "yellow":
            fill_color = (255, 193, 7, 255)
        elif color == "red":
            fill_color = (244, 67, 54, 255)
        else:
            fill_color = (158, 158, 158, 255)
        
        # Рисуем круг
        draw.ellipse([4, 4, size-4, size-4], fill=fill_color)
        
        # Рисуем ноту
        draw.ellipse([18, 36, 30, 48], fill=(255, 255, 255, 255))
        draw.rectangle([28, 20, 32, 40], fill=(255, 255, 255, 255))
        draw.ellipse([34, 30, 46, 42], fill=(255, 255, 255, 255))
        draw.rectangle([44, 14, 48, 34], fill=(255, 255, 255, 255))
        draw.rectangle([28, 14, 48, 18], fill=(255, 255, 255, 255))
        
        return image
    
    def get_status_text(self):
        """Получить текст статуса для меню"""
        if self._current_track:
            status = "▶" if self._current_track.is_playing else "⏸"
            return f"{status} {self._current_track.artist} - {self._current_track.title}"
        return "Нет активного трека"
    
    def on_quit(self, icon, item):
        """Обработчик выхода"""
        self.running = False
        icon.stop()
        if self._on_quit:
            self._on_quit()
    
    def on_open(self, icon, item):
        """Открыть главное окно"""
        self.running = False
        icon.stop()
        if self._on_open:
            self._on_open()
    
    def on_show_status(self, icon, item):
        pass
    
    def update_icon(self, status="green"):
        """Обновить иконку"""
        if self.icon:
            self.icon.icon = self.create_icon_image(status)
    
    def create_menu(self):
        """Создать меню трея"""
        return pystray.Menu(
            item(
                lambda text: self.get_status_text(),
                self.on_show_status,
                enabled=False
            ),
            item("─────────────", None, enabled=False),
            item("Yandex Music RPC", None, enabled=False),
            item("by @nevercr7", None, enabled=False),
            item("─────────────", None, enabled=False),
            item("Открыть", self.on_open),
            item("Выход", self.on_quit)
        )
    
    async def _get_track(self) -> Optional[TrackInfo]:
        """Получить информацию о текущем треке"""
        return await self.media_manager.get_current_track()
    
    def _get_cover_url(self, track: TrackInfo) -> Optional[str]:
        """Получить URL обложки для трека"""
        cover_key = f"{track.artist}|{track.title}"
        
        if cover_key == self._last_cover_key:
            return self._last_cover_url
        
        try:
            cover_url = self.yandex_api.get_cover_url(track.title, track.artist)
            self._last_cover_key = cover_key
            self._last_cover_url = cover_url
            return cover_url
        except Exception:
            return None
    
    def update_loop(self):
        """Цикл обновления статуса"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # Подключаемся к Discord
        retry_count = 0
        while not self.discord.connect() and self.running:
            retry_count += 1
            if retry_count >= 5:
                self.update_icon("red")
                return
            time.sleep(5)
        
        while self.running:
            try:
                track = self._loop.run_until_complete(self._get_track())
                self._current_track = track
                
                cover_url = None
                if track:
                    cover_url = self._get_cover_url(track)
                
                if not self.discord.connected:
                    self.update_icon("red")
                    if not self.discord.connect():
                        time.sleep(self._update_interval)
                        continue
                
                settings = load_settings()
                self.discord.update_presence(track, settings.get("show_timestamp", True), cover_url)
                
                if track:
                    if track.is_playing:
                        self.update_icon("green")
                    else:
                        self.update_icon("yellow")
                else:
                    self.update_icon("gray")
                
                if self.icon:
                    self.icon.menu = self.create_menu()
                
            except Exception:
                self.update_icon("red")
            
            time.sleep(self._update_interval)
        
        self.discord.disconnect()
        if self._loop:
            self._loop.close()
    
    def run(self):
        """Запустить приложение"""
        self.running = True
        
        # Запускаем поток обновления
        self._update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self._update_thread.start()
        
        # Создаём иконку в трее
        self.icon = pystray.Icon(
            "YandexMusicRPC",
            self.create_icon_image("gray"),
            "Yandex Music RPC\nby @nevercr7",
            self.create_menu()
        )
        
        self.icon.run()


def main():
    app = YandexMusicRPCTray()
    app.run()


if __name__ == "__main__":
    main()
