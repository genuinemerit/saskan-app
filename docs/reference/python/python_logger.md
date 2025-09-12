# Python Logger

See:  saskan/infra/log/logger.py

Separation of concerns: use saskan.server for server/client lifecycle; saskan.events for gameplay summaries/snapshots; saskan.debug for predicate/diagnostic logging.

How to use examples...

Configuration (in CLI manage or server bootstrap)

```python
from saskan.infra.log.logger import configure, get_logger, bind_context, TRACE

configure(env="dev", log_dir="/var/log/saskan")  # or omit log_dir in dev

# "server_file": RotatingFileHandler -> server.jsonl
# "events_file": RotatingFileHandler -> events.jsonl
# "debug_file":  RotatingFileHandler -> debug.jsonl

"server_file": {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "/var/log/saskan/server.jsonl",
}
"events_file": {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "/var/log/saskan/events.jsonl"},
"debug_file":  {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "/var/log/saskan/events.jsonl"},


srv_log = get_logger("saskan.server")
evt_log = get_logger("saskan.events")
dbg_log = get_logger("saskan.debug")

srv_log.info("server_started", host="127.0.0.1", port=7777)
dbg_log.trace("handshake_bytes", raw=b"...")     # dev-only trace
```

Attaching context and keeping in on every line:

```python
session_log = bind_context(srv_log, session_id="abc123", player_id="P42")
session_log.info("client_connected", addr="10.0.0.8:53012")
session_log.warning("latency_high", ms=180)
```

Logging an event snapshot:

```python
evt_log.info(
    "battle_summary",
    encounter_id="E-9001",
    attackers=3,
    defenders=2,
    outcome="attacker_victory",
    loot={"gold": 120, "items": ["ring", "potion"]},
)
```

In Python's logging system, the `*args` and `**kwargs` are typically used for passing additional arguments and keyword arguments to the logging method, respectively. These values can enhance the log output by adding contextual data or further configuration.

Here’s a breakdown of what values are typically passed:

## 1. **`*args`** (Positional Arguments)

* These are generally used to pass additional arguments to the log message, especially for things like exception info or arguments for a formatted log message.
* **Common Use Case**:

  * **Exception objects**: If you are logging an exception, you can pass the exception object to provide detailed traceback information.
  * **Formatted string parameters**: Sometimes, additional data is passed to format the log message dynamically (similar to how `printf` works in C).

**Example**:

```python
logger.warning("Something went wrong: %s", error_message)
```

In this case, the `*args` will contain the `error_message` as a tuple, and the logger will replace `%s` with the value of `error_message`.

```python
logger.warning("Error occurred: %s", "File not found")
```

Output:

```text
WARNING:root:Error occurred: File not found
```

**Exception Logging**

```python
try:
    1 / 0
except ZeroDivisionError as e:
    logger.warning("Exception occurred", exc_info=e)
```

Here, `exc_info=e` would be passed in `*args` to include the traceback in the log.

## 2. **`**kwargs`** (Keyword Arguments)

* These are used for additional configurations or parameters that modify how the log is recorded.
* **Common Use Cases**:

  * **`exc_info`**: When logging an exception, you can pass `exc_info=True` to include exception traceback information in the log message.
  * **`extra`**: A dictionary that allows you to add custom contextual data to the log entry. For instance, you might include user-related information or session details in the log entry.
  * **`stack_info`**: If set to `True`, this adds stack information to the log.

**Example**

```python
logger.warning("Something happened", extra={"user": "john_doe"})
```

This would include the extra context (`{"user": "john_doe"}`) in the log output.

**Logging with exceptions**

```python
try:
    1 / 0
except ZeroDivisionError as e:
    logger.warning("Division by zero error", exc_info=True)
```

## In Your Method (`warning`)

```python
def warning(self, message: str, *args, **kwargs):
    """
    Log a message with severity 'WARNING'.

    :param message: The log message.
    """
    self.logger.warning(message, *args, **kwargs)
```

* **`*args`** could be used for things like:

  * Exception objects: `*args = (exception_info,)`
  * Extra parameters that fit into the log message template, like additional data that should be inserted.
* **`**kwargs`** could be used for:

  * Custom data via the `extra` keyword: `**kwargs = {"extra": {"user": "john_doe"}}`
  * `exc_info=True` for logging exception tracebacks: `**kwargs = {"exc_info": True}`

## Example Usage of `warning` Method

```python
logger.warning("Disk space is low: %d%% remaining", 10)  # *args: (10,)
logger.warning("File not found", exc_info=True)  # *args: (), **kwargs: {"exc_info": True}
logger.warning("User logged in", extra={"user": "jane_doe"})  # **kwargs: {"extra": {"user": "jane_doe"}}
```

In each case:

* `*args` is used for dynamic content (e.g., formatting arguments).
* `**kwargs` is used for additional metadata like `exc_info` or `extra`.

---

The Python `logging` module can capture the **module name** by default, and it can also capture the **class name** if you include it in your logging configuration.

### 1. **Module Name**

By default, the `logging` module captures the **name of the module** where the logging call was made. This is typically the name of the Python file/module.

For example:

```python
import logging

logger = logging.getLogger(__name__)  # Uses the module name (usually the filename)
logger.warning('This is a warning message')
```

In the log output, you'll see something like:

```text
module_name.py: WARNING: This is a warning message
```

Here, `module_name.py` is the name of the module, which is equivalent to `__name__` in the logger.

### 2. **Function and Line Number**

The standard logging will automatically include **line numbers** and **function names** when you use the default `%(lineno)d` and `%(funcName)s` formatting options.

For example:

```python
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - %(lineno)d')
logger.warning('Warning message')
```

Output might look like:

```text
2024-11-22 14:45:23,123 - module_name - WARNING - Warning message - function_name - 42
```

### 3. **Class Name**

If you're working inside a class method and would like to include the **class name**, you can include it manually in the logger's format string. You can capture the class name using `%(classname)s` or by manually using `self.__class__.__name__` when logging inside a method.

Example:

```python
class MyClass:
    def my_method(self):
        logger = logging.getLogger(__name__)
        logger.warning('This is a message from within a class.')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(classname)s - %(funcName)s - %(lineno)d')
```

If the `%(classname)s` is not available by default in your format, you can manually add it using `logging.Filter` to dynamically include the class name.

### Example of Class Name and Module Name in Logging

```python
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(classname)s - %(funcName)s - %(lineno)d')
logger = logging.getLogger('my_module')

class MyClass:
    def my_method(self):
        # Add class name manually to the log
        logger.warning('This is a message from inside a method.')

    def another_method(self):
        logger.warning('This is from another method.')

# Create an instance of the class
obj = MyClass()
obj.my_method()
obj.another_method()
```

### 4. **Customizing Logging Format for Class Name**

To capture the **class name** in the logs, you can use a custom logging format. Here's an example that captures **class name** and **module name**:

```python
import logging

class ClassNameFilter(logging.Filter):
    def filter(self, record):
        record.classname = record.pathname.split('/')[-1]  # Example of extracting class name from path
        return True

logger = logging.getLogger(__name__)
logger.addFilter(ClassNameFilter())

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(classname)s - %(funcName)s - %(lineno)d')
logger.warning('This is a warning message')
```

### Conclusion

* The `logging` module automatically captures **module name** and **line number**.
* For **class names**, you'll need to manually add it via custom log formatting, or by using a `logging.Filter`.
* **Function names** can be captured with `%(funcName)s` in the logging format string.

---

If you include `%(classname)s` in the `basicConfig` of the `logging` module and the logging event occurs outside of a class context (i.e., not inside a class method or instance), the `logging` module will **not raise an error**. Instead, it will simply not print anything for the `classname` placeholder.

### Why?

The `logging` module uses `record.classname` as part of the logging record. If the log entry is made outside of a class, `record.classname` will not be set, so the formatter will simply leave that placeholder empty. It doesn't raise an error because the `logging` module is designed to handle missing attributes gracefully.

### Example

Let's say you have this logging configuration with `%(classname)s`:

```python
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(classname)s - %(funcName)s - %(lineno)d')

logger = logging.getLogger('example')

# Logging outside of any class
logger.warning("This is a warning!")
```

Since the log is being made outside of a class, the `classname` placeholder will simply be empty in the output:

```text
2024-11-22 15:45:23,123 - example - WARNING - This is a warning! -  - warning - 10
```

Notice that the `classname` part is just empty, but no error is raised.

### Handling the Missing Class Name Gracefully

If you want to ensure that a value is always present for the `classname` field (even when the log is made outside of a class), you can add a `logging.Filter` that manually sets `record.classname` for you.

Example:

```python
import logging

class ClassNameFilter(logging.Filter):
    def filter(self, record):
        # If record is not from a class, provide a default value for classname
        if not hasattr(record, 'classname'):
            record.classname = 'NoClass'  # Default value
        return True

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(classname)s - %(funcName)s - %(lineno)d')

# Adding filter to set classname if it's missing
logger = logging.getLogger('example')
logger.addFilter(ClassNameFilter())

# Logging outside of any class
logger.warning("This is a warning!")
```

Output with filter applied:

```text
2024-11-22 15:45:23,123 - example - WARNING - This is a warning! - NoClass - warning - 10
```

In this case, even though the log message was created outside of a class, the `classname` field is populated with `'NoClass'`.

### Summary Notes

* The `logging` module will **not raise an error** if `%(classname)s` is used but no class is present in the log record.
* Instead, it will simply **omit** the class name, leaving the placeholder empty.
* To handle this gracefully, you can use a `logging.Filter` to set a default class name when logging outside a class.

---

Logging module as a plug-in?

This is a very interesting and powerful concept for a logging framework! Implementing something like this is absolutely feasible in Python, but it requires a bit of thought and a few advanced techniques. Let me break down the general idea and how you can potentially implement such a plugin-like system, as well as some considerations.

### Problem Outline

You want to configure a logging system where you can "insert" logging statements (like `DEBUG` level events) dynamically into your application code—without manually adding logging calls into each method or function.

### Key Goals

* **External Configuration:** You want to configure logging behavior outside of your core code.
* **Dynamic Injection:** Insert log statements into specific methods/functions/classes without modifying the original code.
* **Granular Control:** You want to control when and where the logs appear, for example, at the top of a method or after a specific event.

### Solution Overview

1. **External Configuration (via config or plugin)**:

   * This can be handled through an external configuration file or a plugin-style system that dynamically controls what gets logged and where.

2. **Function Decorators or Wrappers for Logging**:

   * You can create decorators or wrappers to dynamically add logging into functions or methods without directly modifying their code.

3. **Custom Logging Handler**:

   * You can create a custom logging handler that interacts with your logging configuration and ensures that log messages are inserted at the appropriate points in your code.

4. **Tracebacks for Dynamic Logging**:

   * Using Python's `trace` module can help inject debugging events dynamically during function calls, allowing you to record entry/exit points without changing function logic.

### Step-by-Step Conceptual Plan

#### 1. **Use a Configuration File**

* You can use a JSON, YAML, or simple Python config file that specifies where and what types of logging to insert, e.g., function name, log level, and the message to log.

Example `logging_config.json`:

```json
{
    "logging_points": [
        {"module": "module_name", "function": "function_name", "level": "DEBUG", "message": "Entered function xyz"},
        {"module": "module_name", "function": "another_function", "level": "INFO", "message": "Starting critical process"}
    ]
}
```

#### 2. **Dynamic Injection Using Function Decorators**

* Define a decorator that can be applied to functions or methods. This decorator will insert logging at the start (or anywhere in the function) based on the configuration.

```python
import logging
import functools

def log_function_entry(level="DEBUG", message="Function entered"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Insert logging statement at function entry
            logging.log(getattr(logging, level), message)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

* Then, in your core code, you can simply add the decorator to functions you want to automatically log:

```python
@log_function_entry(level="DEBUG", message="Entering function xyz")
def function_xyz():
    # Function code here
    pass
```

#### 3. **Centralized Logging Configuration**:

* Set up your logger with a configuration file or dictionary. This would allow your logging setup to be external and flexible, without having to hard-code log calls throughout the code.

```python
import logging.config
import json

def setup_logging():
    with open('logging_config.json', 'r') as file:
        config = json.load(file)
        logging.config.dictConfig(config)

setup_logging()

# Use logger
logging.debug("Debug message")
```

#### 4. **Custom Logging Handler**:

* For more sophisticated needs, you can also create custom logging handlers that add functionality (like writing to different places, triggering certain actions, or filtering logs dynamically). A custom handler could be created to listen to specific function calls or modules.

```python
import logging

class MyCustomHandler(logging.Handler):
    def emit(self, record):
        # Custom logic for handling log entries
        pass

logging.getLogger().addHandler(MyCustomHandler())
```

### Potential Challenges:

1. **Performance Overhead**: Adding logging to many functions could introduce some performance overhead. To mitigate this, ensure that logging only happens in the development environment or using a configuration toggle.
2. **Complexity in Config Management**: Managing dynamic logging can add complexity to your codebase. Make sure to test thoroughly to ensure that logging configurations are correctly handled and applied without interfering with business logic.
3. **Dynamic Code Changes**: Injecting logs dynamically might be challenging in some cases, especially if methods or functions are complex, and their entry/exit points are not well-defined.

### Using the `trace` Module for More Dynamic Control:

You could also leverage the Python `trace` module, which allows you to trace function calls, line executions, and more. This could help you add logging dynamically to many parts of your code without manually adding decorators.

```python
import trace

def log_function_call(frame, event, arg):
    if event == "call":
        print(f"Function {frame.f_code.co_name} called at line {frame.f_lineno}")
    return log_function_call

tracer = trace.Trace(trace=0, count=1)
tracer.run('log_function_call()')
```

### Conclusion:

* **Yes, it's possible** to implement a logging framework that works dynamically, like a plugin system, for functions/methods in Python.
* Using **decorators** and an external **configuration file** will allow you to dynamically insert log messages.
* Python's **logging module** and **trace module** can be used to achieve the desired behavior without modifying the core functionality.
* It may introduce some complexity, but it's certainly doable with Python's flexibility!

