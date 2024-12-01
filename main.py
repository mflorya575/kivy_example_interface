from kivymd.app import MDApp

from kivy.uix.stacklayout import StackLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip


class HoverButton(Button):
    """Кнопка с изменением цвета при наведении."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # Убираем дефолтный фон
        self.background_color = (0.5, 0.5, 0.5, 1)  # Белый фон
        self.hover_color = (0.7, 0.7, 0.7, 1)  # Серый при наведении
        self.default_color = self.background_color

        # Привязываем события движения мыши
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        """Отслеживаем позицию мыши."""
        if not self.get_parent_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            self.background_color = self.hover_color
        else:
            self.background_color = self.default_color


class IconButtonWithTooltip(MDIconButton, MDTooltip):
    pass


class MyApp(MDApp):
    def build(self):
        # Основная панель с вкладками
        tb = TabbedPanel(do_default_tab=False, tab_pos="top_left", tab_height=22)

        # Вкладка "Фрагменты"
        fragments_tab = TabbedPanelItem(text="Фрагменты", font_size="12sp", size_hint=(None, None), width=50, height=22)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=5)

        # Используем StackLayout для кнопок
        buttons_layout = StackLayout(orientation="lr-tb", size_hint_y=None, height=40)
        button1 = IconButtonWithTooltip(icon="folder-multiple-plus", icon_color=(0.5, 0.5, 1, 1), md_bg_color='#35C0CD', icon_size="10dp", tooltip_text="Добавить текстов")
        button2 = IconButtonWithTooltip(icon="content-save", icon_color=(0.5, 0.5, 1, 1), md_bg_color='#35C0CD', icon_size="10dp", tooltip_text="Сохранить изменения")
        button3 = IconButtonWithTooltip(icon="checkbox-marked-circle-outline", icon_color=(0.5, 0.5, 1, 1), md_bg_color='#35C0CD', icon_size="10dp", tooltip_text="Отметить всё")
        button4 = IconButtonWithTooltip(icon="checkbox-marked-circle-minus-outline", icon_color=(0.5, 0.5, 1, 1), md_bg_color='#35C0CD', icon_size="10dp", tooltip_text="Обратить отмеченное")

        buttons_layout.add_widget(button1)
        buttons_layout.add_widget(button2)
        buttons_layout.add_widget(button3)
        buttons_layout.add_widget(button4)

        # Добавляем кнопки в layout
        layout.add_widget(buttons_layout)

        # Создаем BoxLayout с горизонтальной ориентацией для размещения таблицы и текстового поля рядом
        main_layout = BoxLayout(orientation="horizontal", spacing=10)

        # Таблица (слева)
        table_layout = GridLayout(cols=3, size_hint=(0.3, 1), spacing=0)
        table_layout.bind(minimum_height=table_layout.setter('height'))

        # Добавляем заголовки
        headers = ["##", "Фрагмент", "Слов"]
        for header in headers:
            label = Label(text=header, size_hint_y=None, height=20, font_size="12sp")
            table_layout.add_widget(label)

        # Добавляем строки с реакцией на наведение
        for i in range(10):
            for col in [f"{i + 1}", f"{i + 1}.txt", f"{i * 100}"]:
                btn = HoverButton(text=col, size_hint_y=None, height=20)
                table_layout.add_widget(btn)

        # Область текста (справа)
        text_area = TextInput(text="Нет текста", multiline=True, size_hint=(0.8, 1))

        # Добавляем таблицу и текстовую область в основной лэйаут
        main_layout.add_widget(table_layout)
        main_layout.add_widget(text_area)

        # Добавляем основной лэйаут и кнопки во вкладку
        layout.add_widget(main_layout)
        fragments_tab.add_widget(layout)
        tb.add_widget(fragments_tab)

        # Вкладка "Фильтры"
        filters_tab = TabbedPanelItem(text="Фильтры", font_size="12sp", size_hint=(None, None), width=50, height=22)
        filters_tab.add_widget(Label(text="Настройка фильтров"))
        tb.add_widget(filters_tab)

        # Вкладка "Словарь"
        dictionary_tab = TabbedPanelItem(text="Словарь", font_size="12sp", size_hint=(None, None), width=50, height=22)
        dictionary_tab.add_widget(Label(text="Словарь и дополнительные функции"))
        tb.add_widget(dictionary_tab)

        return tb


if __name__ == "__main__":
    MyApp().run()
