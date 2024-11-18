from dataclasses import dataclass, field
from typing import List, Dict
from xml.etree import ElementTree


@dataclass
class Rating:
    name: str
    description: str
    justification: str
    score: int
    tags: List[Dict[str, str]] = field(default_factory=list)
    tags_description: str = ""
    recommendation: str = ""

    def __init__(self, xml_data: str):
        """
        Конструктор принимает XML-строку, парсит её и заполняет поля класса.
        """
        # Разбираем XML-строку
        root = ElementTree.fromstring(xml_data)

        # Заполняем поля класса, извлекая данные из XML
        self.name = self._get_text(root, "name")
        self.description = self._get_text(root, "description")
        self.justification = self._get_text(root, "justification")
        self.score = int(self._get_text(root, "score"))

        # Парсим теги в JSON-совместимом формате
        tags_text = self._get_text(root, "Tags")
        if tags_text:
            # Разделяем строку тегов по точке с запятой и создаем словари
            self.tags = [{"name": tag.strip()} for tag in tags_text.split(';') if tag.strip()]

        self.tags_description = self._get_text(root, "Tags_discription")
        self.recommendation = self._get_text(root, "recommendation")

    @staticmethod
    def _get_text(root: ElementTree.Element, tag: str) -> str:
        """
        Извлекает текстовое содержимое тега, если он существует.
        Если тег отсутствует, возвращает пустую строку.
        """
        element = root.find(tag)
        return element.text.strip() if element is not None and element.text else ""

    def get_notion_properties(self, database_id: str) -> dict:
        """
        Возвращает словарь свойств в формате для Notion API
        """
        return {
            "parent": {"database_id": database_id},
            "properties": {
                "Название": {
                    "title": [
                        {
                            "text": {
                                "content": self.name
                            }
                        }
                    ]
                },
                "Описание": {
                    "rich_text": [
                        {
                            "text": {
                                "content": self.description
                            }
                        }
                    ]
                },
                "Оценка Gemini": {
                    "number": self.score
                },
                "Рекомендации": {
                    "rich_text": [
                        {
                            "text": {
                                "content": self.recommendation
                            }
                        }
                    ]
                },
                "Для каких разделов?": {
                    "multi_select": self.tags
                }
            },
            "children": [
                # Первый заголовок
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Почему нужно выбрать именно этот источник"
                                }
                            }
                        ]
                    }
                },
                # Текст обоснования
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": self.justification
                                }
                            }
                        ]
                    }
                },
                # Второй заголовок
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "В каких разделах его можно использовать"
                                }
                            }
                        ]
                    }
                },
                # Текст описания тегов
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": self.tags_description
                                }
                            }
                        ]
                    }
                }
            ]
        }