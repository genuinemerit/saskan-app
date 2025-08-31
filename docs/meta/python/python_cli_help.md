# CLI Help Python code

To set up a callable Python class method that provides help via the command line, you can use docstrings to document the method and use the `argparse` module to create a command-line interface with a `--help` option. Here's an example:

```python
import argparse

class MyClass:
    def my_method(self, param1, param2):
        """
        Perform some action.

        Parameters:
          - param1: Description of param1.
          - param2: Description of param2.
        """
        print(f"Executing my_method with param1={param1} and param2={param2}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MyClass Command Line Interface")
    
    # Add command-line arguments for your method parameters
    parser.add_argument("param1", type=int, help="Description of param1")
    parser.add_argument("param2", type=str, help="Description of param2")

    args = parser.parse_args()

    # Create an instance of MyClass and call the method with provided command-line arguments
    my_instance = MyClass()
    my_instance.my_method(args.param1, args.param2)
```

In this example:

* The `my_method` has a docstring that provides documentation for its parameters.
* The `argparse` module is used to create a command-line interface.
* Command-line arguments are added for the parameters of `my_method`.
* The script creates an instance of `MyClass` and calls `my_method` with the provided command-line arguments.

When you run this script from the command line, you can use the `--help` option to see the documentation:

```bash
python script_name.py --help
```

This will display the help message with information about the script and its parameters.

---

## Help for multiple methods

You can create a command-line interface for multiple methods within a class using a similar approach. One common pattern is to use subcommands. Here's an example using the `argparse` module:

```python
import argparse

class ETL_BAR:
    def __init__(self):
        pass

    def start_batch(self, param1, param2):
        """
        Start a batch process.

        Parameters:
          - param1: Description of param1.
          - param2: Description of param2.
        """
        print(f"Starting batch with param1={param1} and param2={param2}")

    def stop_batch(self, param3):
        """
        Stop a batch process.

        Parameters:
          - param3: Description of param3.
        """
        print(f"Stopping batch with param3={param3}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL_BAR Command Line Interface")

    # Create a subparser for each method
    subparsers = parser.add_subparsers(title="Available Commands", dest="command")

    # Subparser for the start_batch method
    start_batch_parser = subparsers.add_parser("start_batch", help="Start a batch process")
    start_batch_parser.add_argument("param1", type=int, help="Description of param1")
    start_batch_parser.add_argument("param2", type=str, help="Description of param2")

    # Subparser for the stop_batch method
    stop_batch_parser = subparsers.add_parser("stop_batch", help="Stop a batch process")
    stop_batch_parser.add_argument("param3", type=float, help="Description of param3")

    args = parser.parse_args()

    # Create an instance of ETL_BAR and call the selected method with provided command-line arguments
    etl_bar_instance = ETL_BAR()
    
    if args.command == "start_batch":
        etl_bar_instance.start_batch(args.param1, args.param2)
    elif args.command == "stop_batch":
        etl_bar_instance.stop_batch(args.param3)
    else:
        print("Invalid command. Use --help for available commands.")
```

In this example:

* The script uses subparsers to define different commands (`start_batch` and `stop_batch`).
* Each subparser has its own set of arguments, reflecting the parameters of the corresponding method.
* The `dest="command"` argument is used to store the selected command in the `args` namespace.
* Based on the selected command, the script calls the corresponding method with the provided command-line arguments.

You can run the script with `--help` to see the available commands and their respective arguments. For example:

```bash
python script_name.py --help
python script_name.py start_batch --help
python script_name.py stop_batch --help
```

---

## Display docstrings in CLI Help

`argparse` itself does not provide a built-in way to automatically display the docstring associated with the method being called. However, you can manually retrieve the docstring and include it in your help message. Here's an example:

```python
import argparse
import inspect

class ETL_BAR:
    def __init__(self):
        pass

    def start_batch(self, param1, param2):
        """
        Start a batch process.

        Parameters:
          - param1: Description of param1.
          - param2: Description of param2.
        """
        print(f"Starting batch with param1={param1} and param2={param2}")

    def stop_batch(self, param3):
        """
        Stop a batch process.

        Parameters:
          - param3: Description of param3.
        """
        print(f"Stopping batch with param3={param3}")

    def display_help(self, command):
        """
        Display help message for a specific command.

        Parameters:
          - command: The command for which to display help.
        """
        method = getattr(self, command, None)
        if method:
            print(f"Help for {command}:")
            print(inspect.getdoc(method))
        else:
            print(f"Command '{command}' not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL_BAR Command Line Interface")

    # Create a subparser for each method
    subparsers = parser.add_subparsers(title="Available Commands", dest="command")

    # Subparser for the start_batch method
    start_batch_parser = subparsers.add_parser("start_batch", help="Start a batch process")
    start_batch_parser.add_argument("param1", type=int, help="Description of param1")
    start_batch_parser.add_argument("param2", type=str, help="Description of param2")

    # Subparser for the stop_batch method
    stop_batch_parser = subparsers.add_parser("stop_batch", help="Stop a batch process")
    stop_batch_parser.add_argument("param3", type=float, help="Description of param3")

    # Subparser for the help method
    help_parser = subparsers.add_parser("help", help="Display help for a specific command")
    help_parser.add_argument("command", type=str, help="The command for which to display help")

    args = parser.parse_args()

    # Create an instance of ETL_BAR
    etl_bar_instance = ETL_BAR()

    if args.command == "help":
        etl_bar_instance.display_help(args.command)
    else:
        # Call the selected method with provided command-line arguments
        method = getattr(etl_bar_instance, args.command, None)
        if method:
            method(**vars(args))
        else:
            print(f"Invalid command. Use --help for available commands.")
```

In this example:

* I added a `display_help` method to the `ETL_BAR` class, which retrieves the docstring using `inspect.getdoc`.
* I added a subparser for the "help" command, which takes an additional argument for the command you want help with.
* When the "help" command is called, it calls `display_help` to print the docstring for the specified command.

Now, you can run the script as follows:

```bash
python script_name.py help start_batch
python script_name.py help stop_batch
```

This will display the docstring for the specified command.
