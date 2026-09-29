import numpy as np
from matplotlib import rc_context
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bemfmm.plot.slice import draw_efield_slice

from .viewport import electrode_color


class PlotWindow(QWidget):
    """
    Separate window for a popped out plot, closing it docks the plot again
    """

    def __init__(self, panel):
        super().__init__(None, Qt.Window)
        self.panel = panel
        self.setWindowTitle(f"{panel.title} - BEM-FMM")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(panel)
        self.resize(960, 720)

    def closeEvent(self, event):
        self.panel.dock()
        event.accept()


class PlotPanel(QWidget):
    """
    Matplotlib figure with its toolbar (zoom, pan, save) inside a container of
    the main window. It can be popped out into its own window and docked back.
    draw(figure) fills the figure, it is called again on every refresh
    """

    def __init__(self, container, title, draw):
        super().__init__()
        self.title = title
        self.draw = draw
        self.rc = {}
        self.popup = None

        self.figure = Figure(layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.pop_button = QToolButton()
        self.pop_button.setText("Pop out")
        self.pop_button.setToolTip("Show the plot in its own window")
        self.pop_button.clicked.connect(self.toggle_window)

        self.header = QHBoxLayout()
        self.header.setContentsMargins(0, 0, 0, 0)
        self.header.addWidget(self.toolbar)
        self.header.addStretch()
        self.header.addWidget(self.pop_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.header)
        layout.addWidget(self.canvas)

        # shown in the tab while the plot is in its own window
        self.placeholder = QWidget()
        label = QLabel(f"{title} is open in a separate window")
        label.setObjectName("plotPlaceholder")
        label.setAlignment(Qt.AlignCenter)
        back = QPushButton("Bring it back")
        back.clicked.connect(self.dock)
        placeholder_layout = QVBoxLayout(self.placeholder)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(label)
        placeholder_layout.addWidget(back, 0, Qt.AlignCenter)
        placeholder_layout.addStretch()
        self.placeholder.hide()

        self.container = container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self)
        container_layout.addWidget(self.placeholder)

    def refresh(self):
        self.figure.clear()
        with rc_context(self.rc):
            self.figure.set_facecolor(self.rc.get("figure.facecolor", "white"))
            self.draw(self.figure)
        self.canvas.draw_idle()

    def set_style(self, rc):
        self.rc = rc
        # the toolbar picks light or dark icons when it is made
        toolbar = NavigationToolbar2QT(self.canvas, self)
        self.header.replaceWidget(self.toolbar, toolbar)
        self.toolbar.deleteLater()
        self.toolbar = toolbar
        self.refresh()

    def toggle_window(self):
        if self.popup is None:
            self.pop_out()
        else:
            self.dock()

    def pop_out(self):
        self.popup = PlotWindow(self)
        self.placeholder.show()
        self.pop_button.setText("Dock")
        self.pop_button.setToolTip("Put the plot back in the main window")
        self.popup.show()

    def dock(self):
        if self.popup is None:
            return
        popup, self.popup = self.popup, None
        self.container.layout().insertWidget(0, self)
        self.show()
        self.placeholder.hide()
        self.pop_button.setText("Pop out")
        self.pop_button.setToolTip("Show the plot in its own window")
        popup.close()
        popup.deleteLater()


def draw_message(figure, text):
    figure.text(0.5, 0.5, text, ha="center", va="center", fontsize=11, alpha=0.7)


def draw_convergence(figure, result):
    if result is None:
        return draw_message(figure, "No result loaded")
    ax = figure.add_subplot()
    resvec = np.asarray(result.resvec)
    ax.semilogy(np.arange(1, len(resvec) + 1), resvec, "-o", markersize=4)
    relres = result.info.get("options", {}).get("relres")
    if relres:
        ax.axhline(relres, color="grey", linestyle="--", label="Tolerance")
        ax.legend()
    ax.grid(True)
    ax.set_title("Relative residual of the fgmres solution")
    ax.set_xlabel("Iteration number")
    ax.set_ylabel("Relative residual")


def draw_distribution(figure, values, label, unit, tissue, log=False):
    if values is None:
        return draw_message(figure, "No result loaded")
    ax = figure.add_subplot()
    ax.hist(values, bins=100, log=log, alpha=0.85)
    median, p99 = np.percentile(values, [50, 99])
    ax.axvline(median, color="grey", linestyle="--", label=f"Median {median:.4g}")
    ax.axvline(p99, color="#c8372d", linestyle=":", label=f"99th percentile {p99:.4g}")
    ax.legend()
    ax.set_title(f"{label} on {tissue}, {len(values):,} facets")
    ax.set_xlabel(f"{label} ({unit})")
    ax.set_ylabel("Facets")


def draw_currents(figure, electrodes):
    if not electrodes:
        return draw_message(figure, "Electrode currents are shown for tDCS results")
    ax = figure.add_subplot()
    names = [e["name"] for e in electrodes]
    currents = [e["current"] * 1e3 for e in electrodes]
    colors = [electrode_color(e["voltage"]) for e in electrodes]
    bars = ax.bar(names, currents, color=colors)
    ax.bar_label(bars, fmt="%.3f", padding=2)
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.margins(y=0.15)
    ax.set_title("Electrode currents, positive into the head")
    ax.set_ylabel("Current (mA)")


def draw_slices(figure, data, index, color, cmap):
    # the slice at index, or all of them when index is None
    if data is None or not data["slices"]:
        return draw_message(figure, "No slices for this result, press Compute slices")
    slices = data["slices"]
    if index is not None and 0 <= index < len(slices):
        slices = [slices[index]]
    if len(slices) == 1:
        axes, legend_size = [figure.add_subplot()], 10
    else:
        rows = -(-len(slices) // 2)
        axes, legend_size = figure.subplots(rows, 2).ravel(), 7
        for ax in axes[len(slices) :]:
            ax.set_axis_off()
    for ax, data_slice in zip(axes, slices):
        draw_efield_slice(
            figure,
            ax,
            data_slice,
            data["tissues"],
            color=color,
            legend_size=legend_size,
            cmap=cmap,
        )
