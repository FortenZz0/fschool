from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Diary, Day, Lesson, Assignment
from aiogram.utils import formatting
from datetime import date, time, datetime
from typing import Any, Iterable
from io import BytesIO

from handlers import files



class MySchema:
    def __init__(self, obj: Any):
        self._source = obj

    def get_source(self) -> Any:
        return self._source
    
    def __repr__(self):
        return str(self.get_source())



class MyDiary(MySchema):
    __slots__ = [
        "_source", "days", "period_title",
        "start", "end"
    ]
    
    def __init__(self, source: Diary, period_title: str):
        super().__init__(source)
        
        self.days = [MyDay(day) for day in self._source.schedule]
        self.days.sort(key=lambda x: x.date)
        
        self.period_title = period_title
        
        self.start: date = self._source.start
        self.end: date = self._source.end
    
    
    async def get_attachments(self, ns: NetSchoolAPI):
        res = []
        
        temp = {}
        
        for day in self.days:
            for less in day.lessons:
                for ass in less.assignments:
                    attachments = await ns.attachments(ass.id)
                    for att in attachments:
                        n = temp.get(less.subject, 0)
                        temp.update({less.subject: n+1})
                        
                        res.append(MyAttachment(
                            att,
                            less.subject.replace(" ", "-"),
                            str(less.date),
                            n
                        ))
        
        return res
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        res = []
        
        if self.start == self.end or len(self.days) == 1:
            res.append(templates["diary_header_one_day"].format(
                self.start,
                self.period_title
            ))
        else:
            res.append(templates["diary_header"].format(
                self.start,
                self.end,
                self.period_title
            ))
            
        for day in self.days:
            res.append(str(day))
            
        return "\n\n".join(res)
    
    
    
    
class MyDay(MySchema):
    __slots__ = [
        "_source", "lessons", "date",
        "weekday_n", "weekday", "start",
        "end"
    ]
    
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
        
        self.date: _Date = self._source.day
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
    __slots__ = [
        "_source", "date", "start",
        "end", "room", "number",
        "_subj", "assignments"
    ]
    
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

        self.date: _Date = self._source.day
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
        
        marks = self.get_marks()
        if marks:
            res = [templates["lesson_with_marks"].format(
                self.number,
                self.subject,
                ":".join(str(self.start).split(":")[:2]),
                ":".join(str(self.end).split(":")[:2]),
                ", ".join(list(map(str, marks))),
                str(round(sum(marks) / len(marks), 2))
            )]
        else:
            res = [templates["lesson"].format(
                self.number,
                self.subject,
                ":".join(str(self.start).split(":")[:2]),
                ":".join(str(self.end).split(":")[:2]),
            )]
        
        for ass in self.assignments:
            res.append(str(ass))
        
        return "\n".join(res)
    


class MyAssignment(MySchema):
    __slots__ = [
        "_source", "id", "comment",
        "type", "content", "mark",
        "is_duty", "deadline"
    ]

    def __init__(self, source: Assignment):
        super().__init__(source)
        
        self.id: int = self._source.id
        self.comment: str = self._source.comment
        self.type: str = self._source.type
        self.content: str = self._source.content
        self.mark: int = self._source.mark
        self.is_duty: bool = self._source.is_duty
        self.deadline: _Date = self._source.deadline
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        if self.mark:
            res = templates["assignment_with_mark"].format(
                self.type,
                self.mark,
                self.content
            )
        else:
            res = templates["assignment"].format(
                self.type,
                self.content
            )
            
        return res



class MyMarks(MySchema):
    __slots__ = [
        "_source", "period_title", "start",
        "end", "marks_obj", "marks"
    ]
    
    def __init__(self, source: MyDiary, period_title):
        super().__init__(source)
        
        self.period_title = period_title
        
        self.extend_subjects = ["Разговоры о важном"]
        
        self.start: _Date = source.start
        self.end: _Date = source.end
        
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

        if self._source.start == self._source.end:
            res_2 = res.items()
        else:
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
                self._source.start,
                self.period_title
            ))
        else:
            res.append(templates["all_marks_header"].format(
                self._source.start,
                self._source.end,
                self.period_title + (" неделю" if (self.end - self.start).days == 5 else "")
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
        
                
        if l := len(self.marks): # l != 0
            s = sum(list(map(lambda x: x.mark, self.marks))) / l
            res.append(f"\n--------------------\nОбщий средний балл: <b><i>~{s:.2}</i></b>")
            
        return "\n".join(res)
    
        

class MyMark(MySchema):
    __slots__ = [
        "_source", "id", "subject",
        "date", "start", "end"
    ]
    
    def __init__(self, source: dict):
        super().__init__(source)
        
        self.format_types = {
            "Контрольное упражнение": "К/Упр",
            "Самостоятельная работа": "С/Р",
            "Практическая работа": "Пр/Р",
            "Контрольная работа": "К/Р",
            "Домашнее задание": "Д/З",
            "Ответ на уроке": "Ответ",
        }
        
        self.id: int = source["id"]
        self.subject: str = source["subject"]
        self.date: _Date = source["date"]
        self.type: str = source["type"]
        self.mark: int = source["mark"]
        
        
    def __str__(self):
        templates = files.get_settings()["schemas"]
        
        ftype = self.type[:]
        if ftype in self.format_types.keys():
            ftype = self.format_types[ftype]
        
        res = templates["mark"].format(
            ftype,
            self.date,
            self.mark
        )
        
        return res
    
        
    def __repr__(self):
        return str(self.get_source())
    
    

class MyAttachment(MySchema):
    __slots__ = [
        "_source", "id",
        "name", "desc"
    ]
    
    def __init__(self, obj,
                 lesson_name: str | None = None,
                 lesson_date: str | None = None,
                 attachment_n: int | None = None):
        super().__init__(obj)
        
        self.id: str = self._source.id
        self.name: str = self._source.name
        self.desc: str = self._source.description
        
        self._lesson_name = lesson_name
        self._lesson_date = lesson_date
        self._attachment_n = attachment_n
    

    @property
    def fname(self, lesson_name: str | None = None,
                    lesson_date: str | None = None,
                    attachment_n: int | None = None) -> str:
        
        assert self._lesson_name is None or lesson_name is None
        assert self._lesson_date is None or lesson_date is None
        assert self._attachment_n is None or attachment_n is None
        
        name = self._lesson_name if lesson_name is None else lesson_name
        date = self._lesson_date if lesson_date is None else lesson_date
        n = self._attachment_n if attachment_n is None else attachment_n
        
        template = files.get_settings()["txt"]["attachment_name"]
        
        return template.format(
            name,
            date,
            n,
            self.name.split(".")[-1]
        )
        
        
    async def download(self, ns: NetSchoolAPI) -> BytesIO:
        buffer = BytesIO()
        await ns.download_attachment(self.id, buffer)
        
        return buffer