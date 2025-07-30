# teacher_app/trigger_student.py

from multiprocessing import Process
import multiprocessing
from .run import start_the_server

def launch_student_server():
    p = Process(target=start_the_server)
    p.start()
    p.join()
    multiprocessing.freeze_support()  # For Windows safety

    print("Student server started!")
    return p  # You can use this process object to stop it later if needed
