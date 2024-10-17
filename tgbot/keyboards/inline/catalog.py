from aiogram.utils.callback_data import CallbackData

subjects_clb = CallbackData("subjects_clb", "action", "type_id", "subject_id", "day_id", "time_id")

teachers_clb = CallbackData("teachers_clb", "action", "subject_id", "teacher_id")

sign_up_clb = CallbackData("sign_up_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id", "lesson")

teacher_clb = CallbackData("teacher_clb", "action", "teacher_id", "type_id", "subject_id", "day_id", "time_id")

date_clb = CallbackData("date_clb", "action", "teacher_group_id", "attendance_id")

present_clb = CallbackData("present_clb", "action", "attendance_id", "teacher_group_id")

pay_clb = CallbackData("pay_clb", "student_id", "teacher_group_id")

teachers_custom_clb = CallbackData("teachers_custom_clb", "action", "teacher_id")

groups_custom_clb = CallbackData("groups_custom_clb", "action", "teacher_id", "group_id")

admins_clb = CallbackData("admins_clb", "action")

delete_group_clb = CallbackData("delete_group_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

edit_group_clb = CallbackData("edit_group_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

edit_smth_clb = CallbackData("edit_smth_clb", "action", "teacher_group_id")

edit_teacher_clb = CallbackData("edit_teacher_clb", "action", "teacher_id", "teacher_group_id")

delete_student_clb = CallbackData("delete_student_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

get_students_clb = CallbackData("get_students_clb", "action", "teacher_group_id", "student_id")

student_custom_clb = CallbackData("student_custom_clb", "action", "student_id")

add_student_clb = CallbackData("add_student_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

student_confirm = CallbackData("student_confirm", "action", "telegram_id", "teacher_group_id")

student_lessons_confirm = CallbackData("student_lessons_confirm", "action", "student_id", "remaining_lessons", "teacher_group_id")

choose_student_clb = CallbackData("choose_student_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

debstors_clb = CallbackData("debstors_clb", "action", "type_id", "subject_id", "day_id", "time_id", "teacher_id")

marks_clb = CallbackData("marks_clb", "action", "attendance_id", "teacher_group_id", "mark")


























