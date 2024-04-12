import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import glob

script_directory = os.path.dirname(os.path.abspath(__file__))

root = tk.Tk()
directory = os.getcwd()
root.title(f"Eclypse Terminal ({directory})")
root.resizable(True, True)

window_width = 1000
window_height = 800

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)

root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

command_history = []
history_position = 0


def delete_history_duplicates():
    unique_commands = list(set(command_history))
    command_history.clear()
    command_history.extend(unique_commands)


def save_history():
    with open(os.path.join(os.getcwd(), "history.txt"), "w") as file:
        for command in command_history:
            file.write(command + "\n")
        delete_history_duplicates()


def load_history():
    if os.path.exists(os.path.join(os.getcwd(), "history.txt")):
        with open(os.path.join(os.getcwd(), "history.txt"), "r") as file:
            for line in file:
                command_history.append(line.strip())
            delete_history_duplicates()


load_history()

output_text = scrolledtext.ScrolledText(root)
output_text.pack(fill=tk.BOTH, expand=True)
output_text.configure(bg="black", fg="white", insertbackground="white")

output_text.insert(
    tk.END,
    "Welcome to the Eclypse Terminal!\nEclypse is a small, easy-to-reprogram terminal that allows easily adding custom cli commands.\n\n",
    "yellow",
)

custom_commands = {}
full_custom_command = []


def load_custom_commands():
    if os.path.exists(os.path.join(os.getcwd(), "custom_commands.txt")):
        with open(os.path.join(os.getcwd(), "custom_commands.txt"), "r") as file:
            full_custom_command.clear()
            for line in file:
                command, subprocess_command = line.strip().split(":", 1)
                custom_commands[command] = subprocess_command
                full_custom_command.append(line)


def save_custom_commands():
    with open(os.path.join(os.getcwd(), "custom_commands.txt"), "w") as file:
        for command, subprocess_command in custom_commands.items():
            file.write(f"{command}:{subprocess_command}\n")


def execute_command(event=None):
    custom = False
    global history_position
    global directory

    command = output_text.get("end-2c linestart", "end-1c")

    if command.strip() == "":
        output_text.insert(tk.END, "\n")
        return
    if command.lower() == "exit":
        root.destroy()
    if command.lower() == "clear history":
        os.remove(os.path.join(script_directory, 'history.txt'))
        output_text.insert(tk.END, "\nHistory Cleared Boss!\n", "green")
        command_history.clear()
        open(os.path.join(os.getcwd(), "history.txt", "w")).close()
        return
    if command.startswith("cd "):
        _, new_dir = command.split(" ", 1)
        try:
            if new_dir == "..":
                directory = os.path.dirname(directory)
                root.title(f"Eclypse Terminal ({directory})")
            elif new_dir == "~" or new_dir == "~/":
                directory = os.path.expanduser("~")
                root.title(f"Eclypse Terminal ({directory})")
            else:
                directory = os.path.join(directory, new_dir)
            os.chdir(directory)
            output_text.insert(
                tk.END, f"\nChanged directory to '{directory}'.\n", "green"
            )
            root.title(f"Eclypse Terminal ({directory})")
        except Exception as e:
            output_text.tag_config("red", foreground="red")
            output_text.insert(
                tk.END,
                "\n" + "ERROR: " + str(e) + " (Invalid directory! - Eclypse Team)\n",
                "red",
            )

        return

    if command.startswith("ls"):
        try:
            _, args = command.split(" ", 1)
        except ValueError:
            args = "*"

        try:
            if args.startswith(".."):
                path = os.path.join(directory, "..")
                args = args[2:].lstrip()
            elif args.startswith("."):
                path = directory
                args = args[1:].lstrip()
            else:
                path = directory

            if args:
                files = glob.glob(os.path.join(path, args))
            else:
                files = os.listdir(path)

            output_text.insert(tk.END, "\n" + "\n".join(files) + "\n", "green")
        except Exception as e:
            output_text.tag_config("red", foreground="red")
            output_text.insert(
                tk.END,
                "\n"
                + "ERROR: "
                + str(e)
                + " (You weren't meant to do that! - Eclypse Team)\n",
                "red",
            )
        return

    if command.startswith("addcmd "):
        _, custom_command, subprocess_command = command.split(" ", 2)
        custom_commands[custom_command] = subprocess_command
        save_custom_commands()
        load_custom_commands()
        output_text.insert(tk.END, f"\nCustom command '{custom_command}' added.\n")
        return
    if command.lower() == "cmds":
        output_text.insert(tk.END, "\n")
        for i in full_custom_command:
            output_text.insert(tk.END, i, "green")
        return
    if command.split(" ")[0] in custom_commands:
        custom_command, *args = command.split(" ")
        try:
            if command in command_history:
                command_history.remove(command)
            command_history.append(command)
            history_position = len(command_history)
            save_history()
            command = custom_commands[custom_command].format(*args)

            custom = True
        except Exception as e:
            output_text.tag_config("red", foreground="red")
            output_text.insert(
                tk.END,
                "\n"
                + "ERROR: "
                + str(e)
                + " (You weren't meant to do that! Make sure you use arguments if you forgot on of them! - Eclypse Team)\n",
                "red",
            )
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output_text.insert(tk.END, "\n" + output.decode(), "green")
    except Exception as e:
        output_text.tag_config("red", foreground="red")
        output_text.insert(
            tk.END,
            "\n"
            + "ERROR: "
            + str(e)
            + " (You weren't meant to do that! - Eclypse Team)\n",
            "red",
        )
    if not custom:
        if command in command_history:
            command_history.remove(command)
        command_history.append(command)
        history_position = len(command_history)
        save_history()


load_custom_commands()


def recall_previous_command(event):
    global history_position
    if len(command_history) == 0:
        return "break"
    history_position = max(0, history_position - 1)
    output_text.delete("end-2c linestart", "end-1c")
    output_text.insert(tk.END, command_history[history_position])
    output_text.see(tk.END)
    return "break"


def recall_next_command(event):
    global history_position
    if len(command_history) == 0:
        return "break"
    history_position = min(len(command_history) - 1, history_position + 1)
    output_text.delete("end-2c linestart", "end-1c")
    output_text.insert(tk.END, command_history[history_position])  # Removed "\n"
    output_text.see(tk.END)
    return "break"


def autocomplete_command(event):
    current_command = output_text.get("end-2c linestart", "end-1c")
    output_text.delete("end-2c linestart", "end-1c")
    matches = [
        command for command in command_history if command.startswith(current_command)
    ]
    if matches:
        output_text.insert(tk.END, matches[0] + "\n\n")
        output_text.delete("end-2c linestart", "end-1c")


def do_nothing(event):
    if output_text.compare("insert", "==", "end-1c linestart"):
        return "break"


output_text.bind("<BackSpace>", do_nothing)
output_text.bind("<Return>", execute_command)
output_text.bind("<Up>", recall_previous_command)
output_text.bind("<Down>", recall_next_command)
output_text.bind("<Tab>", autocomplete_command)
output_text.bind("<Control-l>", lambda e: output_text.delete(1.0, tk.END))
# output_text.bind("<Command-l>", lambda e: output_text.delete(1.0, tk.END))
output_text.focus()

output_text.tag_config("yellow", foreground="yellow")
output_text.tag_config("red", foreground="red")
output_text.tag_config("green", foreground="green")

for command in ["", "   "]:
    if command in command_history:
        command_history.remove(command)

root.mainloop()
