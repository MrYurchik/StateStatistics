from dataclasses import dataclass
from typing import List

@dataclass
class BookPageContentBody:
    Title: str
    DateAndNumber: str
    OrderName: str
    OrderText: str

@dataclass
class StateStatisticsOrder:
    FolderPath: str
    FolderName: str
    FileNames: List[str]
    BookContentTitle: str
    BookContentDescription: str
    BookPageReferences: List[int]
    BookPageContentBody: BookPageContentBody

@dataclass
class RootStructure:
    StateStatisticsOrders: List[StateStatisticsOrder]

@dataclass
class SubClass:
    letter_ref: str
    name: str
    long_description: list[dict]

@dataclass
class SubGroup:
    letter_ref: str
    name: str
    long_description: list[dict]
    sub_classes: List[SubClass]

@dataclass
class SubSection:
    letter_ref: str
    name: str
    long_description: list[dict]
    sub_groups: List[SubGroup]

@dataclass
class MainSection:
    letter_ref: str
    name: str
    long_description: list[dict]
    sub_sections: List[SubSection]

@dataclass
class KvedModel:
    letter_ref: str
    name: str
    parent: str
    long_description: dict
