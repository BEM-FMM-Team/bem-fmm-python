import tkinter as tk
from tkinter import ttk

import numpy as np

from engines.gui.quat_to_xyz import quat_to_xyz


def create_gui(
    coil_names,
    new_coil,
    get_coil,
    get_coils,
    edit_coil_com,
    edit_coil_rot,
    edit_coil_cur,
    delete_coil,
    save_coil_config,
    add_axes,
    remove_axes,
    auto_orient,
    save_last_coil,
    undo_operation,
):
    # creates a tk GUI that conducts arbitrary call back functions
    root = tk.Tk()
    root.title("Coil Placement")

    # new coils
    ttk.Label(root, text="New Coil:").grid(row=0, column=0, padx=5, pady=5)

    # type
    ttk.Label(root, text="Coil Type").grid(row=1, column=0, padx=5, pady=5)
    coil_var = tk.StringVar(value=coil_names[0])
    coil_dropdown = ttk.Combobox(
        root, textvariable=coil_var, values=coil_names, state="readonly"
    )
    coil_dropdown.grid(row=1, column=1, padx=5, pady=5)

    # coordinates
    ttk.Label(root, text="X").grid(row=2, column=0)
    x_entry = ttk.Entry(root)
    x_entry.grid(row=2, column=1)
    x_entry.insert(0, "42e-3")

    ttk.Label(root, text="Y").grid(row=3, column=0)
    y_entry = ttk.Entry(root)
    y_entry.grid(row=3, column=1)
    y_entry.insert(0, "0")

    ttk.Label(root, text="Z").grid(row=4, column=0)
    z_entry = ttk.Entry(root)
    z_entry.grid(row=4, column=1)
    z_entry.insert(0, "79.5e-3")

    ttk.Label(root, text="current").grid(row=5, column=0)
    dIdt_entry = ttk.Entry(root)
    dIdt_entry.grid(row=5, column=1)
    dIdt_entry.insert(0, "9.4e7")

    # rotation flag
    auto_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(root, text="Auto Orient", variable=auto_var).grid(row=2, column=2)

    # selecting coils
    ttk.Label(root, text="Select Coil").grid(row=7, column=0, padx=5, pady=5)
    coil_listbox = tk.Listbox(root)
    coil_listbox.grid(row=7, column=0, padx=5, pady=5)

    next_coil_id = 0

    gui_ids = []

    def add_coil():
        nonlocal next_coil_id

        coil_type = coil_var.get()

        x = float(x_entry.get())
        y = float(y_entry.get())
        z = float(z_entry.get())
        auto = auto_var.get()
        i = float(dIdt_entry.get())

        new_coil(coil_type, np.array([x, y, z]), auto, i)
        coils = get_coils()
        coil_listbox.delete(0, tk.END)
        gui_ids.clear()

        for coil in coils.values():
            coil_listbox.insert(tk.END, coil.name)
            gui_ids.append(coil.id)

    # add coil
    add_button1 = ttk.Button(root, text="Add Coil", command=add_coil)
    add_button1.grid(row=3, column=2, columnspan=2, pady=10)

    # coil editing
    ttk.Label(root, text="Coil Editing:").grid(row=6, column=0, padx=5, pady=5)

    # editing coils
    def edit_selected_coil():
        selection = coil_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        id = gui_ids[idx]
        coil = get_coil(id)
        save_last_coil()
        add_axes(id)
        print(gui_ids)

        editor = tk.Toplevel(root)
        editor.title(f"Edit Coil {id}")

        def on_close():
            remove_axes()
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

        ttk.Label(editor, text="X").grid(row=1, column=0, padx=5, pady=5)
        x1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=x_var,
        )
        x = ttk.Entry(editor, textvariable=x_var)
        x.grid(row=1, column=1, columnspan=2, pady=10)
        x1.grid(row=1, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="Y").grid(row=2, column=0, padx=5, pady=5)
        y1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=y_var,
        )
        y = ttk.Entry(editor, textvariable=y_var)
        y.grid(row=2, column=1, columnspan=2, pady=10)
        y1.grid(row=2, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="Z").grid(row=3, column=0, padx=5, pady=5)
        z1 = tk.Scale(
            editor,
            from_=-0.15,
            to=0.15,
            resolution=0.0001,
            orient="horizontal",
            variable=z_var,
        )
        z = ttk.Entry(editor, textvariable=z_var)
        z.grid(row=3, column=1, columnspan=2, pady=10)
        z1.grid(row=3, column=3, columnspan=2, pady=10)

        # orientation

        ttk.Label(editor, text="rX").grid(row=4, column=0, padx=5, pady=5)
        rx1 = tk.Scale(
            editor,
            from_=-180.0,
            to=180.0,
            resolution=0.001,
            orient="horizontal",
            variable=rx_var,
        )
        rx2 = ttk.Entry(editor, textvariable=rx_var)
        rx1.grid(row=4, column=1, columnspan=2, pady=10)
        rx2.grid(row=4, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="rY").grid(row=5, column=0, padx=5, pady=5)
        ry1 = tk.Scale(
            editor,
            from_=-180,
            to=180,
            resolution=0.001,
            orient="horizontal",
            variable=ry_var,
        )
        ry2 = ttk.Entry(editor, textvariable=ry_var)
        ry1.grid(row=5, column=1, columnspan=2, pady=10)
        ry2.grid(row=5, column=3, columnspan=2, pady=10)

        ttk.Label(editor, text="rZ").grid(row=6, column=0, padx=5, pady=5)
        rz1 = tk.Scale(
            editor,
            from_=-180,
            to=180,
            resolution=0.001,
            orient="horizontal",
            variable=rz_var,
        )
        rz2 = ttk.Entry(editor, textvariable=rz_var)
        rz1.grid(row=6, column=1, columnspan=2, pady=10)
        rz2.grid(row=6, column=3, columnspan=2, pady=10)

        # current

        ttk.Label(editor, text="dIdt").grid(row=7, column=0, padx=5, pady=5)
        dIdt = ttk.Entry(editor, textvariable=i_var)
        dIdt.grid(row=7, column=2, columnspan=2, pady=10)

        # auto_orient
        def auto_orient_id():
            auto_orient(id)
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
            lambda *args: edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )
        y_var.trace_add(
            "write",
            lambda *args: edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )
        z_var.trace_add(
            "write",
            lambda *args: edit_coil_com(
                id, np.array([x_var.get(), y_var.get(), z_var.get()])
            ),
        )

        rx_var.trace_add(
            "write",
            lambda *args: edit_coil_rot(
                id, np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )
        ry_var.trace_add(
            "write",
            lambda *args: edit_coil_rot(
                id, np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )
        rz_var.trace_add(
            "write",
            lambda *args: edit_coil_rot(
                id, np.array([rx_var.get(), ry_var.get(), rz_var.get()])
            ),
        )

        i_var.trace_add("write", lambda *args: edit_coil_cur(id, i_var.get()))

        editor.mainloop()

        return

    add_button2 = ttk.Button(root, text="Edit Coil", command=edit_selected_coil)
    add_button2.grid(row=7, column=1, columnspan=2, pady=10)

    # deleteing coils

    def delete_selected_coil():
        nonlocal gui_ids
        selection = coil_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        delete_coil(gui_ids[idx])
        coil_listbox.delete(idx)
        del gui_ids[idx]

    add_button3 = ttk.Button(root, text="Delete Coil", command=delete_selected_coil)
    add_button3.grid(row=7, column=2, columnspan=2, pady=10)

    # computing Efield
    ttk.Label(root, text="Electric Field:").grid(row=8, column=0, padx=5, pady=5)

    add_button4 = ttk.Button(root, text="save", command=save_coil_config)
    add_button4.grid(row=9, column=0, columnspan=2, pady=10)

    def undo():
        undo_operation()
        coils = get_coils()
        coil_listbox.delete(0, tk.END)
        gui_ids.clear()

        for coil in coils.values():
            coil_listbox.insert(tk.END, coil.name)
            gui_ids.append(coil.id)

        return

    add_button5 = ttk.Button(root, text="Undo", command=undo)
    add_button5.grid(row=9, column=1, columnspan=2, pady=10)

    return root


# def test_return(coil_type=None, xyz=None, a=None):
#     print(coil_type)
#     return
# create_gui(["ring", "WIP"], test_return, test_return, test_return, test_return, test_return, test_return, test_return)
