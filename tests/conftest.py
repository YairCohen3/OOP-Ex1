from pathlib import Path
import linecache
import os
import sys
import tkinter as tk
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FIXTURES_DIR = Path(__file__).resolve().parent / "csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def csv_dir():
    return CSV_FIXTURES_DIR


@pytest.fixture
def data_dir(project_root):
    return project_root / "data"


def _run_popup(title: str, width: int, height: int, build_ui):
    """יוצר חלון קופץ שסוגר את כל תהליך הרצת הטסטים מיד עם סגירתו."""
    try:
        root = tk.Tk()
        root.title(title)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{width}x{height}+{(sw - width) // 2}+{(sh - height) // 2}")
        root.configure(bg="#181825")
        root.attributes("-topmost", True)

        def close_and_exit(event=None):
            try:
                root.destroy()
            except Exception:
                pass
            # עצירה מוחלטת של תהליך פייתון וכל טסטים שרצים ברקע
            os._exit(0)

        root.protocol("WM_DELETE_WINDOW", close_and_exit)
        root.bind_all("<Escape>", close_and_exit)
        root.bind_all("<Return>", close_and_exit)

        build_ui(root, close_and_exit)

        root.lift()
        root.focus_force()
        root.mainloop()
    except Exception as err:
        print(f"\n[Popup Error]: {err}", file=sys.stderr)


def show_error_popup(test_name: str, file_path: str, line_no: int, message: str):
    """חלון ERROR שנעצר ומפסיק את הריצה ברגע שסוגרים אותו."""
    def build(root, close_fn):
        top_bar = tk.Frame(root, bg="#181825", padx=20, pady=12)
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text=" ERROR ",
            font=("Consolas", 13, "bold"),
            fg="#11111b",
            bg="#f38ba8",
        ).pack(side=tk.LEFT)

        short_file = Path(file_path).name
        tk.Label(
            top_bar,
            text=f"  {test_name}  ({short_file}:{line_no})",
            font=("Consolas", 12, "bold"),
            fg="#cdd6f4",
            bg="#181825",
        ).pack(side=tk.LEFT)

        code_box = tk.Text(
            root,
            height=7,
            font=("Consolas", 11),
            bg="#11111b",
            fg="#6c7086",
            bd=0,
            padx=14,
            pady=10,
            highlightthickness=1,
            highlightbackground="#313244",
        )
        code_box.pack(fill=tk.X, padx=20, pady=4)
        code_box.tag_config("context", foreground="#7f849c")
        code_box.tag_config(
            "failed_line",
            background="#45212c",
            foreground="#f38ba8",
            font=("Consolas", 11, "bold"),
        )

        resolved_path = Path(file_path)
        if not resolved_path.is_absolute():
            resolved_path = PROJECT_ROOT / resolved_path

        linecache.checkcache(str(resolved_path))
        for curr_no in range(max(1, line_no - 2), line_no + 3):
            code_line = linecache.getline(str(resolved_path), curr_no).rstrip("\r\n")
            if not code_line and curr_no != line_no:
                continue
            if curr_no == line_no:
                prefix = f"> {curr_no:3d} | "
                code_box.insert(tk.END, f"{prefix}{code_line}\n", "failed_line")
            else:
                prefix = f"  {curr_no:3d} | "
                code_box.insert(tk.END, f"{prefix}{code_line}\n", "context")

        code_box.configure(state="disabled")

        clean_msg = message.splitlines()[0] if message else "Test assertion failed"
        tk.Label(
            root,
            text=clean_msg,
            font=("Consolas", 10, "bold"),
            fg="#fab387",
            bg="#181825",
            anchor="w",
            padx=20,
            pady=6,
        ).pack(fill=tk.X)

        btn = tk.Button(
            root,
            text="Close & Stop (Enter / Esc)",
            font=("Consolas", 10, "bold"),
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#ffffff",
            bd=0,
            padx=18,
            pady=6,
            command=close_fn,
        )
        btn.pack(pady=8)
        btn.focus_set()

    _run_popup("ERROR", 640, 340, build)


def show_success_popup(total_tests: int):
    """חלון ירוק כאשר כל הטסטים עברו."""
    def build(root, close_fn):
        tk.Label(
            root,
            text=" ALL TESTS PASSED ",
            font=("Consolas", 13, "bold"),
            fg="#11111b",
            bg="#a6e3a1",
        ).pack(pady=(22, 10))

        tk.Label(
            root,
            text=f"{total_tests} / {total_tests} tests succeeded",
            font=("Consolas", 11),
            fg="#cdd6f4",
            bg="#181825",
        ).pack(pady=4)

        btn = tk.Button(
            root,
            text="OK (Enter / Esc)",
            font=("Consolas", 10, "bold"),
            bg="#313244",
            fg="#cdd6f4",
            bd=0,
            padx=18,
            pady=5,
            command=close_fn,
        )
        btn.pack(pady=12)
        btn.focus_set()

    _run_popup("PASSED", 400, 170, build)


def pytest_exception_interact(node, call, report):
    if report.failed and hasattr(report.longrepr, "reprcrash"):
        crash = report.longrepr.reprcrash
        show_error_popup(
            test_name=node.name,
            file_path=crash.path,
            line_no=crash.lineno,
            message=crash.message,
        )


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0 and session.testscollected > 0:
        show_success_popup(session.testscollected)