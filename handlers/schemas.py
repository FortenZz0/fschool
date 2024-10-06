from abc import ABC, abstractmethod
from netschoolapi.schemas import Diary, Day, Lesson, Assignment
from datetime import date, time, datetime
from typing import Any, Iterable

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
        
        self.start: date = self._source.start
        self.end: date = self._source.end
        
        
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
        
        self.date: date = self._source.day
        self.weekday_n: int = self.date.weekday()
        self.weekday: str = self.WEEKDAYS[self.weekday_n]
        
        self.start: time = self.lessons[0].start
        self.end: time = self.lessons[-1].end
        
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

        self.date: date = self._source.day
        self.start: time = self._source.start
        self.end: time = self._source.end
        self.room: str = self._source.room
        self.number: int = self._source.number
        
        self._subj: str = self._source.subject
        
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
        
        self.id: int = self._source.id
        self.comment: str = self._source.comment
        self.type: str = self._source.type
        self.content: str = self._source.content
        self.mark: int = self._source.mark
        self.is_duty: bool = self._source.is_duty
        self.deadline: date = self._source.deadline
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = templates["assignment"].format(
            self.type,
            self.content
        )
        
        if self.mark:
            res += templates["assignment_mark"].format(self.mark)
            
        return res



class MyMarks(MySchema):
    def __init__(self, source: MyDiary):
        super().__init__(source)
        
        self.extend_subjects = ["Разговоры о важном"]
        
        self.marks_obj = {}
        self.marks = []
        
        self._load_marks_obj()
        self._load_marks()
        
    
    def _load_marks_obj(self):
        res = {}
        
        for day in self._source.days:
            for les in day.lessons:
                if les.subject not in list(res.keys()):
                    res[les.subject] = []
                
                for ass in les.assignments:
                    
                    if ass.mark:
                    
                        mark = MyMark({"id": ass.id,
                                "subject": les.subject,
                                "date": les.date,
                                "type": ass.type,
                                "mark": ass.mark})
                        
                        if les.subject in res.keys():
                            res[les.subject].append(mark)
                        else:
                            res[les.subject] = [mark]
                        
        
        res_2 = sorted(res.items(), key=lambda x: x[0])
        
        for i in res_2:
            subj, marks = i
            
            if subj in self.extend_subjects:
                continue
            
            self.marks_obj[subj] = []
            
            for mark in marks:
                self.marks_obj[subj].append(mark)
                    
    
    
    def _load_marks(self):
        res = []
        
        for v in self.marks_obj.values():
            v.sort(key=lambda x: x.mark, reverse=True)
            res.extend(v)
            
        res.sort(key=lambda x: x.date)
        
        self.marks = res
    
    
    def marks_by_subj(self, subj: str) -> list[int] | None:
        res = []
        
        for k, v in self.marks_obj.items():
            for mark in v:
                if k == subj:
                    res.append(mark.mark)
                
        return res
    
    
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = []
        
        if self._source.start == self._source.end:
            res.append(templates["all_marks_header_one_day"].format(
                self._source.start
            ))
        else:
            res.append(templates["all_marks_header"].format(
                self._source.start,
                self._source.end
            ))
        
        for i, item in enumerate(self.marks_obj.items()):
            subj, marks = item
            
            ms = self.marks_by_subj(subj)
            
            res.append(templates["marks_header"].format(
                i + 1,
                subj,
                round(sum(ms) / len(ms), 2) if ms else 0
            ))
            
            marks.sort(key=lambda x: x.date)
            for mark in marks:
                res.append(str(mark))
                
            res.append("")
        
            
        return "\n".join(res)
    
        

class MyMark(MySchema):
    def __init__(self, source: dict):
        super().__init__(source)
        
        self.id: int = source["id"]
        self.subject: str = source["subject"]
        self.date: date = source["date"]
        self.type: str = source["type"]
        self.mark: int = source["mark"]
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = templates["mark"].format(
            self.type,
            self.date,
            self.mark
        )
        
        return res
    
        
    def __repr__(self):
        return str(self.get_source())