from netschoolapi.schemas import Diary

from handlers.output_handler import translate_subject



def get_marks_of_diary(diary: Diary) -> dict:
    output_marks = {}
    
    for day in diary.schedule:
        for lesson in day.lessons:
            for ass in lesson.assignments:
                if ass.mark == None:
                    continue
                
                subj = translate_subject(lesson.subject)
                
                if subj not in list(output_marks.keys()):
                    output_marks[subj] = []
                    
                output_marks[subj].append(ass.mark)
                
    return output_marks