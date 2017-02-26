# Prepare Requirement

```
linux:~ $ git clone https://github.com/wsunccake/my_tool.git
linux:~ $ pip install PyBuilder

# setup IntelliJ IDEA/PyCharm IDE environment
linux:~/my_tool $ pyb pycharm_generate
```


# Usage PyBuilder

```
linux:~/my_tool $ pyb -h
linux:~/my_tool $ pyb -t

# Install Required Module
linux:~/my_tool $ pyb install_dependencies

# Run Unittest
linux:~/my_tool $ pyb run_unit_tests

# Build Package
linux:~/my_tool $ pyb -x run_unit_tests package

linux:~/my_tool $ pyb install
# Install
```
