import numpy as np
import tkinter as tk
from tkinter import ttk

from engines.gui.quat_to_xyz import quat_to_xyz
from engines.gui.gui_backend import Backend

"""
GUI frontend for placing coils. This class is responsible for managing the widget.
"""


class Frontend:
    def __init__(self, head, names):
        # backend
        self.backend = Backend(head)

        # state
        self.root = tk.Tk()
        self.gui_ids = []
        self.coil_names = names

        # widget values
        self.coil_dropdown = None
        self.coil_listbox = None
        self.x_entry = None
        self.y_entry = None
        self.z_entry = None
        self.dIdt_entry = None
        self.auto_flag = None
        self.custom_coil = None

    def create_root(self):
        # creates a tk GUI that conducts arbitrary call back functions
        # merely constructs the window and does not run the program
        self.root.title("Coil Placement")

        # new coils
        ttk.Label(self.root, text="New Coil:").grid(row=0, column=0, padx=5, pady=5)

        # type
        ttk.Label(self.root, text="Coil Type").grid(row=1, column=0, padx=5, pady=5)
        self.coil_dropdown = ttk.Combobox(
            self.root, values=self.coil_names, state="readonly"
        )
        self.coil_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.coil_dropdown.set(self.coil_names[0])

        # coordinates
        ttk.Label(self.root, text="X (m)").grid(row=2, column=0)
        self.x_entry = ttk.Entry(self.root)
        self.x_entry.grid(row=2, column=1)
        self.x_entry.insert(0, "0")

        ttk.Label(self.root, text="Y (m)").grid(row=3, column=0)
        self.y_entry = ttk.Entry(self.root)
        self.y_entry.grid(row=3, column=1)
        self.y_entry.insert(0, "0")

        ttk.Label(self.root, text="Z (m)").grid(row=4, column=0)
        self.z_entry = ttk.Entry(self.root)
        self.z_entry.grid(row=4, column=1)
        self.z_entry.insert(0, "0")

        clear_button = ttk.Button(self.root, text="Clear", command=self.clear_gui)
        clear_button.grid(row=4, column=2, columnspan=2, pady=10)

        ttk.Label(self.root, text="dIdt (amps/ns)").grid(row=5, column=0)
        self.dIdt_entry = ttk.Entry(self.root)
        self.dIdt_entry.grid(row=5, column=1)
        self.dIdt_entry.insert(0, "1e6")

        ttk.Label(self.root, text="Custom coil").grid(row=6, column=0, padx=5, pady=5)
        self.custom_coil = ttk.Entry(self.root)
        self.custom_coil.grid(row=6, column=1)

        add_button4 = ttk.Button(
            self.root, text="Add Custom", command=self.import_custom_coil
        )
        add_button4.grid(row=6, column=2, columnspan=2, pady=10)

        # rotation flag
        self.auto_flag = tk.BooleanVar(value=True)
        auto_button = ttk.Checkbutton(
            self.root, text="Auto Orient", variable=self.auto_flag
        )
        auto_button.grid(row=2, column=2)

        # selecting coils
        ttk.Label(self.root, text="Select Coil").grid(row=7, column=0, padx=5, pady=5)
        self.coil_listbox = tk.Listbox(self.root)
        self.coil_listbox.grid(row=7, column=0, padx=5, pady=5)

        # add coil
        add_button1 = ttk.Button(self.root, text="Add Coil", command=self.add_coil)
        add_button1.grid(row=3, column=2, columnspan=2, pady=10)

        # coil editing

        add_button2 = ttk.Button(
            self.root, text="Edit Coil", command=self.edit_selected_coil
        )
        add_button2.grid(row=7, column=1, columnspan=2, pady=10)

        add_button3 = ttk.Button(
            self.root, text="Delete Coil", command=self.delete_selected_coil
        )
        add_button3.grid(row=7, column=2, columnspan=2, pady=10)

        # computing Efield
        ttk.Label(self.root, text="Electric Field:").grid(
            row=8, column=0, padx=5, pady=5
        )

        add_button5 = ttk.Button(
            self.root, text="save", command=self.backend.save_coil_config
        )
        add_button5.grid(row=10, column=0, columnspan=2, pady=10)

        add_button6 = ttk.Button(self.root, text="Undo", command=self.undo)
        add_button6.grid(row=10, column=1, columnspan=2, pady=10)

        return

    def activate(self):
        # activates the entire system
        self.backend.renderer.activate()
        self.create_root()

        def tick():
            # iterate state
            self.backend.renderer.render_plot()
            self.root.after(16, tick)
            return

        tick()
        self.root.mainloop()
        return

    def add_coil(self):
        # creates a new coil
        coil_type = self.coil_dropdown.get()

        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())
        auto = self.auto_flag.get()
        dIdt = float(self.dIdt_entry.get())

        self.backend.new_coil(
            np.array([x, y, z]),
            coil_type,
            dIdt,
            auto,
            [self.root.winfo_x(), self.root.winfo_y()],
        )
        coils = self.backend.get_coils()
        self.coil_listbox.delete(0, tk.END)
        self.gui_ids.clear()

        for coil in coils.values():
            self.coil_listbox.insert(tk.END, coil.name)
            self.gui_ids.append(coil.id)
        return

    def import_custom_coil(self):
        # creates a new custom coil
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())
        auto = self.auto_flag.get()
        dIdt = float(self.dIdt_entry.get())
        name = self.custom_coil.get()

        self.backend.new_custom_coil(np.array([x, y, z]), name, dIdt, auto)
        coils = self.backend.get_coils()
        self.coil_listbox.delete(0, tk.END)
        self.gui_ids.clear()

        for coil in coils.values():
            self.coil_listbox.insert(tk.END, coil.name)
            self.gui_ids.append(coil.id)
        return

    def delete_selected_coil(self):
        # deletes a coil
        selection = self.coil_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        self.backend.delete_coil(self.gui_ids[idx])
        self.coil_listbox.delete(idx)
        del self.gui_ids[idx]

    def edit_selected_coil(self):
        # prepares a coil for editing
        selection = self.coil_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        id = self.gui_ids[idx]
        coil = self.backend.get_coil(id)
        self.backend.save_last_coil()

        ## rendering
        self.backend.renderer.show_world_axes(coil)

        print(self.gui_ids)

        self.root.update_idletasks()

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()

        editor = tk.Toplevel(self.root)

        editor.geometry(f"+{root_x}+{root_y}")

        editor.title(f"Edit Coil {id}")

        def on_close():
            self.backend.renderer.remove_world_axes()
            editor.destroy()

        editor.protocol("WM_DELETE_WINDOW", on_close)

        x_var = tk.DoubleVar(value=coil.com[0])
        y_var = tk.DoubleVar(value=coil.com[1])
        z_var = tk.DoubleVar(value=coil.com[2])

        rx_var = tk.DoubleVar(value=quat_to_xyz(coil)[0])
        ry_var = tk.DoubleVar(value=quat_to_xyz(coil)[1])
        rz_var = tk.DoubleVar(value=quat_to_xyz(coil)[2])

        i_var = tk.DoubleVar(value=coil.dIdt)

        # position

        ttk.Label(editor, text="Position").grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(editor, text="X (m)").grid(row=1, column=0, padx=5, pady=5)
        x1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=x_var,
            length=200,
        )
        x = ttk.Entry(editor, textvariable=x_var)
        x.grid(row=1, column=1, columnspan=2, pady=10)
        x1.grid(row=1, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="Y (m)").grid(row=2, column=0, padx=5, pady=5)
        y1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=y_var,
            length=200,
        )
        y = ttk.Entry(editor, textvariable=y_var)
        y.grid(row=2, column=1, columnspan=2, pady=10)
        y1.grid(row=2, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="Z (m)").grid(row=3, column=0, padx=5, pady=5)
        z1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=z_var,
            length=200,
        )
        z = ttk.Entry(editor, textvariable=z_var)
        z.grid(row=3, column=1, columnspan=2, pady=10)
        z1.grid(row=3, column=3, columnspan=2, pady=10)

        # orientation

        ttk.Label(editor, text="rX (degrees)").grid(row=4, column=0, padx=5, pady=5)
        rx1 = tk.Scale(
            editor,
            from_=-180.0,
            to=180.0,
            resolution=0.001,
            orient="horizontal",
            variable=rx_var,
            length=200,
        )
        rx2 = ttk.Entry(editor, textvariable=rx_var)
        rx1.grid(row=4, column=1, columnspan=2, pady=10)
        rx2.grid(row=4, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="rY (degrees)").grid(row=5, column=0, padx=5, pady=5)
        ry1 = tk.Scale(
            editor,
            from_=-180,
            to=180,
            resolution=0.001,
            orient="horizontal",
            variable=ry_var,
            length=200,
        )
        ry2 = ttk.Entry(editor, textvariable=ry_var)
        ry1.grid(row=5, column=1, columnspan=2, pady=10)
        ry2.grid(row=5, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="rZ (degrees)").grid(row=6, column=0, padx=5, pady=5)
        rz1 = tk.Scale(
            editor,
            from_=-180,
            to=180,
            resolution=0.001,
            orient="horizontal",
            variable=rz_var,
            length=200,
        )
        rz2 = ttk.Entry(editor, textvariable=rz_var)
        rz1.grid(row=6, column=1, columnspan=2, pady=10)
        rz2.grid(row=6, column=3, columnspan=2, pady=10)

        # current

        ttk.Label(editor, text="dIdt (amps/ns)").grid(row=7, column=0, padx=5, pady=5)
        dIdt = ttk.Entry(editor, textvariable=i_var)
        dIdt.grid(row=7, column=2, columnspan=2, pady=10)

        # auto_orient
        def auto_orient_id():
            self.backend.auto_orient(id)
            new_rot = quat_to_xyz(coil)
            rx_var.set(new_rot[0])
            ry_var.set(new_rot[1])
            rz_var.set(new_rot[2])
            return

        auto_orient_button = ttk.Button(
            editor, text="Auto Orient", command=auto_orient_id
        )
        auto_orient_button.grid(row=8, column=0, columnspan=2, pady=10)

        x_var.trace_add(
            "write",
            lambda *args: self.backend.edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )
        y_var.trace_add(
            "write",
            lambda *args: self.backend.edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )
        z_var.trace_add(
            "write",
            lambda *args: self.backend.edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )

        base_rot = self.backend.get_coil(id).rot
        twist = tk.DoubleVar(value=0.0)

        updating_rot = False
        updating_twist = False

        def edit_coil_rot_gui(new_rot):
            nonlocal updating_rot
            nonlocal base_rot
            if updating_twist:
                return
            updating_rot = True
            self.backend.edit_coil_rot(id, new_rot)
            base_rot = self.backend.get_coil(id).rot
            twist.set(0)
            updating_rot = False
            return

        rx_var.trace_add(
            "write",
            lambda *args: edit_coil_rot_gui(
                np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )
        ry_var.trace_add(
            "write",
            lambda *args: edit_coil_rot_gui(
                np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )
        rz_var.trace_add(
            "write",
            lambda *args: edit_coil_rot_gui(
                np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )

        i_var.trace_add(
            "write", lambda *args: self.backend.edit_coil_cur(id, i_var.get())
        )

        def apply_twist_gui(twist, base_rot):
            nonlocal updating_twist
            if updating_rot:
                return
            updating_twist = True
            self.backend.apply_twist(id, twist, base_rot)
            new_rot = quat_to_xyz(coil)
            rx_var.set(round(new_rot[0], 3))
            ry_var.set(round(new_rot[1], 3))
            rz_var.set(round(new_rot[2], 3))
            updating_twist = False
            return

        ttk.Label(editor, text="twist (degrees)").grid(row=9, column=0, padx=5, pady=5)
        twist_bar = tk.Scale(
            editor,
            from_=-180,
            to=180,
            resolution=0.001,
            orient="horizontal",
            variable=twist,
            length=200,
        )
        twist_entry = ttk.Entry(editor, textvariable=twist)
        twist_bar.grid(row=9, column=1, columnspan=2, pady=10)
        twist_entry.grid(row=9, column=3, columnspan=2, pady=10)

        twist.trace_add("write", lambda *args: apply_twist_gui(twist.get(), base_rot))

        ok_button = ttk.Button(editor, text="OK", command=on_close)
        ok_button.grid(row=10, column=0, columnspan=2, pady=10)

        def cancel():
            on_close()
            self.undo()

        cancel_button = ttk.Button(editor, text="cancel", command=cancel)
        cancel_button.grid(row=10, column=2, columnspan=2, pady=10)

        editor.mainloop()

        return

    def clear_gui(self):
        self.coil_dropdown.set("")
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        self.z_entry.delete(0, tk.END)
        self.dIdt_entry.delete(0, tk.END)
        self.custom_coil.delete(0, tk.END)

        return

    def undo(self):
        self.backend.undo_operation()
        coils = self.backend.get_coils()
        self.coil_listbox.delete(0, tk.END)
        self.gui_ids.clear()

        for coil in coils.values():
            self.coil_listbox.insert(tk.END, coil.name)
            self.gui_ids.append(coil.id)

        return
