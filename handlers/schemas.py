from abc import ABC, abstractmethod
from netschoolapi.schemas import Diary
from datetime import date
from typing import Any



class MySchema:
    def __init__(self, obj: Any):
        self._source = obj

    def get_source(self) -> Any:
        return self._source



class MyDiary(MySchema):
    def __init__(self, source: Diary):
        super().__init__(source)
        
    
    def get_dates(self) -> tuple[date, date]:
        return self._source.start, self._source.end
    
    
    