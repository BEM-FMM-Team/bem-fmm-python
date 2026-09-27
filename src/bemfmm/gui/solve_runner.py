import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, Signal

STAGES = {
    "imprint": "Imprinting electrodes",
    "neighbors": "Neighbor integrals",
    "rhs": "Coil fields",
    "solve": "Solving",
    "fields": "Computing fields",
    "slices": "E-field slices",
}


class SolveRunner(QObject):
    """
    Runs `bemfmm <args>` in a child process so the window stays responsive
    and a crash in the solver cannot take the gui down with it. job is a name
    for what is running, "solve" or "slices"
    """

    progress = Signal(str, int, int)
    output = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.run_dir = None
        self.job = None
        self.buffer = ""
        self.cancelled = False

    @property
    def running(self):
        return self.process is not None

    def start(self, args, run_dir, job="solve"):
        self.run_dir = Path(run_dir)
        self.job = job
        self.buffer = ""
        self.cancelled = False

        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        env.insert("MPLBACKEND", "Agg")

        self.process = QProcess(self)
        self.process.setProcessEnvironment(env)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.setWorkingDirectory(str(self.run_dir))
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_error)

        args = ["-m", "bemfmm"] + [str(arg) for arg in args] + ["--progress"]
        self.output.emit(f"$ {Path(sys.executable).name} {' '.join(args)}")
        self.process.start(sys.executable, args)

    def cancel(self):
        if self.process is not None:
            self.cancelled = True
            self.process.kill()

    def read_output(self):
        self.buffer += bytes(self.process.readAllStandardOutput()).decode(
            errors="replace"
        )
        *lines, self.buffer = self.buffer.split("\n")
        for line in lines:
            line = line.rstrip("\r")
            if line.startswith("@progress "):
                _, stage, done, total = line.split()
                self.progress.emit(stage, int(done), int(total))
            else:
                self.output.emit(line)

    def on_error(self, error):
        if error == QProcess.FailedToStart:
            self.output.emit("The solver could not be started")
            self.process = None
            self.finished.emit(False, str(self.run_dir))

    def on_finished(self, code, status):
        if self.buffer:
            self.output.emit(self.buffer)
            self.buffer = ""
        ok = status == QProcess.NormalExit and code == 0 and not self.cancelled
        self.process = None
        self.finished.emit(ok, str(self.run_dir))
