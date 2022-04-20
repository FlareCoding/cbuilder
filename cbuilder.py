import os
import re
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

def clear_screen(): 
    # Windows 
    if os.name == 'nt': 
        _ = os.system('cls') 
    # Unix/Posix 
    else: 
        _ = os.system('clear') 

PRAGMA_ONCE_DEFINITION = '#pragma once\n'

DEFAULT_MAIN_FILE_SOURCE = '''#include <iostream>

using namespace {}; // project namespace

int main()
{{
    std::cout << "Hello World!\\n";
    return 0;
}}
'''

CMAKE_HEADER_DEFINITION = '''cmake_minimum_required(VERSION 3.0)
set(CMAKE_CONFIGURATION_TYPES "Debug;Release")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(UNIX AND NOT APPLE)
    set(LINUX TRUE)
endif()

if (APPLE)
    set(CMAKE_MACOSX_RPATH OFF)
endif()

add_definitions(-DUNICODE -D_UNICODE)

'''

g_project_name = None
g_current_module = None
g_current_system = None
g_current_cmake_dir = None

'''
Structure containing the name and the documentation for a C++ function.
'''
class CFunction:
    def __init__(self, name, description) -> None:
        self.return_type = 'void'
        self.name = name
        self.params = []
        self.description = description

'''
CClass is a template class for holding C++ project classes within a specific module.
It is able to hold public and private function names and variable names.
'''
class CClass:
    def __init__(self, name = 'class1') -> None:
        self.name = name
        self.public_functions: list[CFunction]   = []
        self.private_functions: list[CFunction]  = []
        self.public_variables   = []
        self.private_variables  = []

    # Remove the variable given its name
    def remove_variable(self, name: str) -> None:
        for var in self.public_variables:
            var_name = var.split(' ')[1]
            if var_name == name:
                self.public_variables.remove(var)
                return

        for var in self.private_variables:
            var_name = var.split(' ')[1]
            if var_name == name:
                self.private_variables.remove(var)
                return

    # Remove the function given its name
    def remove_function(self, name: str) -> None:
        for fn in self.public_functions:
            if fn.name == name:
                self.public_functions.remove(fn)
                return

        for fn in self.private_functions:
            if fn.name == name:
                self.private_functions.remove(fn)
                return

    # Generates the C++ function declaration signature
    def __get_header_function_declaration(self, fn: CFunction) -> str:
        result = ''

        # Write the function comment if neccessary
        if fn.description != None and len(fn.description) > 0:
            result += '\t\t/*\n\t\t\t{}\n\t\t*/\n'.format(fn.description.replace('\n', '\n\t\t\t'))

        # Write the function declaration
        result += '\t\t{} {}({});\n'.format(fn.return_type, fn.name, ', '.join(fn.params))

        # To make the spacing look good, if there was comment,
        # add a new line after the function declaration as well.
        if fn.description != None and len(fn.description) > 0:
            result += '\n'

        return result

    # Returns the function's signature as string
    def __get_function_signature(self, fn: CFunction) -> str:
        return '{} {}::{}({})'.format(fn.return_type, self.name, fn.name, ', '.join(fn.params))

    # Returns the function's signature
    # with curly braces defining the body.
    def __get_function_definition(self, fn: CFunction) -> str:
        return '\t{}\n\t{{\n\t}}\n'.format(self.__get_function_signature(fn))

    # Generates a C++ header file (.h)
    def __generate_header_file(self) -> None:
        global g_project_name, g_current_module, g_current_system

        # Check to make sure the file doesn't exist already
        if os.path.exists('{}.h'.format(self.name)):
            return

        with open(self.name + '.h', 'w') as f:
            # Pragma + includes
            f.write(PRAGMA_ONCE_DEFINITION)

            # Namespace begin
            f.write('\nnamespace {}::{}::{}\n{{\n'.format(g_project_name, g_current_module, g_current_system))

            # Class begin
            f.write('\tclass {}\n'.format(self.name))
            f.write('\t{')

            # Public functions
            if len(self.public_functions) > 0:
                f.write('\n')
                f.write('\tpublic:\n')

                for fn in self.public_functions:
                    code = self.__get_header_function_declaration(fn)
                    f.write(code)

            # Public variables
            if len(self.public_variables) > 0:
                f.write('\n')
                f.write('\tpublic:\n')
                
                for var in self.public_variables:
                    f.write('\t\t{};\n'.format(var))

            # Private functions
            if len(self.private_functions) > 0:
                f.write('\n')
                f.write('\tprivate:\n')

                for fn in self.private_functions:
                    code = self.__get_header_function_declaration(fn)
                    f.write(code)

            # Private variables
            if len(self.private_variables) > 0:
                f.write('\n')
                f.write('\tprivate:\n')
                
                for var in self.private_variables:
                    f.write('\t\t{};\n'.format(var))

            # Private functions
            f.write('\n')

            # Class end
            f.write('\t};\n')

            # Namespace end
            f.write('}\n')

    # Generates a C++ source file (.cpp)
    def __generate_source_file(self) -> None:
        global g_project_name, g_current_module

        with open(self.name + '.cpp', 'w') as f:
            f.write('#include "{}.h"\n\n'.format(self.name))

            # Namespace begin
            f.write('namespace {}::{}::{}\n{{\n'.format(g_project_name, g_current_module, g_current_system))

            # Create a list of all functions
            all_functions = self.public_functions + self.private_functions

            # Generate function definitions
            for fn in all_functions:
                f.write('{}\n'.format(self.__get_function_definition(fn)))

            # Namespace end
            f.write('}\n')

    # Generates a set of header and source files
    def generate_class_files(self):
        self.__generate_header_file()
        self.__generate_source_file()

'''
CSystem is a logical representation of a collection of classes
that directly relate to a unique set of functionality.
'''
class CSystem:
    def __init__(self, name = 'system1') -> None:
        self.name = name
        self.classes: list[CClass] = []

    # Returns a class with the given name
    def get_class(self, name) -> CClass:
        for cppclass in self.classes:
            if cppclass.name == name:
                return cppclass

        return None

     # Removes a class with the given name
    def remove_class(self, name) -> None:
        for cppclass in self.classes:
            if cppclass.name == name:
                self.classes.remove(cppclass)
                break

    # Creates the appropriate directory structure and
    # child C++ class header and source files on the disk.
    def generate_source_files(self) -> None:
        global g_current_system

        # Set the current module
        g_current_system = self.name

        # Create the directory for the module
        os.mkdir(self.name)

        # Enter the system directory
        os.chdir(self.name)

        # Iterate over every class in the module and
        # call its function to generate source files.
        for cppclass in self.classes:
            cppclass.generate_class_files()

        # Exit back from the module directory
        os.chdir('..')

        # Set the current module to None as we are done working with it
        g_current_system = None

    # Creates a CMakeLists.txt file that groups together and exposes
    # the contained class files to the parent module CMakeLists.
    def generate_cmake_file(self) -> None:
        global g_current_system
        g_current_system = self.name

        # Enter the system directory
        os.chdir(self.name)

        with open('CMakeLists.txt', 'w') as f:

            # Create a definition for header files
            f.write('set(\n\t{}_HEADERS\n\n'.format(self.name))

            for cppclass in self.classes:
                f.write('\t{}/{}/{}.h\n'.format(g_current_module, g_current_system, cppclass.name))

            f.write('\n\tPARENT_SCOPE\n)\n\n')

            # Create a definition for source files
            f.write('set(\n\t{}_SOURCES\n\n'.format(self.name))

            for cppclass in self.classes:
                f.write('\t{}/{}/{}.cpp\n'.format(g_current_module, g_current_system, cppclass.name))

            f.write('\n\tPARENT_SCOPE\n)\n\n')

        # Return to parent module directory
        os.chdir('..')

'''
CModule is essentially a C++ namespace. It encapsulates classes
for a specific subsystem within a project.
'''
class CModule:
    def __init__(self, name = 'module1') -> None:
        self.name = name
        self.systems: list[CSystem] = []

    # Returns a class with the given name
    def get_system(self, name) -> CSystem:
        for system in self.systems:
            if system.name == name:
                return system

        return None

    # Removes a class with the given name
    def remove_system(self, name) -> None:
        for system in self.systems:
            if system.name == name:
                self.systems.remove(system)
                break

    # Creates the appropriate directory structure and
    # child C++ class header and source files on the disk.
    def generate_source_files(self) -> None:
        global g_current_module

        # Set the current module
        g_current_module = self.name

        # Create the directory for the module
        os.mkdir(self.name)

        # Enter the module directory
        os.chdir(self.name)

        # Iterate over every class in the module and
        # call its function to generate source files.
        for system in self.systems:
            system.generate_source_files()

        # Exit back from the module directory
        os.chdir('..')

        # Set the current module to None as we are done working with it
        g_current_module = None

    # Creates a CMakeLists.txt files for each system within the module.
    def generate_cmake_files(self) -> None:
        global g_current_module
        g_current_module = self.name

        # Enter the module directory
        os.chdir(self.name)

        for system in self.systems:
            system.generate_cmake_file()

        # Return to parent project directory
        os.chdir('..')

'''
The main class that holds all the information about the project
on the highest level, i.e. which modules and subsystems exist within the project,
and other configuration parameters.
'''
class CProject:
    def __init__(self, name = 'project1', cppnamespace = '') -> None:
        # Initialize the name of the project
        self.name = name

        # Initialize the project c++ namespace
        if len(cppnamespace) > 0:
            self.cppnamespace = cppnamespace
        else:
            self.cppnamespace = name

        # Initialize the list of modules that the project contains
        self.modules: list[CModule] = []

    # Returns a CModule object given the module name
    def get_module(self, name) -> CModule:
        for mod in self.modules:
            if mod.name == name:
                return mod
        
        return None

    # Removes a module with the given name
    def remove_module(self, name) -> None:
        for mod in self.modules:
            if mod.name == name:
                self.modules.remove(mod)
                break

    # Generates C++ source files for each module and class
    def __generate_source_files(self) -> None:
        for mod in self.modules:
            mod.generate_source_files()

    # Generates the CMakeLists.txt files
    # for the project directory and contained modules.
    def __generate_cmake_files(self) -> None:
        for mod in self.modules:
            mod.generate_cmake_files()

        with open('CMakeLists.txt', 'w') as f:
            # CMake header
            f.write(CMAKE_HEADER_DEFINITION)

            # Project declaration
            f.write('project({})\n'.format(self.name))

            # Target definition
            f.write('set(TARGET_NAME {})\n\n'.format(self.name))

            # Include directories
            f.write('include_directories(\n')
            for mod in self.modules:
                f.write('\t"{}"\n'.format(mod.name))

            f.write(')\n\n')                

            # Add appropriate subdirectories and
            # keep track of the headers/sources to add.
            headers_and_sources = []

            for mod in self.modules:
                for system in mod.systems:
                    f.write('add_subdirectory({}/{})\n'.format(mod.name, system.name))
                    headers_and_sources.append('${{{}_HEADERS}}'.format(system.name))
                    headers_and_sources.append('${{{}_SOURCES}}'.format(system.name))

            # Gotta keep the spacing clean
            f.write('\n')

            # Create an executable target
            f.write('add_executable(\n\t${TARGET_NAME}\n\n')

            # Add headers and sources to the executable
            for item in headers_and_sources:
                f.write('\t{}\n'.format(item))

            # Add the main source file
            f.write('\n\tmain.cpp\n)\n\n')

    # Primary function for processing all
    # the project details and subsystems and
    # creating the physical project in the filesystem.
    def generate_project(self, target_dir) -> None:

        # Check for existance of at least one module
        if len(self.modules) < 1:
            return            

        global g_project_name

        # Set the project name global
        g_project_name = self.name

        # Get the absolute path (also fixes platform-dependent backslashes on windows)
        target_dir = os.path.abspath(target_dir)

        # Check if project parent directory exists
        if not os.path.isdir(target_dir):
            print('Error> target directory does not exist')
            return

        # Move into the target directory
        os.chdir(target_dir)

        # Check if project directory already exists
        if os.path.isdir(self.name):
            print('Error> project directory already exists')
            return

        # Create a new directory for the project
        os.mkdir(self.name)
        os.chdir(self.name)

        # Generate the main.cpp file
        with open('main.cpp', 'w') as f:
            f.write(DEFAULT_MAIN_FILE_SOURCE.format(self.name))

        # Generate project source files on the disk
        self.__generate_source_files()

        # Create required CMake files
        self.__generate_cmake_files()

        # Move back up to the parent directory (target dir)
        os.chdir(target_dir)

def render_project_table(console, project: CProject) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Project Name", style="bright", min_width=16)
    table.add_column("Modules", min_width=26)
    table.add_row(project.name)
    
    for mod in project.modules:
        table.add_row('', mod.name)

    console.print(table)
    console.print()

def render_module_table(console, module: CModule) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Module Name", style="bright", min_width=16)
    table.add_column("Systems",  min_width=26)
    table.add_row(module.name)
    
    for system in module.systems:
        table.add_row('', system.name)

    console.print(table)
    console.print()

def render_system_table(console, system: CSystem) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("System Name", style="bright", min_width=16)
    table.add_column("Classes",  min_width=26)
    table.add_row(system.name)
    
    for cppclass in system.classes:
        table.add_row('', cppclass.name)

    console.print(table)
    console.print()

def render_class_table(console, cppclass: CClass) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Class Name", style="bright", min_width=16)
    table.add_column("Functions",  min_width=26)
    table.add_column("Members Variables",  min_width=26)
    table.add_row(cppclass.name)

    # Creating a single list that contains
    # both public and private functions.
    all_fns = [fn.name for fn in cppclass.public_functions]
    all_fns.extend([fn.name for fn in cppclass.private_functions])

    # Creating a single list that contains
    # both public and private variables.
    all_vars = [var for var in cppclass.public_variables]
    all_vars.extend([var for var in cppclass.private_variables])

    greatest_member_count = max(len(all_fns), len(all_vars))

    for i in range(0, greatest_member_count):
        fn = ''
        fn_type = ''
        if i < len(all_fns):
            fn = all_fns[i]
            fn_type = '(public)'
            if i >= len(cppclass.public_functions):
                fn_type = '(private)'

        var = ''
        var_type = ''
        if i < len(all_vars):
            var = all_vars[i]
            var_type = '(public)'
            if i >= len(cppclass.public_variables):
                var_type = '(private)'

        table.add_row('', '{} {}'.format(fn, fn_type), '{} {}'.format(var, var_type))

    console.print(table)
    console.print()

def show_class_controls(console, cppclass: CClass):
    try:
        while True:
            render_class_table(console, cppclass)
            
            console.print('[1] Add function')
            console.print('[2] Remove function')
            console.print('[3] Add variable')
            console.print('[4] Remove variable')
            console.print('[5] Edit class name')
            console.print('[6] Return to system menu')
            console.print()

            combined_functions_list = cppclass.public_functions + cppclass.private_functions
            combined_variables_list = cppclass.public_variables + cppclass.private_variables

            user_cmd = int(Prompt.ask('Select option', choices=['1','2','3','4','5','6']))
            if user_cmd == 6: # return to project menu
               return

            # Adding a function to the class
            if user_cmd == 1:
                fn_type = Prompt.ask('public or private?', choices=['pub','priv'], default='pub')
                fn_return_type = Prompt.ask('return type', default='void')
                fn_name = Prompt.ask('name')
                fn_params = Prompt.ask('parameters (comma separated)', default='').replace(',\\s+', ',').split(',')
                docs = Prompt.ask('documentation', default='')
                
                fn = CFunction(fn_name, docs)
                fn.return_type = fn_return_type
                fn.params = fn_params

                combined_functions_list = cppclass.public_functions + cppclass.private_functions

                if fn_type == 'pub':
                    if fn_name not in [f.name for f in combined_functions_list] and len(fn_name) > 0:
                        cppclass.public_functions.append(fn)
                else:
                    if fn_name not in [f.name for f in combined_functions_list] and len(fn_name) > 0:
                        cppclass.private_functions.append(fn)

            # Remove function
            elif user_cmd == 2 and len(combined_functions_list) > 0:
                console.print('Enter function name', style='cyan', end='')
                fn_name = Prompt.ask('', choices=[fn.name for fn in combined_functions_list])
                cppclass.remove_function(fn_name)

            # Add variable
            if user_cmd == 3:
                var_type = Prompt.ask('public or private?', choices=['pub','priv'], default='pub')
                var_name = Prompt.ask('enter the variable type, name, and initial value in C++ syntax')

                if var_type == 'pub':
                    if var_name not in list(cppclass.public_variables + cppclass.private_variables) and len(var_name) > 0:
                        cppclass.public_variables.append(var_name)
                else:
                    if var_name not in list(cppclass.public_variables + cppclass.private_variables) and len(var_name) > 0:
                        cppclass.private_variables.append(var_name)

            # Remove variable
            elif user_cmd == 4 and len(combined_variables_list) > 0:
                console.print('Enter variable name', style='cyan', end='')
                var_name = Prompt.ask('', choices=[var.split()[1] for var in combined_variables_list])
                cppclass.remove_variable(var_name)

            # Edit module name
            elif user_cmd == 5:
                console.print('Enter new class name', style='cyan', end='')
                new_name = Prompt.ask('').replace(' ', '_')
                new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name) # remove all the non-alphanumeric characters
                cppclass.name = new_name

            clear_screen()
    except KeyboardInterrupt:
        return

def show_system_controls(console, system: CModule):
    try:
        while True:
            render_system_table(console, system)
            
            console.print('[1] Select class')
            console.print('[2] Add class')
            console.print('[3] Remove class')
            console.print('[4] Edit module name')
            console.print('[5] Return to module menu')
            console.print()

            user_cmd = int(Prompt.ask('Select option', choices=['1','2','3','4','5']))
            if user_cmd == 5: # return to project menu
               return

            # Select a class
            if user_cmd == 1 and len(system.classes) > 0:
                console.print('Enter class name', style='cyan', end='')
                class_choices = [cppclass.name for cppclass in system.classes]
                selected_class_name = Prompt.ask('', choices=class_choices)
                
                clear_screen()
                show_class_controls(console, system.get_class(selected_class_name))

            # Add class
            elif user_cmd == 2:
                console.print('New class name', style='cyan', end='')
                class_name = Prompt.ask('').replace(' ', '_')
                class_name = re.sub(r'[^a-zA-Z0-9_]', '', class_name) # remove all the non-alphanumeric characters

                if class_name not in [cppclass.name for cppclass in system.classes] and len(class_name) > 0:
                    system.classes.append(CClass(class_name))

            # Remove class
            elif user_cmd == 3 and len(system.classes) > 0:
                console.print('Enter class name', style='cyan', end='')
                class_name = Prompt.ask('', choices=[cppclass.name for cppclass in system.classes])
                system.remove_class(class_name)

            # Edit module name
            elif user_cmd == 4:
                console.print('Enter new system name', style='cyan', end='')
                new_name = Prompt.ask('').replace(' ', '_')
                new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name) # remove all the non-alphanumeric characters
                system.name = new_name

            clear_screen()
    except KeyboardInterrupt:
        return

def show_module_controls(console, module: CModule):
    try:
        while True:
            render_module_table(console, module)
            
            console.print('[1] Select system')
            console.print('[2] Add system')
            console.print('[3] Remove system')
            console.print('[4] Edit module name')
            console.print('[5] Return to project menu')
            console.print()

            user_cmd = int(Prompt.ask('Select option', choices=['1','2','3','4','5']))
            if user_cmd == 5: # return to project menu
               return

            # Select a class
            if user_cmd == 1 and len(module.systems) > 0:
                console.print('Enter system name', style='cyan', end='')
                class_choices = [system.name for system in module.systems]
                selected_system_name = Prompt.ask('', choices=class_choices)
                
                clear_screen()
                show_system_controls(console, module.get_system(selected_system_name))

            # Add class
            elif user_cmd == 2:
                console.print('New system name', style='cyan', end='')
                system_name = Prompt.ask('').replace(' ', '_')
                system_name = re.sub(r'[^a-zA-Z0-9_]', '', system_name) # remove all the non-alphanumeric characters

                if system_name not in [system.name for system in module.systems] and len(system_name) > 0:
                    module.systems.append(CSystem(system_name))

            # Remove class
            elif user_cmd == 3 and len(module.systems) > 0:
                console.print('Enter system name', style='cyan', end='')
                system_name = Prompt.ask('', choices=[system.name for system in module.systems])
                module.remove_system(system_name)

            # Edit module name
            elif user_cmd == 4:
                console.print('Enter new module name', style='cyan', end='')
                new_name = Prompt.ask('').replace(' ', '_')
                new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name) # remove all the non-alphanumeric characters
                module.name = new_name

            clear_screen()
    except KeyboardInterrupt:
        return

def show_project_controls(console, project: CProject) -> None:
    while True:
        try:
            render_project_table(console, project)
            
            console.print('[1] Select module')
            console.print('[2] Add module')
            console.print('[3] Remove module')
            console.print('[4] Edit project name')
            console.print('[5] Generate project')
            console.print('[6] Exit')
            console.print()

            user_cmd = int(Prompt.ask('Select option', choices=['1','2','3','4','5','6']))
            if user_cmd == 6: # exit
               if Confirm.ask('Are you sure you want to exit?'):
                   return

            # Select module
            if user_cmd == 1 and len(project.modules) > 0:
                console.print('Enter module name', style='cyan', end='')
                module_choices = [mod.name for mod in project.modules]
                selected_module_name = Prompt.ask('', choices=module_choices)
                
                clear_screen()
                show_module_controls(console, project.get_module(selected_module_name))

            # Add module
            elif user_cmd == 2:
                console.print('New module name', style='cyan', end='')
                mod_name = Prompt.ask('').replace(' ', '_')
                mod_name = re.sub(r'[^a-zA-Z0-9_]', '', mod_name) # remove all the non-alphanumeric characters

                if mod_name not in [mod.name for mod in project.modules] and len(mod_name) > 0:
                    project.modules.append(CModule(mod_name))

            # Remove module
            elif user_cmd == 3 and len(project.modules) > 0:
                console.print('Enter module name', style='cyan', end='')
                mod_name = Prompt.ask('', choices=[mod.name for mod in project.modules])
                project.remove_module(mod_name)

            # Edit project name
            elif user_cmd == 4:
                console.print('Enter new project name', style='cyan', end='')
                new_name = Prompt.ask('').replace(' ', '_')
                new_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name) # remove all the non-alphanumeric characters
                project.name = new_name

            # Generate the project
            elif user_cmd == 5:
                console.print('Enter target directory', style='cyan', end='')
                target_dir = Prompt.ask('').replace(' ', '_')

                project.generate_project(target_dir)

            clear_screen()

        except KeyboardInterrupt:
            console.print()
            if Confirm.ask('Are you sure you want to exit?'):
                return
            else:
                clear_screen()

def main() -> None:
    clear_screen()

    console = Console()
    console.print('\n', end='')
    console.print('Enter the project name', end='', style='cyan')

    project = CProject(Prompt.ask(''))
    clear_screen()

    show_project_controls(console, project)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

    print()
