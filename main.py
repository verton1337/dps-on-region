import sys
import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage, Image


from kivy.config import Config

__version__ = '1.0.0' #Версия продукта

import requests
import datetime
import time
import json
from mapview import MapView, MapSource, MapMarker

class DpsApp(App):
	#Функция проверки доступности рекламы, если возвращает 200 - подключаем рекламный модуль
	def check_marketplace(self):
		responce = requests.get("http://dps.mybland.xyz/add_marketplace.txt")
		return responce.text
	#Функция проверки версии продукта
	def check_version(self):
		responce = requests.get("http://dps.mybland.xyz/version.txt")
		return responce.text
	#Функция для обновления продукта, тут пока пусто
	def update_app(self,instance):
		pass
	#Функци удаления метки с карты
	def remove_gps_dot(self,instance):
		if len(self.dots_obj)>=1:
			for i in range(len(self.dots_obj)):
				if (abs(self.google_map.lat - self.dots_obj[i].lat) < 0.0004) and (abs(self.google_map.lon - self.dots_obj[i].lon) < 0.0004):
						self.google_map.remove_marker(self.dots_obj[i])
						responce = requests.get("http://dps.mybland.xyz/remove_dot.php?x="
													+str(self.dots_obj[i].lat)+"&y="
													+str(self.dots_obj[i].lon))
						self.dots_obj.pop(i)
						break
	#Добавление метки в базу и на карте
	def add_gps_dot(self,instance):
		lat_pos = self.google_map.lat
		lon_pos = self.google_map.lon
		responce = requests.get("http://dps.mybland.xyz/add_gps_dot.php?x="+str(lat_pos)+"&y="+str(lon_pos))
		m1 = MapMarker(lat = float(lat_pos), lon = float(lon_pos))
		self.google_map.add_marker(m1)
		self.dots_obj.append(m1)

	#Функция добавления на карту маркеров из базы
	def update_gps_dot(self,lat,lon):
		m1 = MapMarker(lat = float(lat), lon = float(lon))
		self.dots_obj.append(m1)
		self.google_map.add_marker(m1)
	def update_gps_dots_list(self):
		#Добавление последних меток на карту
		dots_array = self.read_current_dots() #Создание массива точек
		current_date = datetime.datetime.today() #Получение актуальной даты
		for i in range(len(dots_array)):
			posted_date = datetime.datetime.strptime(dots_array[i]["post_time"], "%Y-%m-%d %H:%M:%S")
			delta = current_date - posted_date #Высчитывание разницы между актуальной датой и датой из записи базы
			if (delta.days < 1) and (delta.seconds < 7200): #Delta в секундах (тут 2 часа)
				self.update_gps_dot(dots_array[i]["x_pos"],dots_array[i]["y_pos"]) #Использование функции расставления меток
			else:
				#Удаление старых меток
				responce = requests.get("http://dps.mybland.xyz/remove_dot.php?x="
													+str(dots_array[i]["x_pos"])+"&y="
													+str(dots_array[i]["y_pos"]))
	#Функция получения JSON данных о метках из базы
	def read_current_dots(self):
		dots_array = []
		responce = requests.get("http://dps.mybland.xyz/return_dots.php")
		for i in responce.json():
			dots_array.append(i)
		return dots_array
	def close_market_place(self,instance):
		self.container.remove_widget(self.market_place)


	def build(self):
		self.container = FloatLayout() #Контейнер программы
		self.dots_obj = []
		self.google_map = MapView(zoom=15, lat=55.122850, lon=37.947274) # Координаты lat и lon - примерные координаты Михнево
		#60px x 60px height x 0.9  center on 121 px
		btn_down = Image(source = "source_img/button_down2.png", pos_hint={'top':0.6,'right':0.6}, size_hint = (.2 ,.2))

		#Создание экземпляра карты и помещение на нее курсора
		fl = FloatLayout()
		fl.add_widget(self.google_map)
		fl.add_widget(btn_down)
		self.container.add_widget(fl)

		#Создание кнопок Добавления и удаления меток и помещение их на основной экран приложения
		button_bl = BoxLayout(orientation="horizontal", size_hint_y = .10)
		button_bl.add_widget(Button(text = "Добавить экипаж",size = (100,50), on_press = self.add_gps_dot)) #Кнопка добавления метки
		button_bl.add_widget(Button(text = "Здесь чисто",size = (100,50), on_press = self.remove_gps_dot))
		self.container.add_widget(button_bl)

		#self.container.add_widget(Button(size_hint = (.3,.1), pos_hint = {'top': 1, 'right': 1}, text = 'Обновить', on_press=self.build))

		self.update_gps_dots_list() #Обновление списка меток на карте


		#Проверка включен ли модуль рекламы
		if self.check_marketplace() == '1':
			#Модуль с рекламой
			self.market_place = FloatLayout()
			pic_source = 'http://dps.mybland.xyz/marketplace_source/'+str(random.randint(1,3))+'.jpg'
			market_place_source = AsyncImage(source = pic_source)
			market_place_close = Button(pos_hint = {'top': 0.98, 'right' : 0.98}, text = 'X', size_hint=(.07,.06), on_press = self.close_market_place)

			self.market_place.add_widget(market_place_source)
			self.market_place.add_widget(market_place_close)
			self.container.add_widget(self.market_place)

		#Проверка версии продукта, в случае несовпадения вылезает баннер на все окно программы
		if self.check_version() != __version__:
			self.container.add_widget(Button(size_hint =(1,1), text = 'Обновите приложение по ссылке \n http://dps.mybland.xyz/index.html', on_press=self.update_app))
		return self.container

if __name__ == "__main__":
	DpsApp().run()
