import datetime

def initialize(root, output_text, execute_command):
    def date_command(event=None):
        now = datetime.datetime.now()
        output_text.insert(tk.END, "\n" + now.strftime("%Y-%m-%d %H:%M:%S") + "\n", "green")

    # Add the new command to the command history
    execute_command.command_history.append("!date")

    # Override the execute_command function to handle the new command
    original_execute_command = execute_command
    def new_execute_command(event=None):
        command = output_text.get("end-2c linestart", "end-1c")
        if command == "!date":
            date_command()
        else:
            original_execute_command(event)

    root.bind("<Return>", new_execute_command)
