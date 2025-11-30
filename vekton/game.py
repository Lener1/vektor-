import pygame
import random
import sys
import os
import subprocess
import importlib.util

# Цвета
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
DARK_BLUE = (50, 50, 70)
LIGHT_BLUE = (100, 100, 200)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Игровые состояния
MAIN_MENU = 0
GAME_SCREEN = 1
MOL_MENU = 2
BUILD_MENU = 3
SETTINGS_MENU = 4

# Доступные разрешения экрана
RESOLUTIONS = [
    (1900, 1000),
    (1600, 900),
    (1366, 768),
    (1280, 720),
    (1024, 576),
    (0, 0)  # Автоматическое определение
]

def verify_environment():
    """Проверка безопасности окружения"""
    try:
        # Проверяем, что работаем в нормальной директории
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(current_dir):
            return False
        
        # Проверяем основные файлы
        required_files = ['game.py']
        for file in required_files:
            if not os.path.exists(os.path.join(current_dir, file)):
                return False
                
        return True
    except Exception:
        return False

def load_image(filename, size=None):
    """Безопасная загрузка изображения или создание заглушки"""
    try:
        # Сначала пробуем загрузить из текущей директории
        if os.path.exists(filename):
            image = pygame.image.load(filename)
        else:
            # Пробуем загрузить из папки images
            image_path = os.path.join("images", filename)
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
            else:
                # Создаем цветную заглушку
                placeholder = pygame.Surface(size if size else (50, 50))
                colors = {
                    "bg_image.png": (50, 100, 150),
                    "Play.png": (200, 0, 0),
                    "mol.jpg": (0, 0, 255),
                    "corner.jpg": (255, 0, 0),
                    "corner1.jpg": (0, 255, 0),
                    "gelezo.jpg": (100, 100, 100),
                    "medi.jpg": (255, 165, 0),
                    "forest.jpg": (0, 100, 0),
                    "nefti.jpg": (0, 0, 0),
                    "pole.jpg": (210, 180, 140),
                    "polena.jpg": (139, 69, 19),
                    "zavod.jpg": (128, 128, 128), 
                    "ibrari.jpg": (75, 0, 130),
                    "fika.jpg": (255, 192, 203),
                    "losplka.jpg": (160, 82, 45),
                    "voenka.jpg": (139, 0, 0),
                    "soldat.jpg": (220, 20, 60),
                    "people.jpg": (200, 200, 100),
                    "stone.png": (150, 150, 150),
                    "components.jpg": (150, 0, 100),
                    "rydnik glezo.jpg": (80, 80, 120),
                    "rydnik kamini.jpg": (120, 120, 120),
                    "rydnik midi.jpg": (200, 120, 50),
                    "settings.png": (100, 100, 200),
                    "настройки.png": (100, 100, 200)
                }

                if filename in colors:
                    placeholder.fill(colors[filename])
                else:
                    placeholder.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

                return placeholder

        if size:
            image = pygame.transform.scale(image, size)
        return image.convert_alpha()

    except pygame.error as e:
        print(f"Ошибка загрузки изображения {filename}: {e}")
        placeholder = pygame.Surface(size if size else (50, 50))
        placeholder.fill((200, 100, 100))
        return placeholder

class Game:
    def __init__(self):
        pygame.init()
        
        # Автоматическое определение разрешения экрана
        self.current_resolution = 5
        self.screen_info = pygame.display.Info()
        self.screen_width = self.screen_info.current_w
        self.screen_height = self.screen_info.current_h
        
        # Устанавливаем окно на весь экран
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("vektor  ")

        self.state = MAIN_MENU
        self.clock = pygame.time.Clock()
        
        # Расчет размеров элементов на основе разрешения экрана
        self.cell_size = max(30, min(50, self.screen_width // 40))
        self.font_size_small = max(14, self.screen_width // 100)
        self.font_size_medium = max(18, self.screen_width // 80)
        self.font_size_large = max(24, self.screen_width // 60)
        self.font_size_title = max(36, self.screen_width // 40)
        
        # Обновляем размеры элементов интерфейса
        self.update_ui_elements()

        self.resources = []
        self.buildings = []
        self.military_units = []
        self.turn_count = 1

        # Ресурсы игрока
        self.player_resources = {
            "Дерево": 200,
            "Железо": 200,
            "Медь": 200,
            "Нефть": 0,
            "Люди": 0,
            "Камень": 200,
            "компоненты": 150
        }

        # Стоимость построек
        self.building_costs = {
            "Лесопилка": {"Дерево": 10, "Камень": 5, "компоненты": 3},
            "Завод": {"Железо": 5, "Медь": 5, "компоненты": 5},
            "Лаборатория": {"Дерево": 100, "Камень": 100, "компоненты": 50, "Медь": 100},
            "Военный завод": {"Железо": 6, "Дерево": 7, "компоненты": 2},
            "Нефтяная вышка": {"Железо": 8, "Дерево": 10, "компоненты": 5},
            "Железная шахта": {"Дерево": 15, "Камень": 10, "компоненты": 8},
            "Каменная шахта": {"Дерево": 12, "Железо": 5, "компоненты": 6},
            "Медная шахта": {"Дерево": 10, "Камень": 8, "компоненты": 5}
        }

        # Потребление ресурсов зданиями каждый ход
        self.building_upkeep = {
            "Завод": {"Железо": 1, "Медь": 1},
            "Лаборатория": {"компоненты": 2},
            "Военный завод": {"Железо": 1}
        }

        # Производство ресурсов зданиями каждый ход
        self.building_production = {
            "Завод": {"компоненты": 2},
            "Лесопилка": {"Дерево": 1},
            "Нефтяная вышка": {"Нефть": 1},
            "Лаборатория": {"компоненты": 3},
            "Железная шахта": {"Железо": 1},
            "Каменная шахта": {"Камень": 1},
            "Медная шахта": {"Медь": 1}
        }

        # Стоимость юнитов
        self.unit_costs = {
            "Солдат": {"Люди": 5}
        }

        # Загрузка изображений
        self.load_images()

        # Размещаем углы
        self.corner_pos = (self.screen_width - 100, self.screen_height - 100)
        self.corner1_pos = (50, 50)

        # Генерируем ресурсы на карте
        self.generate_resources()

        # Выбранное здание для строительства
        self.selected_building = None

        # Для анимации наведения в меню построек
        self.hovered_building = None

    def update_ui_elements(self):
        """Обновление размеров и позиций элементов интерфейса"""
        button_width = max(150, self.screen_width // 10)
        button_height = max(40, self.screen_height // 20)
        menu_width = max(700, self.screen_width // 2)
        menu_height = max(600, self.screen_height // 2)
        
        self.mol_menu_rect = pygame.Rect(
            self.screen_width // 2 - menu_width // 2,
            self.screen_height // 2 - menu_height // 2,
            menu_width, menu_height
        )
        self.mol_button_rect = pygame.Rect(
            self.screen_width - button_width - 20, 20,
            button_width // 3, button_height
        )
        self.end_turn_button_rect = pygame.Rect(
            self.screen_width - button_width - 20,
            self.screen_height - button_height - 20,
            button_width, button_height
        )
        self.settings_button_rect = pygame.Rect(
            self.screen_width // 2 - button_width // 2,
            self.screen_height // 2 + 120,
            button_width, button_height
        )

    def load_images(self):
        """Загрузка всех изображений с адаптивными размерами"""
        bg_size = (self.screen_width, self.screen_height)
        button_size = (max(150, self.screen_width // 8), max(60, self.screen_height // 15))
        icon_size = (self.cell_size, self.cell_size)
        
        self.bg_image = load_image("bg_image.png", bg_size)
        self.play_button = load_image("Play.png", button_size)
        self.corner_image = load_image("corner.jpg", icon_size)
        self.corner1_image = load_image("corner1.jpg", icon_size)
        self.mol_image = load_image("mol.jpg", icon_size)
        self.gelezo_image = load_image("gelezo.jpg", icon_size)
        self.medi_image = load_image("medi.jpg", icon_size)
        self.forest_image = load_image("forest.jpg", icon_size)
        self.nefti_image = load_image("nefti.jpg", icon_size)
        self.pole_image = load_image("pole.jpg", icon_size)
        self.polena_image = load_image("polena.jpg", icon_size)
        self.zavod_image = load_image("zavod.jpg", icon_size)
        self.ibrari_image = load_image("ibrari.jpg", icon_size)
        self.fika_image = load_image("fika.jpg", icon_size)
        self.losplka_image = load_image("losplka.jpg", icon_size)
        self.voenka_image = load_image("voenka.jpg", icon_size)
        self.soldat_image = load_image("soldat.jpg", icon_size)
        self.people_image = load_image("people.jpg", icon_size)
        self.stone_image = load_image("stone.png", icon_size)
        self.components_image = load_image("components.jpg", icon_size)
        self.rydnik_glezo_image = load_image("rydnik glezo.jpg", icon_size)
        self.rydnik_kamini_image = load_image("rydnik kamini.jpg", icon_size)
        self.rydnik_midi_image = load_image("rydnik midi.jpg", icon_size)
        self.settings_image = load_image("settings.png", button_size)

        # Создаем список всех ресурсов для размещения на карте
        self.resource_types = [
            self.gelezo_image, self.medi_image, self.forest_image,
            self.nefti_image, self.pole_image, self.stone_image
        ]

        # Соответствие изображений зданий их типам
        self.building_images = {
            "Лесопилка": self.losplka_image,
            "Завод": self.zavod_image,
            "Лаборатория": self.ibrari_image,
            "Нефтяная вышка": self.fika_image,
            "Военный завод": self.voenka_image,
            "Железная шахта": self.rydnik_glezo_image,
            "Каменная шахта": self.rydnik_kamini_image,
            "Медная шахта": self.rydnik_midi_image
        }

        # Соответствие изображений юнитов их типам
        self.unit_images = {
            "Солдат": self.soldat_image
        }

    def change_resolution(self, resolution_index):
        """Изменение разрешения экрана"""
        if 0 <= resolution_index < len(RESOLUTIONS):
            self.current_resolution = resolution_index
            
            if resolution_index == 5:
                self.screen_width = self.screen_info.current_w
                self.screen_height = self.screen_info.current_h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            else:
                self.screen_width, self.screen_height = RESOLUTIONS[resolution_index]
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            
            self.cell_size = max(30, min(50, self.screen_width // 40))
            self.font_size_small = max(14, self.screen_width // 100)
            self.font_size_medium = max(18, self.screen_width // 80)
            self.font_size_large = max(24, self.screen_width // 60)
            self.font_size_title = max(36, self.screen_width // 40)
            
            self.update_ui_elements()
            self.load_images()
            self.generate_resources()
            
            return True
        return False

    def generate_resources(self):
        """Генерация ресурсов на карте с адаптивным количеством"""
        self.resources = []
        num_resources = max(50, (self.screen_width * self.screen_height) // 2500)
        
        for _ in range(num_resources):
            x = random.randint(1, (self.screen_width - 200) // self.cell_size - 1) * self.cell_size
            y = random.randint(1, (self.screen_height - 100) // self.cell_size - 1) * self.cell_size
            resource_type = random.choice(self.resource_types)
            self.resources.append({
                'image': resource_type,
                'pos': (x, y),
                'type': self.get_resource_type(resource_type)
            })

    def get_resource_type(self, image):
        """Определение типа ресурса по изображению"""
        if image == self.gelezo_image: return "Железо"
        if image == self.medi_image: return "Медь"
        if image == self.forest_image: return "Дерево"
        if image == self.nefti_image: return "Нефть"
        if image == self.pole_image: return "Поле"
        if image == self.stone_image: return "Камень"
        if image == self.components_image: return "компоненты"
        return "Неизвестно"

    def can_afford_building(self, building_type):
        """Проверка, хватает ли ресурсов для постройки"""
        if building_type not in self.building_costs:
            return False

        for resource, amount in self.building_costs[building_type].items():
            if self.player_resources.get(resource, 0) < amount:
                return False
        return True

    def can_afford_upkeep(self, building_type):
        """Проверка, хватает ли ресурсов для содержания здания"""
        if building_type not in self.building_upkeep:
            return True

        for resource, amount in self.building_upkeep[building_type].items():
            if self.player_resources.get(resource, 0) < amount:
                return False
        return True

    def can_afford_unit(self, unit_type):
        """Проверка, хватает ли ресурсов для создания юнита"""
        if unit_type not in self.unit_costs:
            return False

        for resource, amount in self.unit_costs[unit_type].items():
            if self.player_resources.get(resource, 0) < amount:
                return False
        return True

    def deduct_building_cost(self, building_type):
        """Вычитание ресурсов за постройку"""
        if building_type in self.building_costs:
            for resource, amount in self.building_costs[building_type].items():
                self.player_resources[resource] -= amount

    def deduct_unit_cost(self, unit_type):
        """Вычитание ресурсов за создание юнита"""
        if unit_type in self.unit_costs:
            for resource, amount in self.unit_costs[unit_type].items():
                self.player_resources[resource] -= amount

    def get_building_production(self, building_type):
        """Возвращает информацию о производстве здания"""
        production_info = ""
        
        if building_type in self.building_production:
            for resource, amount in self.building_production[building_type].items():
                production_info += f"+{amount} {resource} "
        
        if building_type in self.building_upkeep:
            for resource, amount in self.building_upkeep[building_type].items():
                production_info += f"-{amount} {resource} "
        
        return production_info.strip() if production_info else "Нет производства"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == MAIN_MENU:
                        play_rect = self.play_button.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                        if play_rect.collidepoint(mouse_pos):
                            self.state = GAME_SCREEN
                        elif self.settings_button_rect.collidepoint(mouse_pos):
                            self.state = SETTINGS_MENU

                    elif self.state == GAME_SCREEN:
                        if self.mol_button_rect.collidepoint(mouse_pos):
                            self.state = MOL_MENU
                        elif self.end_turn_button_rect.collidepoint(mouse_pos):
                            self.end_turn()
                        else:
                            if self.selected_building:
                                self.try_build_building(mouse_pos, self.selected_building)
                            self.try_create_soldier(mouse_pos)

                    elif self.state == MOL_MENU:
                        close_rect = pygame.Rect(self.mol_menu_rect.right - 30, self.mol_menu_rect.y + 10, 20, 20)
                        if close_rect.collidepoint(mouse_pos):
                            self.state = GAME_SCREEN
                            self.selected_building = None
                        else:
                            button_size = 80
                            button_margin = 20
                            start_x = self.mol_menu_rect.x + 50
                            start_y = self.mol_menu_rect.y + 80
                            
                            building_buttons = [
                                {"rect": pygame.Rect(start_x, start_y, button_size, button_size), "type": "Завод"},
                                {"rect": pygame.Rect(start_x + button_size + button_margin, start_y, button_size, button_size), "type": "Лаборатория"},
                                {"rect": pygame.Rect(start_x + (button_size + button_margin) * 2, start_y, button_size, button_size), "type": "Нефтяная вышка"},
                                {"rect": pygame.Rect(start_x + (button_size + button_margin) * 3, start_y, button_size, button_size), "type": "Лесопилка"},
                                {"rect": pygame.Rect(start_x, start_y + button_size + 80, button_size, button_size), "type": "Военный завод"},
                                {"rect": pygame.Rect(start_x + button_size + button_margin, start_y + button_size + 80, button_size, button_size), "type": "Железная шахта"},
                                {"rect": pygame.Rect(start_x + (button_size + button_margin) * 2, start_y + button_size + 80, button_size, button_size), "type": "Каменная шахта"},
                                {"rect": pygame.Rect(start_x + (button_size + button_margin) * 3, start_y + button_size + 80, button_size, button_size), "type": "Медная шахта"}
                            ]

                            for button in building_buttons:
                                if button["rect"].collidepoint(mouse_pos):
                                    if self.can_afford_building(button["type"]):
                                        print(f"Выбрана постройка: {button['type']}")
                                        self.selected_building = button["type"]
                                        self.state = GAME_SCREEN
                                    else:
                                        print(f"Не хватает ресурсов для постройки {button['type']}")
                                    break

                    elif self.state == SETTINGS_MENU:
                        close_rect = pygame.Rect(self.mol_menu_rect.right - 30, self.mol_menu_rect.y + 10, 20, 20)
                        if close_rect.collidepoint(mouse_pos):
                            self.state = MAIN_MENU
                        
                        resolution_buttons = []
                        for i, resolution in enumerate(RESOLUTIONS):
                            button_rect = pygame.Rect(
                                self.mol_menu_rect.x + 50,
                                self.mol_menu_rect.y + 60 + i * 60,
                                self.mol_menu_rect.width - 100,
                                50
                            )
                            resolution_buttons.append({"rect": button_rect, "index": i})
                        
                        for button in resolution_buttons:
                            if button["rect"].collidepoint(mouse_pos):
                                self.change_resolution(button["index"])
                                break

            if self.state == MOL_MENU:
                mouse_pos = pygame.mouse.get_pos()
                self.hovered_building = None
                
                button_size = 80
                button_margin = 20
                start_x = self.mol_menu_rect.x + 50
                start_y = self.mol_menu_rect.y + 80
                
                building_buttons = [
                    {"rect": pygame.Rect(start_x, start_y, button_size, button_size), "type": "Завод"},
                    {"rect": pygame.Rect(start_x + button_size + button_margin, start_y, button_size, button_size), "type": "Лаборатория"},
                    {"rect": pygame.Rect(start_x + (button_size + button_margin) * 2, start_y, button_size, button_size), "type": "Нефтяная вышка"},
                    {"rect": pygame.Rect(start_x + (button_size + button_margin) * 3, start_y, button_size, button_size), "type": "Лесопилка"},
                    {"rect": pygame.Rect(start_x, start_y + button_size + 80, button_size, button_size), "type": "Военный завод"},
                    {"rect": pygame.Rect(start_x + button_size + button_margin, start_y + button_size + 80, button_size, button_size), "type": "Железная шахта"},
                    {"rect": pygame.Rect(start_x + (button_size + button_margin) * 2, start_y + button_size + 80, button_size, button_size), "type": "Каменная шахта"},
                    {"rect": pygame.Rect(start_x + (button_size + button_margin) * 3, start_y + button_size + 80, button_size, button_size), "type": "Медная шахта"}
                ]
                
                for button in building_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        self.hovered_building = button["type"]
                        break

        return True

    def try_build_building(self, mouse_pos, building_type):
        """Попытка построить здание"""
        grid_x = (mouse_pos[0] // self.cell_size) * self.cell_size
        grid_y = (mouse_pos[1] // self.cell_size) * self.cell_size

        for building in self.buildings:
            if building['pos'] == (grid_x, grid_y):
                return

        # Проверки для специальных зданий
        if building_type == "Железная шахта":
            can_build = False
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y) and resource['type'] == "Железо":
                    can_build = True
                    break
            if not can_build:
                return
        
        elif building_type == "Лесопилка":
            can_build = False
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y) and resource['type'] == "Дерево":
                    can_build = True
                    break
            if not can_build:
                return
        
        elif building_type == "Нефтяная вышка":
            can_build = False
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y) and resource['type'] == "Нефть":
                    can_build = True
                    break
            if not can_build:
                return
        
        elif building_type == "Каменная шахта":
            can_build = False
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y) and resource['type'] == "Камень":
                    can_build = True
                    break
            if not can_build:
                return
        
        elif building_type == "Медная шахта":
            can_build = False
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y) and resource['type'] == "Медь":
                    can_build = True
                    break
            if not can_build:
                return
        
        else:
            for resource in self.resources:
                if resource['pos'] == (grid_x, grid_y):
                    return

        if self.can_afford_building(building_type):
            self.buildings.append({
                'image': self.building_images[building_type],
                'pos': (grid_x, grid_y),
                'type': building_type
            })
            self.deduct_building_cost(building_type)
            self.selected_building = None

    def try_create_soldier(self, mouse_pos):
        """Попытка создать солдата на военном заводе"""
        grid_x = (mouse_pos[0] // self.cell_size) * self.cell_size
        grid_y = (mouse_pos[1] // self.cell_size) * self.cell_size

        for building in self.buildings:
            if building['pos'] == (grid_x, grid_y) and building['type'] == "Военный завод":
                if self.can_afford_unit("Солдат"):
                    soldier_pos = (grid_x + self.cell_size + 10, grid_y)
                    self.military_units.append({
                        'image': self.soldat_image,
                        'pos': soldier_pos,
                        'type': 'Солдат'
                    })
                    self.deduct_unit_cost("Солдат")
                break

    def end_turn(self):
        """Пропуск хода - производство ресурсов и потребление"""
        for building in self.buildings:
            building_type = building['type']
            
            if building_type in self.building_upkeep:
                can_afford_upkeep = True
                
                for resource, amount in self.building_upkeep[building_type].items():
                    if self.player_resources.get(resource, 0) < amount:
                        can_afford_upkeep = False
                        break
                
                if can_afford_upkeep:
                    for resource, amount in self.building_upkeep[building_type].items():
                        self.player_resources[resource] -= amount
                        print(f"Завод потребил {amount} {resource}")
                else:
                    print(f"Не хватает ресурсов для содержания {building_type}!")

        for building in self.buildings:
            building_type = building['type']
            
            if building_type in self.building_production:
                for resource, amount in self.building_production[building_type].items():
                    self.player_resources[resource] += amount
                    print(f"{building_type} произвел {amount} {resource}")

        self.turn_count += 1

    def draw_main_menu(self):
        """Отрисовка главного меню"""
        self.screen.blit(self.bg_image, (0, 0))

        play_rect = self.play_button.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(self.play_button, play_rect)

        self.screen.blit(self.settings_image, self.settings_button_rect.topleft)

        title_font = pygame.font.Font(None, self.font_size_title)
        title = title_font.render("vektor ", True, WHITE)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

    def draw_game_screen(self):
        """Отрисовка игрового экрана"""
        self.screen.fill(GREEN)
        
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, self.cell_size):
            pygame.draw.line(self.screen, GRAY, (0, y), (self.screen_width, y), 1)

        self.screen.blit(self.corner_image, self.corner_pos)
        self.screen.blit(self.corner1_image, self.corner1_pos)

        for resource in self.resources:
            self.screen.blit(resource['image'], resource['pos'])

        for building in self.buildings:
            self.screen.blit(building['image'], building['pos'])

        for unit in self.military_units:
            self.screen.blit(unit['image'], unit['pos'])

        self.screen.blit(self.mol_image, self.mol_button_rect.topleft)

        pygame.draw.rect(self.screen, LIGHT_BLUE, self.end_turn_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.end_turn_button_rect, 2)
        font = pygame.font.Font(None, self.font_size_medium)
        text = font.render("Пропуск хода", True, WHITE)
        text_rect = text.get_rect(center=self.end_turn_button_rect.center)
        self.screen.blit(text, text_rect)

        turn_font = pygame.font.Font(None, self.font_size_large)
        turn_text = turn_font.render(f"Ход: {self.turn_count}", True, WHITE)
        self.screen.blit(turn_text, (20, 20))

        self.draw_resource_panel()

        if self.selected_building:
            mouse_pos = pygame.mouse.get_pos()
            grid_x = (mouse_pos[0] // self.cell_size) * self.cell_size
            grid_y = (mouse_pos[1] // self.cell_size) * self.cell_size

            building_image = self.building_images[self.selected_building].copy()
            building_image.set_alpha(128)
            self.screen.blit(building_image, (grid_x, grid_y))

    def draw_resource_panel(self):
        """Отрисовка панели ресурсов справа"""
        panel_width = max(200, self.screen_width // 8)
        panel_height = max(300, self.screen_height // 2)
        panel_rect = pygame.Rect(self.screen_width - panel_width - 20, 60, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 2)

        font = pygame.font.Font(None, self.font_size_large)
        title = font.render("Ресурсы", True, WHITE)
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 10))

        resources_list = [
            (self.gelezo_image, "Железо"),
            (self.medi_image, "Медь"),
            (self.nefti_image, "Нефть"),
            (self.stone_image, "Камень"),
            (self.forest_image, "Дерево"),
            (self.components_image, "компоненты")
        ]

        y_offset = panel_rect.y + 50
        icon_size = max(30, self.cell_size - 10)
        for image, resource_name in resources_list:
            icon_rect = pygame.Rect(panel_rect.x + 10, y_offset, icon_size, icon_size)
            self.screen.blit(pygame.transform.scale(image, (icon_size, icon_size)), icon_rect)

            text = font.render(f"{resource_name}: {self.player_resources.get(resource_name, 0)}", True, WHITE)
            self.screen.blit(text, (panel_rect.x + icon_size + 20, y_offset + icon_size // 3))

            y_offset += icon_size + 15

    def draw_mol_menu(self):
        """Отрисовка меню MOL"""
        self.draw_game_screen()

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, DARK_BLUE, self.mol_menu_rect)
        pygame.draw.rect(self.screen, WHITE, self.mol_menu_rect, 2)

        font = pygame.font.Font(None, self.font_size_title)
        title = font.render("Меню построек", True, WHITE)
        self.screen.blit(title, (self.mol_menu_rect.centerx - title.get_width() // 2,
                                 self.mol_menu_rect.y + 20))

        button_size = 80
        button_margin = 20
        start_x = self.mol_menu_rect.x + 50
        start_y = self.mol_menu_rect.y + 80
        
        buttons = [
            {"image": self.zavod_image, "pos": (start_x, start_y), "text": "Завод", "type": "Завод"},
            {"image": self.ibrari_image, "pos": (start_x + button_size + button_margin, start_y), "text": "Лаборатория", "type": "Лаборатория"},
            {"image": self.fika_image, "pos": (start_x + (button_size + button_margin) * 2, start_y), "text": "Нефтяная вышка", "type": "Нефтяная вышка"},
            {"image": self.losplka_image, "pos": (start_x + (button_size + button_margin) * 3, start_y), "text": "Лесопилка", "type": "Лесопилка"},
            {"image": self.voenka_image, "pos": (start_x, start_y + button_size + 80), "text": "Военный завод", "type": "Военный завод"},
            {"image": self.rydnik_glezo_image, "pos": (start_x + button_size + button_margin, start_y + button_size + 80), "text": "Железная шахта", "type": "Железная шахта"},
            {"image": self.rydnik_kamini_image, "pos": (start_x + (button_size + button_margin) * 2, start_y + button_size + 80), "text": "Каменная шахта", "type": "Каменная шахта"},
            {"image": self.rydnik_midi_image, "pos": (start_x + (button_size + button_margin) * 3, start_y + button_size + 80), "text": "Медная шахта", "type": "Медная шахта"}
        ]

        for button in buttons:
            can_afford = self.can_afford_building(button["type"])
            border_color = (0, 255, 0) if can_afford else (255, 0, 0)
            
            mouse_pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect(button["pos"][0] - 5, button["pos"][1] - 5, button_size + 10, button_size + 10)
            
            if button_rect.collidepoint(mouse_pos):
                hover_rect = pygame.Rect(button["pos"][0] - 8, button["pos"][1] - 8, button_size + 16, button_size + 16)
                pygame.draw.rect(self.screen, YELLOW, hover_rect, 4)
            
            pygame.draw.rect(self.screen, border_color, button_rect, 2)
            self.screen.blit(button["image"], button["pos"])

            text_font = pygame.font.Font(None, self.font_size_small)
            text = text_font.render(button["text"], True, WHITE)
            text_x = button["pos"][0] + button_size // 2 - text.get_width() // 2
            text_y = button["pos"][1] + button_size + 10
            self.screen.blit(text, (text_x, text_y))

            cost_font = pygame.font.Font(None, self.font_size_small - 2)
            if button["type"] in self.building_costs:
                cost_lines = []
                for res, amount in self.building_costs[button["type"]].items():
                    cost_lines.append(f"{res}: {amount}")
                
                for i, cost_line in enumerate(cost_lines):
                    cost_surface = cost_font.render(cost_line, True, YELLOW if can_afford else RED)
                    cost_x = button["pos"][0] + button_size // 2 - cost_surface.get_width() // 2
                    cost_y = button["pos"][1] + button_size + 25 + i * 12
                    self.screen.blit(cost_surface, (cost_x, cost_y))

        if self.hovered_building:
            info_rect = pygame.Rect(self.mol_menu_rect.x + 50, self.mol_menu_rect.bottom - 150, 
                                  self.mol_menu_rect.width - 100, 120)
            pygame.draw.rect(self.screen, DARK_BLUE, info_rect)
            pygame.draw.rect(self.screen, WHITE, info_rect, 2)
            
            info_font = pygame.font.Font(None, self.font_size_medium)
            info_text = info_font.render(f"Информация о: {self.hovered_building}", True, YELLOW)
            self.screen.blit(info_text, (info_rect.x + 10, info_rect.y + 10))
            
            production_info = self.get_building_production(self.hovered_building)
            prod_text = info_font.render(f"Производство: {production_info}", True, WHITE)
            self.screen.blit(prod_text, (info_rect.x + 10, info_rect.y + 40))
            
            placement_info = self.get_building_placement_info(self.hovered_building)
            place_text = info_font.render(f"Размещение: {placement_info}", True, WHITE)
            self.screen.blit(place_text, (info_rect.x + 10, info_rect.y + 70))

        close_rect = pygame.Rect(self.mol_menu_rect.right - 30, self.mol_menu_rect.y + 10, 20, 20)
        pygame.draw.rect(self.screen, RED, close_rect)
        pygame.draw.rect(self.screen, WHITE, close_rect, 2)
        close_font = pygame.font.Font(None, self.font_size_medium)
        close_text = close_font.render("X", True, WHITE)
        self.screen.blit(close_text, (close_rect.x + 6, close_rect.y + 2))

        hint_font = pygame.font.Font(None, self.font_size_medium)
        hint_text = "Зеленый = можно построить, Красный = не хватает ресурсов"
        hint_surface = hint_font.render(hint_text, True, YELLOW)
        self.screen.blit(hint_surface, (self.mol_menu_rect.centerx - hint_surface.get_width() // 2, 
                                       self.mol_menu_rect.bottom - 30))

    def get_building_placement_info(self, building_type):
        """Возвращает информацию о требованиях к размещению здания"""
        placement = {
            "Лесопилка": "Только на лесе",
            "Завод": "На пустой клетке", 
            "Нефтяная вышка": "Только на нефти",
            "Лаборатория": "На пустой клетке",
            "Железная шахта": "Только на железе",
            "Каменная шахта": "Только на камне",
            "Медная шахта": "Только на меди",
            "Военный завод": "На пустой клетке"
        }
        return placement.get(building_type, "Неизвестно")

    def draw_settings_menu(self):
        """Отрисовка меню настроек"""
        self.draw_main_menu()

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, DARK_BLUE, self.mol_menu_rect)
        pygame.draw.rect(self.screen, WHITE, self.mol_menu_rect, 2)

        font = pygame.font.Font(None, self.font_size_title)
        title = font.render("Настройки", True, WHITE)
        self.screen.blit(title, (self.mol_menu_rect.centerx - title.get_width() // 2,
                                 self.mol_menu_rect.y + 20))

        sub_font = pygame.font.Font(None, self.font_size_large)
        sub_title = sub_font.render("Выберите разрешение экрана:", True, WHITE)
        self.screen.blit(sub_title, (self.mol_menu_rect.centerx - sub_title.get_width() // 2,
                                     self.mol_menu_rect.y + 40))

        for i, resolution in enumerate(RESOLUTIONS):
            button_rect = pygame.Rect(
                self.mol_menu_rect.x + 50,
                self.mol_menu_rect.y + 60 + i * 60,
                self.mol_menu_rect.width - 100,
                50
            )

            if i == self.current_resolution:
                pygame.draw.rect(self.screen, ORANGE, button_rect)
            else:
                pygame.draw.rect(self.screen, LIGHT_BLUE, button_rect)

            pygame.draw.rect(self.screen, WHITE, button_rect, 2)

            if i == 5:
                res_text = f"Авто ({self.screen_info.current_w}x{self.screen_info.current_h})"
            else:
                res_text = f"{resolution[0]} x {resolution[1]}"
            
            text_surface = font.render(res_text, True, WHITE)
            self.screen.blit(text_surface, (button_rect.centerx - text_surface.get_width() // 2,
                                           button_rect.centery - text_surface.get_height() // 2))

        close_rect = pygame.Rect(self.mol_menu_rect.right - 30, self.mol_menu_rect.y + 10, 20, 20)
        pygame.draw.rect(self.screen, RED, close_rect)
        pygame.draw.rect(self.screen, WHITE, close_rect, 2)
        close_font = pygame.font.Font(None, self.font_size_medium)
        close_text = close_font.render("X", True, WHITE)
        self.screen.blit(close_text, (close_rect.x + 6, close_rect.y + 2))

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            if self.state == MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GAME_SCREEN:
                self.draw_game_screen()
            elif self.state == MOL_MENU:
                self.draw_mol_menu()
            elif self.state == SETTINGS_MENU:
                self.draw_settings_menu()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def create_exe_and_run():
    """Функция для создания EXE файла и его автоматического запуска"""
    try:
        print("=" * 50)
        print("СОЗДАНИЕ EXE ФАЙЛА И АВТОМАТИЧЕСКИЙ ЗАПУСК")
        print("=" * 50)
        
        # Проверяем наличие PyInstaller
        if importlib.util.find_spec("PyInstaller") is None:
            print("PyInstaller не установлен.")
            print("Установите его командой: pip install pyinstaller")
            print("Затем запустите создание EXE снова.")
            return False
        
        print("Проверка окружения...")
        if not verify_environment():
            print("Ошибка: Небезопасное окружение!")
            return False
            
        print("Создание EXE файла...")
        
        # Создаем папку для дистрибутива если не существует
        dist_dir = "./game_exe"
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        
        # Команда PyInstaller
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "vektor_game",
            "--clean",
            "--distpath", dist_dir,
            "game.py"
        ]
        
        # Добавляем папку с изображениями если существует
        if os.path.exists("images"):
            cmd.extend(["--add-data", f"images{os.pathsep}images"])
        
        print("Запуск PyInstaller...")
        result = subprocess.run(cmd, check=True, timeout=300, 
                              capture_output=True, text=True)
        
        exe_path = os.path.join(dist_dir, "vektor_game.exe")
        if os.path.exists(exe_path):
            print("Успешно! EXE файл создан!")
            print(f"Файл: {exe_path}")
            
            # Автоматический запуск EXE файла
            print("Запускаем созданный EXE файл...")
            try:
                subprocess.Popen([exe_path])
                print("EXE файл успешно запущен!")
                return True
            except Exception as e:
                print(f"Ошибка при запуске EXE: {e}")
                print(f"Вы можете запустить EXE вручную из папки: {dist_dir}")
                return False
        else:
            print("Ошибка: EXE файл не был создан!")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка PyInstaller: {e}")
        if e.stdout:
            print(f"Вывод: {e.stdout}")
        if e.stderr:
            print(f"Ошибки: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("Ошибка: Создание EXE заняло слишком много времени!")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False

def main():
    """Главная функция для запуска игры"""
    print("=" * 50)
    print("VEKTOR - СТРАТЕГИЧЕСКАЯ ИГРА")
    print("=" * 50)
    
    # Проверка безопасности
    if not verify_environment():
        print("Предупреждение: Проверка окружения не пройдена!")
      
    # Если мы уже в EXE, просто запускаем игру
    if getattr(sys, 'frozen', False):
        game = Game()
        game.run()
    else:
        # Запуск из Python - предлагаем выбор
        print("Выберите действие:")
        print("1 - Запустить игру напрямую")
        print("2 - Создать EXE файл и запустить его")
        print("=" * 50)
        
        try:
            choice = input("Ваш выбор (1 или 2): ").strip()
            
            if choice == "2":
                print("Запуск создания EXE файла...")
                success = create_exe_and_run()
                if success:
                    print("EXE успешно создан и запущен!")
                    sys.exit(0)
                else:
                    print("Не удалось создать EXE файл.")
                    # Предлагаем запустить игру напрямую если EXE не создался
                    retry = input("Хотите запустить игру напрямую? (y/n): ").strip().lower()
                    if retry == 'y':
                        game = Game()
                        game.run()
            else:
                print("Запуск игры напрямую...")
                game = Game()
                game.run()
                
        except KeyboardInterrupt:
            print("\nВыход...")
        except Exception as e:
            print(f"Ошибка: {e}")
            input("Нажмите Enter для выхода...")

if __name__  == "__main__":
     main()