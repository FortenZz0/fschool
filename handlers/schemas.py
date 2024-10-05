from abc import ABC, abstractmethod
from netschoolapi.schemas import Diary, Day, Lesson, Assignment
from datetime import date
from typing import Any

from handlers import files



class MySchema:
    def __init__(self, obj: Any):
        self._source = obj

    def get_source(self) -> Any:
        return self._source
    
    def __repr__(self):
        return self.get_source()



class MyDiary(MySchema):
    def __init__(self, source: Diary):
        super().__init__(source)
        
        self.days = [MyDay(day) for day in self._source.schedule]
        self.days.sort(key=lambda x: x.date)
        
        self.start = self._source.start
        self.end = self._source.end
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = []
        
        if self.start == self.end or len(self.days) == 1:
            res.append(templates["diary_header_one_day"].format(
                self.start
            ))
        else:
            res.append(templates["diary_header"].format(
                self.start,
                self.end
            ))
            
        for day in self.days:
            res.append(str(day))
            
        return "\n\n".join(res)
    
    
    
    
class MyDay(MySchema):
    def __init__(self, source: Day):
        super().__init__(source)

        self.WEEKDAYS = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
        ]

        self.lessons = [MyLesson(les) for les in self._source.lessons]
        
        self.date = self._source.day
        self.weekday_n = self.date.weekday()
        self.weekday = self.WEEKDAYS[self.weekday_n]
        
        self.start = self.lessons[0].start
        self.end = self.lessons[-1].end
        
        # self.length = self.end - self.start
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = [templates["day_header"].format(
            self.weekday_n + 1,
            self.weekday,
            self.date
        )]
        
        for les in self.lessons:
            res.append(str(les))
            
        return "\n".join(res)



class MyLesson(MySchema):
    def __init__(self, source: Lesson):
        super().__init__(source)
        
        self.SUBJECT_TRANSLATE = {
            "Элективный курс \"Методология решения задач по физике\"": "Физика ЭЛЕКТИВ",
            "Алгебра и начала математического анализа": "Алгебра",
            "Основы безопасности жизнедеятельности": "ОБЖ",
            "Иностранный язык (английский).": "Английский",
            "Основы безопасности и защиты Родины": "ОБЗР",
            "Иностранный язык (немецкий).": "Немецкий",
            "Вероятность и статистика": "Вер. и Стат.",
            "Индивидуальный проект": "Инд. проект",
            "Физическая культура": "Физкультура",
            "Информатика и ИКТ": "Информатика",
            "Русский язык": "Русский"
        }

        self.date = self._source.day
        self.start = self._source.start
        self.end = self._source.end
        self.room = self._source.room
        self.number = self._source.number
        
        self._subj = self._source.subject
        
        if self._subj in self.SUBJECT_TRANSLATE.keys():
            self.subject = self.SUBJECT_TRANSLATE[self._subj]
        else:
            self.subject = self._subj
        
        self.assignments = [MyAssignment(ass) for ass in self._source.assignments]
    
    
    def get_marks(self):
        marks = []
        
        for ass in self.assignments:
            if ass.mark:
                marks.append(ass.mark)
                
        return marks
    
    
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = [templates["lesson"].format(
            self.number,
            self.subject,
            self.start,
            self.end
        )]
        
        marks = self.get_marks()
        if marks:
            res.append(templates["lesson_marks"].format(
                ", ".join(list(map(str, marks))),
                str(round(sum(marks) / len(marks), 2))
            ))
        
        for ass in self.assignments:
            res.append(str(ass))
        
        return "\n".join(res)
    


class MyAssignment(MySchema):
    def __init__(self, source: Assignment):
        super().__init__(source)
        
        self.id = self._source.id
        self.comment = self._source.comment
        self.type = self._source.type
        self.content = self._source.content
        self.mark = self._source.mark
        self.is_duty = self._source.is_duty
        self.deadline = self._source.deadline
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = templates["assignment"].format(
            self.type,
            self.content
        )
        
        if self.mark:
            res += templates["assignment_mark"].format(self.mark)
            
        return res