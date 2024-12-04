from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
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

from functools import partial


class HoverButton(Button):
    """
    Кнопка с изменением цвета при наведении.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # Убираем дефолтный фон
        self.background_color = (0.5, 0.5, 0.5, 1)  # Белый фон
        self.hover_color = (0.7, 0.7, 0.7, 1)  # Серый при наведении
        self.default_color = self.background_color

        # Привязываем события движения мыши
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        """
        Отслеживаем позицию мыши.
        """
        if not self.get_parent_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            self.background_color = self.hover_color
        else:
            self.background_color = self.default_color


class IconButtonWithTooltip(MDIconButton, MDTooltip):
    """
    Класс кастомной кнопки для отображения текста при наведении на кнопку.
    """
    pass


class MyApp(MDApp):
    def build(self):
        self.texts = []
        self.text_area = TextInput(
            text="Нет текста", multiline=True, size_hint=(0.8, 1), readonly=False
        )

        # Основная панель с вкладками
        tb = TabbedPanel(do_default_tab=False, tab_pos="top_left", tab_height=22)

        # Вкладка "Фрагменты"
        fragments_tab = TabbedPanelItem(
            text="Фрагменты", font_size="12sp", size_hint=(None, None), width=50, height=22
        )
        layout = BoxLayout(orientation="vertical", spacing=10, padding=5)

        # Используем StackLayout для кнопок
        buttons_layout = StackLayout(orientation="lr-tb", size_hint_y=None, height=40)
        button1 = IconButtonWithTooltip(
            icon="folder-multiple-plus",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#35C0CD",
            icon_size="10dp",
            tooltip_text="Добавить текстов",
        )
        button1.bind(on_release=self.open_file_dialog)
        button2 = IconButtonWithTooltip(
            icon="content-save",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#35C0CD",
            icon_size="10dp",
            tooltip_text="Сохранить изменения",
        )
        button3 = IconButtonWithTooltip(
            icon="checkbox-marked-circle-outline",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#35C0CD",
            icon_size="10dp",
            tooltip_text="Отметить всё",
        )
        button3.bind(on_release=self.select_all_checkboxes)
        button4 = IconButtonWithTooltip(
            icon="checkbox-marked-circle-minus-outline",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#35C0CD",
            icon_size="10dp",
            tooltip_text="Обратить отмеченное",
        )
        button4.bind(on_release=self.disable_all_checkboxes)
        button5 = IconButtonWithTooltip(
            icon="code-brackets",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#e33d3d",
            icon_size="10dp",
            tooltip_text="Разделить текст",
        )
        button5.bind(on_release=self.split_text)

        buttons_layout.add_widget(button1)
        buttons_layout.add_widget(button2)
        buttons_layout.add_widget(button3)
        buttons_layout.add_widget(button4)
        buttons_layout.add_widget(button5)

        # Добавляем кнопки в layout
        layout.add_widget(buttons_layout)

        # Основной лэйаут с таблицей и текстовым полем
        main_layout = BoxLayout(orientation="horizontal", spacing=10)
        self.table_layout = GridLayout(cols=4, size_hint=(0.4, 1), spacing=5)

        # Устанавливаем начальные данные в таблице
        self.initialize_table()

        main_layout.add_widget(self.table_layout)
        main_layout.add_widget(self.text_area)

        layout.add_widget(main_layout)
        fragments_tab.add_widget(layout)
        tb.add_widget(fragments_tab)

        # Вкладка "Фильтры"
        filters_tab = TabbedPanelItem(
            text="Фильтры", font_size="12sp", size_hint=(None, None), width=50, height=22
        )
        filters_tab.add_widget(Label(text="Настройка фильтров"))
        tb.add_widget(filters_tab)

        # Вкладка "Словарь"
        dictionary_tab = TabbedPanelItem(
            text="Словарь", font_size="12sp", size_hint=(None, None), width=50, height=22
        )
        dictionary_tab.add_widget(Label(text="Словарь и дополнительные функции"))
        tb.add_widget(dictionary_tab)

        return tb



    ############################ Стартовое состояние программы ################################
    def initialize_table(self):
        """
        Устанавливает начальное состояние таблицы с заголовками и значением по умолчанию.
        """
        # Заголовки таблицы
        headers = ["##", "Фрагмент", "Слов", "Выбрать"]
        for header in headers:
            self.table_layout.add_widget(Label(text=header, size_hint_y=None, height=20, font_size="12sp"))

        # Добавляем начальную строку с данными
        self.table_layout.add_widget(Label(text="0", size_hint_y=None, height=20))
        self.table_layout.add_widget(Label(text="Пустой", size_hint_y=None, height=20))
        self.table_layout.add_widget(Label(text="2", size_hint_y=None, height=20))
        self.table_layout.add_widget(CheckBox(size_hint_y=None, height=20))
    #############################################################################



    ############################ Загрузка файлов ################################
    def open_file_dialog(self, instance):
        """
        Открывает диалог выбора файлов с поддержкой множественного выбора.
        """
        file_chooser = FileChooserIconView(filters=["*.txt"], multiselect=True)
        popup_content = BoxLayout(orientation="vertical")
        popup_content.add_widget(file_chooser)

        # Создаем кнопку для подтверждения выбора файлов
        confirm_button = Button(text="Загрузить файлы", size_hint_y=None, height=40)
        confirm_button.bind(on_release=lambda btn: self.load_files(file_chooser.selection, popup))

        popup_content.add_widget(confirm_button)

        # Создаем попап и отображаем его
        popup = Popup(title="Выберите файлы", content=popup_content, size_hint=(0.9, 0.9))
        popup.open()

    def load_files(self, file_paths, popup):
        """
        Загружает несколько текстовых файлов и добавляет их в таблицу.
        """
        popup.dismiss()  # Закрываем попап
        self.texts = []  # Сброс списка текстов
        self.table_layout.clear_widgets()  # Очищаем таблицу

        # Заголовки таблицы
        headers = ["##", "Фрагмент", "Слов", "Выбрать"]
        for header in headers:
            self.table_layout.add_widget(Label(text=header, size_hint_y=None, height=20, font_size="12sp"))

        # Добавляем строки таблицы
        for i, file_path in enumerate(file_paths, start=1):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read().strip()  # Убираем лишние пробелы
                    self.texts.append((file_path, text))  # Добавляем текст в список
                    words_count = len(text.split())

                    # Генерация короткого имени файла для отображения
                    file_name = file_path.split("/")[-1]  # Получаем только имя файла
                    if len(file_name) > 10:
                        fragment = f"{file_name[:4]}..{file_name[-4:]}"  # Сокращённое название
                    else:
                        fragment = file_name  # Если имя короткое, используем его целиком

                    # Используем partial для передачи правильного индекса в on_release
                    button = Button(text=str(i), size_hint_y=None, height=20)
                    button.bind(on_release=partial(self.display_text, i - 1))  # Передаем индекс

                    # Чекбокс для выбора
                    checkbox = CheckBox(size_hint_y=None, height=20)

                    # Добавляем элементы в таблицу
                    self.table_layout.add_widget(button)
                    self.table_layout.add_widget(Label(text=fragment, size_hint_y=None, height=20))
                    self.table_layout.add_widget(Label(text=str(words_count), size_hint_y=None, height=20))
                    self.table_layout.add_widget(checkbox)

            except Exception as e:
                self.text_area.text = f"Ошибка при загрузке файла {file_path}: {e}"

    def display_text(self, index, instance=None):
        """
        Отображает текст выбранного файла.
        """
        file_path, text = self.texts[index]
        # Отображение текста в правом окне
        self.text_area.text = f"{text}"
    #############################################################################





    ############################ Выделение чекбоксов ################################
    def select_all_checkboxes(self, instance):
        """
        Отмечает все чекбоксы в таблице.
        """
        for child in self.table_layout.children:
            if isinstance(child, CheckBox):
                child.active = True  # Устанавливаем активное состояние для чекбоксов

    def disable_all_checkboxes(self, instance):
        """
        Убирает отметки всех чекбоксов в таблице.
        """
        for child in self.table_layout.children:
            if isinstance(child, CheckBox):
                child.active = False  # Устанавливаем НЕактивное состояние для чекбоксов

    #############################################################################

    def split_text(self, instance):
        """
        Разделяет текст в text_area на две части, используя позицию курсора.
        Обновляет таблицу с новыми фрагментами, не добавляя старые данные.
        """
        cursor_position = self.text_area.cursor_index()  # Получаем текущую позицию курсора
        text = self.text_area.text

        # Разделяем текст на две части по позиции курсора
        first_part = text[:cursor_position].strip()
        second_part = text[cursor_position:].strip()

        # Обновляем таблицу только новыми фрагментами
        self.update_table(first_part, second_part)

    def update_table(self, first_part, second_part):
        """
        Обновляет таблицу с новыми фрагментами после разделения текста.
        Удаляет старые строки и добавляет только новые фрагменты.
        """
        # Считаем количество слов в каждом фрагменте
        first_part_word_count = len(first_part.split())
        second_part_word_count = len(second_part.split())

        # Генерация короткого имени для отображения
        fragment1 = "fl 1"
        fragment2 = "fl 2"

        # Очищаем таблицу перед добавлением новых данных
        self.table_layout.clear_widgets()

        # Добавляем заголовки
        headers = ["##", "Фрагмент", "Слов", "Выбрать"]
        for header in headers:
            self.table_layout.add_widget(Label(text=header, size_hint_y=None, height=20, font_size="12sp"))

        # Добавляем первый фрагмент
        button1 = Button(text="1", size_hint_y=None, height=20)
        button1.bind(on_press=lambda instance: self.view_fragment(first_part))  # Привязка к обработчику
        self.table_layout.add_widget(button1)
        self.table_layout.add_widget(Label(text=fragment1, size_hint_y=None, height=20))
        self.table_layout.add_widget(Label(text=str(first_part_word_count), size_hint_y=None, height=20))
        self.table_layout.add_widget(CheckBox(size_hint_y=None, height=20))

        # Добавляем второй фрагмент
        button2 = Button(text="2", size_hint_y=None, height=20)
        button2.bind(on_press=lambda instance: self.view_fragment(second_part))  # Привязка к обработчику
        self.table_layout.add_widget(button2)
        self.table_layout.add_widget(Label(text=fragment2, size_hint_y=None, height=20))
        self.table_layout.add_widget(Label(text=str(second_part_word_count), size_hint_y=None, height=20))
        self.table_layout.add_widget(CheckBox(size_hint_y=None, height=20))

    def view_fragment(self, fragment_text):
        """
        Обработчик для отображения содержимого фрагмента текста.
        Этот метод может отображать фрагмент в отдельном поле или всплывающем окне.
        """
        # Пример, как можно отобразить содержимое в text_area:
        self.text_area.text = fragment_text





if __name__ == "__main__":
    MyApp().run()
