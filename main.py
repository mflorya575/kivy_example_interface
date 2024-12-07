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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fragments = {}  # Словарь для хранения фрагментов
        self.files = {}
        self.table_layout = None  # Контейнер для отображения таблицы
        self.original_text = ""  # Переменная для хранения исходного текста
        self.current_fragment_to_remove = None

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
            icon="window-close",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#e33d3d",
            icon_size="10dp",
            tooltip_text="Удалить фрагмент",
        )
        button5.bind(on_release=self.delete_selected_fragments)
        button6 = IconButtonWithTooltip(
            icon="code-brackets",
            icon_color=(0.5, 0.5, 1, 1),
            md_bg_color="#e33d3d",
            icon_size="10dp",
            tooltip_text="Разделить текст",
        )
        button6.bind(on_release=self.split_text)

        buttons_layout.add_widget(button1)
        buttons_layout.add_widget(button2)
        buttons_layout.add_widget(button3)
        buttons_layout.add_widget(button4)
        buttons_layout.add_widget(button5)
        buttons_layout.add_widget(button6)

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



    ############################ Разделение фрагмента на 2 части по местоположению курсора ################################
    def split_text(self, instance):
        print("split_text called")
        cursor_position = self.text_area.cursor_index()  # Получаем текущую позицию курсора
        text = self.text_area.text.strip()

        if not text:
            print("Text is empty, aborting split")
            return

        # Проверяем, является ли это фрагментом или загруженным файлом
        original_key = None
        is_file = False
        for key, fragment_text in self.fragments.items():
            if fragment_text == text:
                original_key = key
                break

        if original_key is None:
            # Проверяем среди файлов
            for file_name, file_text in self.files.items():  # `self.files` — это словарь с загруженными файлами
                if file_text == text:
                    original_key = file_name  # Устанавливаем как имя файла
                    is_file = True
                    break

        if original_key is None:
            # Генерируем новый ключ и добавляем текст
            original_key = f"frag.{len(self.fragments) + 1}"
            self.fragments[original_key] = text
            print(f"Added original text to fragments with key: {original_key}")

        # Разделение текста
        first_part = text[:cursor_position].strip()
        second_part = text[cursor_position:].strip()

        print("First part:", first_part)
        print("Second part:", second_part)

        if not first_part or not second_part:
            print("One of the parts is empty, aborting split")
            return

        # Обновление для фрагмента
        if not is_file:
            # Удаляем исходный фрагмент из словаря
            del self.fragments[original_key]

            # Обновляем оригинальный ключ с первой частью
            self.fragments[original_key] = first_part

            # Создаем ключ для новой части
            new_key = f"{original_key}.1"

            # Добавляем новую часть
            new_fragments = {
                new_key: second_part,
            }
            self.fragments.update(new_fragments)
        else:
            # Для файлов: обновляем содержимое файла
            self.files[original_key] = first_part
            new_key = f"{original_key}.1"
            self.files[new_key] = second_part

        # Обновляем текст в text_area (оставляем первую часть)
        self.text_area.text = first_part

        print("Updated fragments/files:", self.fragments, self.files)

        # Обновляем таблицу: удаляем оригинальный элемент и добавляем обе части
        if is_file:
            self.update_table(removed_key=original_key, new_fragments={original_key: first_part, new_key: second_part})
        else:
            self.update_table(removed_key=original_key, new_fragments={original_key: first_part, new_key: second_part})

    def update_table(self, removed_key=None, new_fragments=None):
        """
        Обновляет таблицу: удаляет строку с `removed_key` и добавляет строки из `new_fragments`.
        """
        print("Updating table...")
        print(f"Removed key: {removed_key}")
        print(f"New fragments: {new_fragments}")

        if removed_key:
            # Удаляем строку, связанную с removed_key
            widgets_to_remove = []
            for i, child in enumerate(self.table_layout.children[:]):
                widget_text = getattr(child, 'text', '').strip()
                if widget_text == removed_key.strip():
                    # Удаляем строку (4 виджета: кнопка, ключ, счетчик слов, чекбокс)
                    widgets_to_remove.extend(self.table_layout.children[i:i + 4])
                    break

            if widgets_to_remove:
                for widget in widgets_to_remove:
                    print(f"Removing widget: {widget} | Text: {getattr(widget, 'text', 'No text')}")
                    self.table_layout.remove_widget(widget)
            else:
                print(f"Key {removed_key} not found in table_layout!")

        if new_fragments:
            # Добавляем новые строки для фрагментов или файлов
            for key, fragment_text in new_fragments.items():
                word_count = len(fragment_text.split())

                # Проверяем, это фрагмент или файл
                if key.startswith("frag"):
                    # Это фрагмент текста
                    button = Button(text=str(len(self.fragments)), size_hint_y=None, height=20)
                    button.bind(
                        on_press=lambda instance, text=fragment_text, key=key: self.view_fragment(text, instance, key)
                    )
                else:
                    # Это файл
                    button = Button(text=key, size_hint_y=None, height=20)
                    button.bind(
                        on_press=lambda instance, text=fragment_text, key=key: self.view_fragment(text, instance, key)
                    )

                # Добавляем новые виджеты в таблицу
                self.table_layout.add_widget(button)
                self.table_layout.add_widget(Label(text=key, size_hint_y=None, height=20))
                self.table_layout.add_widget(Label(text=str(word_count), size_hint_y=None, height=20))
                self.table_layout.add_widget(CheckBox(size_hint_y=None, height=20))

                print(f"Added fragment/file: {key} with word count {word_count}")


    def view_fragment(self, fragment_text, instance=None, fragment_key=None):
        """
        Обработчик для отображения содержимого фрагмента текста.
        Этот метод будет отображать фрагмент в text_area.
        """
        # Отображаем фрагмент в text_area
        self.text_area.text = fragment_text

        # Если это тот фрагмент, который мы разделили, удаляем его
        if fragment_key == self.current_fragment_to_remove:
            del self.fragments[fragment_key]

        # Обновляем таблицу, чтобы отобразить изменения
        self.update_table()
    #############################################################################





    ############################ Удаление фрагментов по выделенному чекбоксу ################################
    def delete_selected_fragments(self, instance):
        """Удаляет выбранные фрагменты, если активирован чекбокс."""
        fragments_to_delete = []

        # Перебираем виджеты в таблице, чтобы найти все активированные чекбоксы
        for i, widget in enumerate(self.table_layout.children[:]):
            if isinstance(widget, CheckBox) and widget.active:  # Проверяем, выбран ли чекбокс
                # Определяем индекс фрагмента, связанного с чекбоксом
                fragment_index = i // 4
                fragments_to_delete.append(fragment_index)
                print(f"Fragment with index {fragment_index} marked for deletion.")

        # Удаляем выбранные фрагменты из словаря
        removed_keys = []
        for fragment_index in fragments_to_delete:
            if fragment_index in self.fragments:
                removed_key = list(self.fragments.keys())[fragment_index]  # Получаем ключ фрагмента
                removed_keys.append(removed_key)
                del self.fragments[removed_key]
                print(f"Fragment with key {removed_key} deleted.")

        # Обновляем таблицу после удаления фрагментов
        self.update_table_after_deletion(fragments_to_delete)  # Передаем список всех фрагментов для удаления
        self.update_table()

    def update_table_after_deletion(self, fragments_to_delete):
        """Обновляет таблицу после удаления фрагментов."""
        widgets_to_remove = []

        # Перебираем все виджеты в таблице
        for i, widget in enumerate(self.table_layout.children[:]):
            # Проверяем, принадлежит ли виджет фрагментам, которые мы собираемся удалить
            if i // 4 in fragments_to_delete:  # Проверяем, связан ли виджет с фрагментом для удаления
                widgets_to_remove.append(widget)

        # Удаляем все виджеты, связанные с этими фрагментами
        for widget in widgets_to_remove:
            self.table_layout.remove_widget(widget)

    def get_fragment_index_from_checkbox(self, checkbox):
        """Получает индекс фрагмента, связанного с чекбоксом."""
        # Логика для получения индекса фрагмента, связанного с чекбоксом
        return self.table_layout.children.index(checkbox) // 4
    #############################################################################


    


if __name__ == "__main__":
    MyApp().run()
