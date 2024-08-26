import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from typing import Optional

from src.calculate import Calculate, AbortionException


class App:
    """
    This module includes a class `App`, which represents an application for estimating costs. It provides a user interface for selecting a target folder and starting or stopping the cost calculation process.
    """

    def __init__(self, main_root: tk.Tk) -> None:
        """
        Class for the estimator tool application.

        This class represents the main application for the estimator tool. It contains methods to initialize the application window, handle folder selection, and start/stop the estimation process.

        Attributes:
            root (tk.Tk): The root window of the application.
            calculate (Optional[Calculate]): The calculate object used for estimation.
            thread (Optional[threading.Thread]): The thread used for the estimation process.
            browse_button (tk.Button): The button to browse and select a target folder.
            selected_folder_label (tk.Label): The label to display the selected folder.
            start_button (tk.Button): The button to start/stop the estimation process.
            progress_label (tk.Label): The label to display the progress of the estimation process.
        """
        self.root = main_root
        self.root.title("견적 산출기")
        self.root.minsize(300, 200)

        # 상태 변수
        self.calculate: Optional[Calculate] = None
        self.thread: Optional[threading.Thread] = None

        # 대상 폴더
        self.browse_button = tk.Button(root, text="대상 폴더 지정", command=self.browse_folder)
        self.browse_button.grid(row=0, column=0)
        self.selected_folder_label = tk.Label(root, text="선택 폴더 없음")
        self.selected_folder_label.grid(row=0, column=1)

        # 시작/중지 토글
        self.start_button = tk.Button(
            root, text="견적 산출하기", state=tk.DISABLED, command=self.toggle_process)
        self.start_button.grid(row=1, column=0)
        self.progress_label = tk.Label(root, text="")
        self.progress_label.grid(row=1, column=1)

    def browse_folder(self) -> None:
        """
        Method to browse and select a folder.

        This method prompts a file dialog to allow the user to browse and select a folder.
        If a folder is selected, the method updates the selected folder label with the chosen folder path.
        It also enables the start button and creates an instance of the `Calculate` class with the selected folder path.
        """
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder_label.config(text=folder_selected)
            self.start_button.config(state=tk.NORMAL)
            self.calculate = Calculate(folder_selected)
        self.root.focus_force()
        self.root.lift()

    def toggle_process(self) -> None:
        """
        Toggles the process.

        If the process is already running (i.e., the thread is alive), it stops the process by calling the `stop` method of the `calculate` object.

        If the process is not running, it starts the process by disabling the `browse_button`, changing the text of the `start_button` to "중지", and updating the text of the `progress_label` to "진행 중...".

        The processing is done in a separate thread using the `run_process` method.
        """
        if self.thread and self.thread.is_alive():
            # 이미 진행 중일 때 중지
            assert self.calculate
            self.calculate.stop()
        else:
            # 산출 시작
            self.browse_button.config(state=tk.DISABLED)
            self.start_button.config(text="중지")
            self.progress_label.config(text="진행 중...")

            # Run the processing in a separate thread
            self.thread = threading.Thread(target=self.run_process)
            self.thread.start()

    def run_process(self) -> None:
        """
        Runs the process and updates the UI with the progress status.

        This method is responsible for running the process and updating the progress status on the UI. It uses the `calculate` attribute of the current object to run the process.
        """
        assert self.calculate
        status_message: str = ""
        try:
            for status in self.calculate.run():
                status_message = status
                if not self.thread:
                    break
                self.root.after(0, lambda: self.progress_label.config(text=status))
            # Once the process is complete, update the UI (in the main thread)
            self.root.after(0, self.on_process_complete, status_message)
        except AbortionException:
            self.finish_process()

    def finish_process(self) -> None:
        """
        Finish the process and update the GUI elements.

        Note:
            This function is used to finish the process and update the state of GUI elements. It sets the state of the
            "browse_button" to NORMAL, changes the text of "start_button" to "견적 산출하기", and sets the text of
            "progress_label" to an empty string.
        """
        self.browse_button.config(state=tk.NORMAL)
        self.start_button.config(text="견적 산출하기")
        self.progress_label.config(text="")

    def on_process_complete(self, status_message: str) -> None:
        """
        This method is called when a process is complete. It finishes the process and displays a modal dialog box with the given status message.
        """
        self.finish_process()
        # Show a modal dialog when the process is finished
        messagebox.showinfo("완료", status_message)


root = tk.Tk()
app = App(root)
root.mainloop()
