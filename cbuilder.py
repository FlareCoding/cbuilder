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

CONSOLE_MAIN_CPP = '''#include <iostream>

int main()
{
    std::cout << "Hello World!\\n";
    return 0;
}
'''

GUI_MAIN_CPP_UNIX = '''#define GL_SILENCE_DEPRECATION
#include <client/ui/ClientApplication.h>
#include <client/ui/imgui/imgui.h>
#include <client/ui/imgui/imgui_impl_glfw.h>
#include <client/ui/imgui/imgui_impl_opengl3.h>
#include <GLFW/glfw3.h> // Will drag system OpenGL headers
#include <stdio.h>
#include <memory>

using namespace {0}; // project namespace

static void glfw_error_callback(int error, const char* description)
{{
    fprintf(stderr, "Glfw Error %d: %s\\n", error, description);
}}

int main(int, char**)
{{
    // Setup window
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit())
        return 1;

    // Decide GL+GLSL versions
#if defined(IMGUI_IMPL_OPENGL_ES2)
    // GL ES 2.0 + GLSL 100
    const char* glsl_version = "#version 100";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
#elif defined(__APPLE__)
    // GL 3.2 + GLSL 150
    const char* glsl_version = "#version 150";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // Required on Mac
#else
    // GL 3.0 + GLSL 130
    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
    //glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // 3.0+ only
#endif

    // Create window with graphics context
    GLFWwindow* window = glfwCreateWindow(900, 600, "{0}", NULL, NULL);
    if (window == NULL)
        return 1;

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1); // Enable vsync

    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    //io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
    //io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;      // Enable Gamepad Controls

    // Setup Dear ImGui style
    ImGui::StyleColorsDark();

    // Setup Platform/Renderer backends
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init(glsl_version);

    // Load Fonts
    //io.Fonts->AddFontFromFileTTF("path//Roboto-Medium.ttf", 16.0f);
    //ImFont* font = io.Fonts->AddFontFromFileTTF("c:\Windows\Fonts\ArialUni.ttf", 18.0f, NULL, io.Fonts->GetGlyphRangesJapanese());
    //IM_ASSERT(font != NULL);
    //io.Fonts->AddFont(font);

    // Our state
    ImVec4 clear_color = ImVec4(0.1f, 0.1f, 0.1f, 1.0f);

    // Create the client application
    auto client = std::make_unique<client::ui::ClientApplication>();

    // Initialize the client application
    client->init();

    // Main loop
    while (!glfwWindowShouldClose(window))
    {{
        // Poll and handle events (inputs, window resize, etc.)
        // You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
        // - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application, or clear/overwrite your copy of the mouse data.
        // - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application, or clear/overwrite your copy of the keyboard data.
        // Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
        glfwPollEvents();

        // Start the Dear ImGui frame
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // Client UI code
        client->render();

        // Rendering
        ImGui::Render();
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(clear_color.x * clear_color.w, clear_color.y * clear_color.w, clear_color.z * clear_color.w, clear_color.w);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
    }}

    // Cleanup
    client->shutdown();

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}}
'''

GUI_MAIN_CPP_WINDOWS = '''#pragma comment(linker, "/SUBSYSTEM:windows /ENTRY:mainCRTStartup")
#include <imgui/imgui.h>
#include <imgui/imgui_impl_win32.h>
#include <imgui/imgui_impl_dx11.h>
#include <d3d11.h>
#include <tchar.h>
#include <memory>
#include <client/ui/ClientApplication.h>

using namespace {0};

// Data
static ID3D11Device*            g_pd3dDevice = NULL;
static ID3D11DeviceContext*     g_pd3dDeviceContext = NULL;
static IDXGISwapChain*          g_pSwapChain = NULL;
static ID3D11RenderTargetView*  g_mainRenderTargetView = NULL;

// Forward declarations
bool CreateDeviceD3D(HWND hWnd);
void CleanupDeviceD3D();
void CreateRenderTarget();
void CleanupRenderTarget();
LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

int main(int, char**)
{{
    WNDCLASSEX wc = {{ sizeof(WNDCLASSEX), CS_CLASSDC, WndProc, 0L, 0L, GetModuleHandle(NULL), NULL, NULL, NULL, NULL, _T("{0}"), NULL }};
    ::RegisterClassEx(&wc);
    HWND hwnd = ::CreateWindow(wc.lpszClassName, _T("{0}"), WS_OVERLAPPEDWINDOW, 100, 100, 900, 600, NULL, NULL, wc.hInstance, NULL);

    // Initialize Direct3D
    if (!CreateDeviceD3D(hwnd))
    {{
        CleanupDeviceD3D();
        ::UnregisterClass(wc.lpszClassName, wc.hInstance);
        return 1;
    }}

    ::ShowWindow(hwnd, SW_SHOWDEFAULT);
    ::UpdateWindow(hwnd);

    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;

    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;       // Enable Keyboard Controls
    io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;           // Enable Docking
    io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;         // Enable Multi-Viewport / Platform Windows

    // Setup ImGui style
    ImGui::StyleColorsDark();

    // When viewports are enabled we tweak WindowRounding/WindowBg so platform windows can look identical to regular ones.
    ImGuiStyle& style = ImGui::GetStyle();
    if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable)
    {{
        style.WindowRounding = 0.0f;
        style.Colors[ImGuiCol_WindowBg].w = 1.0f;
        style.WindowMinSize.x = 200.0f;
    }}

    // Setup Platform/Renderer backends
    ImGui_ImplWin32_Init(hwnd);
    ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);

    // Create the client application
    auto client = std::make_unique<client::ui::ClientApplication>();

    // Initialize the client application
    client->init();

    // Rendering and updating loop
    bool done = false;
    ImVec4 clear_color = ImVec4(0.1f, 0.1f, 0.1f, 1.0f);

    while (!done)
    {{
        // Poll and handle messages (inputs, window resize, etc.)
        // See the WndProc() function below for our to dispatch events to the Win32 backend.
        MSG msg;
        while (::PeekMessage(&msg, NULL, 0U, 0U, PM_REMOVE))
        {{
            ::TranslateMessage(&msg);
            ::DispatchMessage(&msg);
            if (msg.message == WM_QUIT)
                done = true;
        }}
        if (done)
            break;

        // Start the Dear ImGui frame
        ImGui_ImplDX11_NewFrame();
        ImGui_ImplWin32_NewFrame();
        ImGui::NewFrame();

        // Client UI code
        client->render();

        // Rendering
        ImGui::Render();
        const float clear_color_with_alpha[4] = {{ clear_color.x * clear_color.w, clear_color.y * clear_color.w, clear_color.z * clear_color.w, clear_color.w }};
        g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, NULL);
        g_pd3dDeviceContext->ClearRenderTargetView(g_mainRenderTargetView, clear_color_with_alpha);
        ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

        // Update and Render additional Platform Windows
        if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable)
        {{
            ImGui::UpdatePlatformWindows();
            ImGui::RenderPlatformWindowsDefault();
        }}

        g_pSwapChain->Present(1, 0); // Present with vsync
    }}

    // Cleanup
    client->shutdown();

    ImGui_ImplDX11_Shutdown();
    ImGui_ImplWin32_Shutdown();
    ImGui::DestroyContext();

    CleanupDeviceD3D();
    ::DestroyWindow(hwnd);
    ::UnregisterClass(wc.lpszClassName, wc.hInstance);

    return 0;
}}

// Helper functions
bool CreateDeviceD3D(HWND hWnd)
{{
    // Setup swap chain
    DXGI_SWAP_CHAIN_DESC sd;
    ZeroMemory(&sd, sizeof(sd));
    sd.BufferCount = 2;
    sd.BufferDesc.Width = 0;
    sd.BufferDesc.Height = 0;
    sd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    sd.BufferDesc.RefreshRate.Numerator = 60;
    sd.BufferDesc.RefreshRate.Denominator = 1;
    sd.Flags = DXGI_SWAP_CHAIN_FLAG_ALLOW_MODE_SWITCH;
    sd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    sd.OutputWindow = hWnd;
    sd.SampleDesc.Count = 1;
    sd.SampleDesc.Quality = 0;
    sd.Windowed = TRUE;
    sd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;

    UINT createDeviceFlags = 0;
    //createDeviceFlags |= D3D11_CREATE_DEVICE_DEBUG;
    D3D_FEATURE_LEVEL featureLevel;
    const D3D_FEATURE_LEVEL featureLevelArray[2] = {{ D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_0, }};
    if (D3D11CreateDeviceAndSwapChain(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, createDeviceFlags, featureLevelArray, 2, D3D11_SDK_VERSION, &sd, &g_pSwapChain, &g_pd3dDevice, &featureLevel, &g_pd3dDeviceContext) != S_OK)
        return false;

    CreateRenderTarget();
    return true;
}}

void CleanupDeviceD3D()
{{
    CleanupRenderTarget();
    if (g_pSwapChain) {{ g_pSwapChain->Release(); g_pSwapChain = NULL; }}
    if (g_pd3dDeviceContext) {{ g_pd3dDeviceContext->Release(); g_pd3dDeviceContext = NULL; }}
    if (g_pd3dDevice) {{ g_pd3dDevice->Release(); g_pd3dDevice = NULL; }}
}}

void CreateRenderTarget()
{{
    ID3D11Texture2D* pBackBuffer;
    g_pSwapChain->GetBuffer(0, IID_PPV_ARGS(&pBackBuffer));

    if (pBackBuffer)
    {{
        g_pd3dDevice->CreateRenderTargetView(pBackBuffer, NULL, &g_mainRenderTargetView);
        pBackBuffer->Release();
    }}
}}

void CleanupRenderTarget()
{{
    if (g_mainRenderTargetView) {{ g_mainRenderTargetView->Release(); g_mainRenderTargetView = NULL; }}
}}

#ifndef WM_DPICHANGED
#define WM_DPICHANGED 0x02E0 // From Windows SDK 8.1+ headers
#endif

// Forward declare message handler from imgui_impl_win32.cpp
extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

// Win32 message handler
// You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
// - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application, or clear/overwrite your copy of the mouse data.
// - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application, or clear/overwrite your copy of the keyboard data.
// Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{{
    if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam))
        return true;

    switch (msg)
    {{
    case WM_SIZE:
        if (g_pd3dDevice != NULL && wParam != SIZE_MINIMIZED)
        {{
            CleanupRenderTarget();
            g_pSwapChain->ResizeBuffers(0, (UINT)LOWORD(lParam), (UINT)HIWORD(lParam), DXGI_FORMAT_UNKNOWN, 0);
            CreateRenderTarget();
        }}
        return 0;
    case WM_SYSCOMMAND:
        if ((wParam & 0xfff0) == SC_KEYMENU) // Disable ALT application menu
            return 0;
        break;
    case WM_DESTROY:
        ::PostQuitMessage(0);
        return 0;
    case WM_DPICHANGED:
        if (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_DpiEnableScaleViewports)
        {{
            //const int dpi = HIWORD(wParam);
            //printf("WM_DPICHANGED to %d (%.0f%%)\n", dpi, (float)dpi / 96.0f * 100.0f);
            const RECT* suggested_rect = (RECT*)lParam;
            ::SetWindowPos(hWnd, NULL, suggested_rect->left, suggested_rect->top, suggested_rect->right - suggested_rect->left, suggested_rect->bottom - suggested_rect->top, SWP_NOZORDER | SWP_NOACTIVATE);
        }}
        break;
    }}
    return ::DefWindowProc(hWnd, msg, wParam, lParam);
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
        # if it doesn't exist already.
        if not os.path.exists(self.name):
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
        # if it doesn't exist already.
        if not os.path.exists(self.name):
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

        # Flag that specifies whether to include imgui into the project
        self.uses_imgui_ui_module = False

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

    # Creates the structure for
    # includes and libraries directories.
    def __create_includes_directory(self) -> None:
        # Create the includes directory
        os.mkdir('includes')

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

            # Definition for ImGui files
            if self.uses_imgui_ui_module:
                # Main ImGui sources
                f.write('''set(
    IMGUI_SOURCE_FILES

    client/ui/imgui/imgui.cpp
    client/ui/imgui/imgui_draw.cpp
    client/ui/imgui/imgui_tables.cpp
    client/ui/imgui/imgui_widgets.cpp
)

''')

                # Backend implementations
                f.write('''if (APPLE OR LINUX)
    set(
        IMGUI_BACKEND_FILES
        
        client/ui/imgui/imgui_impl_glfw.cpp
        client/ui/imgui/imgui_impl_opengl3.cpp
    )
else()
    set(
        IMGUI_BACKEND_FILES
        
        client/ui/imgui/imgui_impl_dx11.cpp
    )
endif()

''')

            # Entry point definition
            f.write('if (APPLE OR LINUX)\n')
            f.write('\tset(ENTRY_POINT_FILE main_unix.cpp)\n')
            f.write('else()\n')
            f.write('\tset(ENTRY_POINT_FILE main_windows.cpp)\n')
            f.write('endif()\n\n')

            # Include directories
            f.write('include_directories(\n')
            f.write('\t${CMAKE_SOURCE_DIR}\n')
            f.write('\tincludes/\n')
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

            # Add MacOS bundling options
            f.write('''if (APPLE)
    set(MACOSX_BUNDLE_ICON_FILE app-icon.icns)
    set(APP_ICON_PATH ${CMAKE_CURRENT_SOURCE_DIR}/resources/app-icon.icns)
    set_source_files_properties(${APP_ICON_PATH} PROPERTIES MACOSX_PACKAGE_LOCATION "Resources")

    set(PLATFORM_BUNDLING MACOSX_BUNDLE ${APP_ICON_PATH})
else()
    set(PLATFORM_BUNDLING )
endif()

''')

            # Create an executable target
            f.write('add_executable(\n\t${TARGET_NAME} ${PLATFORM_BUNDLING}\n\n')

            # Add headers and sources to the executable
            for item in headers_and_sources:
                f.write('\t{}\n'.format(item))

            f.write('\n')

            # Add ImGui implementation files
            # if the project is a GUI app.
            if self.uses_imgui_ui_module:
                f.write('\t${IMGUI_SOURCE_FILES}\n\n')
                f.write('\t${IMGUI_BACKEND_FILES}\n\n')

            # Add the main source file
            f.write('\t${ENTRY_POINT_FILE}\n)\n\n')

            # Link appropriate libraries for OSX
            # and set the correct MACOS_BUNDLE_XXX properties.
            f.write('''if (APPLE)
    find_library(COCOA_LIBRARY Cocoa)
    find_library(OpenGL_LIBRARY OpenGL)
    find_library(IOKIT_LIBRARY IOKit)
    find_library(COREVIDEO_LIBRARY CoreVideo)

    SET(EXTRA_LIBS ${COCOA_LIBRARY} ${OpenGL_LIBRARY} ${IOKIT_LIBRARY} ${COREVIDEO_LIBRARY})

    target_link_libraries(${PROJECT_NAME} glfw "-framework OpenGL")
    target_link_directories(${PROJECT_NAME} PRIVATE /opt/homebrew/lib)
    target_include_directories(${PROJECT_NAME} PRIVATE /usr/local/include opt/local/include /opt/homebrew/include)

    set_target_properties(${PROJECT_NAME} PROPERTIES
        MACOSX_BUNDLE True
        MACOSX_BUNDLE_GUI_IDENTIFIER cpp.app.${PROJECT_NAME}
        MACOSX_BUNDLE_BUNDLE_NAME ${PROJECT_NAME}
        MACOSX_BUNDLE_BUNDLE_VERSION "0.1"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "0.1"
    )
endif(APPLE)
''')

    # Sets up the imgui directory folder
    # and downloads latest imgui files.
    def __setup_imgui_files(self) -> None:
        os.chdir('client/ui')

        # Create a directory for imgui files
        os.mkdir('imgui')
        os.chdir('imgui')

        # Download the imgui files
        print('Downloading ImGui files...')
        os.system('curl -o imgui.h https://raw.githubusercontent.com/ocornut/imgui/docking/imgui.h')
        os.system('curl -o imgui.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/imgui.cpp')
        os.system('curl -o imconfig.h https://raw.githubusercontent.com/ocornut/imgui/docking/imconfig.h')
        os.system('curl -o imgui_internal.h https://raw.githubusercontent.com/ocornut/imgui/docking/imgui_internal.h')
        os.system('curl -o imstb_rectpack.h https://raw.githubusercontent.com/ocornut/imgui/docking/imstb_rectpack.h')
        os.system('curl -o imstb_textedit.h https://raw.githubusercontent.com/ocornut/imgui/docking/imstb_textedit.h')
        os.system('curl -o imstb_truetype.h https://raw.githubusercontent.com/ocornut/imgui/docking/imstb_truetype.h')
        os.system('curl -o imgui_draw.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/imgui_draw.cpp')
        os.system('curl -o imgui_tables.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/imgui_tables.cpp')
        os.system('curl -o imgui_widgets.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/imgui_widgets.cpp')
        os.system('curl -o imgui_impl_dx11.h https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_dx11.h')
        os.system('curl -o imgui_impl_dx11.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_dx11.cpp')
        os.system('curl -o imgui_impl_glfw.h https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_glfw.h')
        os.system('curl -o imgui_impl_glfw.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_glfw.cpp')
        os.system('curl -o imgui_impl_opengl3.h https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_opengl3.h')
        os.system('curl -o imgui_impl_opengl3.cpp https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_opengl3.cpp')
        os.system('curl -o imgui_impl_opengl3_loader.h https://raw.githubusercontent.com/ocornut/imgui/docking/backends/imgui_impl_opengl3_loader.h')

        # Move back up to ther project root directory
        os.chdir('../../../')

    # Set up GLFW directory and
    # download the library files.
    def __setup_glfw_files(self) -> None:
        # Enter the libs directory
        os.chdir('includes')

        # Make the GLFW directory
        os.mkdir('GLFW')
        os.chdir('GLFW')

        # Download the GLFW include files
        print('Downloading GLFW files...')
        os.system('curl -o glfw3.h https://raw.githubusercontent.com/glfw/glfw/master/include/GLFW/glfw3.h')

        # Move back up to the
        # project root directory.
        os.chdir('../../')

    # Setup resources directory with app-icon.icns
    def __setup_resources(self) -> None:
        # Create the resources directory
        os.mkdir('resources')
        os.chdir('resources')

        # Download the app-icon.icns
        # file for macos bundling.
        print('Download app-icon...')
        os.system('curl -o app-icon.icns https://raw.githubusercontent.com/FlareCoding/cbuilder/master/app-icon.icns')

        # Move back up to the
        # project root directory.
        os.chdir('..')

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
            print('Error> project already exists')
            return

        # Create a new directory for the project
        os.mkdir(self.name)
        os.chdir(self.name)

        # Setup includes directory
        self.__create_includes_directory()

        # Generate project source files on the disk
        self.__generate_source_files()

        # If the project has a GUI, setup
        # the imgui directory structure.
        if self.uses_imgui_ui_module:
            self.__setup_imgui_files()
            self.__setup_glfw_files()
            self.__setup_resources()

        # Generate the main.cpp file according
        # to the project type and platform.
        if self.uses_imgui_ui_module:
            # Unix version of the entry point
            with open('main_unix.cpp', 'w') as f:
                f.write(GUI_MAIN_CPP_UNIX.format(self.name))
            
            # Windows version of the entry point
            with open('main_windows.cpp', 'w') as f:
                f.write(GUI_MAIN_CPP_WINDOWS.format(self.name))

        else:
            # Default console version of main.cpp
            with open('main.cpp', 'w') as f:
                f.write(CONSOLE_MAIN_CPP)

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

def show_class_controls(console, cppclass: CClass) -> None:
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

def show_system_controls(console, system: CModule) -> None:
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

def show_module_controls(console, module: CModule) -> None:
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
                return

            clear_screen()

        except KeyboardInterrupt:
            console.print()
            if Confirm.ask('Are you sure you want to exit?'):
                return
            else:
                clear_screen()

def main() -> None:
    clear_screen()

    # Create a "rich" console object
    console = Console()

    # Let the user choose the application type for the project
    console.print('\n===== Application Type =====\n', style='yellow')
    console.print('[1] Console')
    console.print('[2] GUI')

    console.print('\nSelect the application type', end='', style='cyan')
    selected_type = int(Prompt.ask('', choices=['1','2']))
    
    project_type = 'Console'
    if selected_type == 2:
        project_type = 'GUI'

    console.print('\nEnter project name', end='', style='cyan')
    project = CProject(Prompt.ask(''))

    # If the user wants to make a GUI
    # application cbuilder should automatically
    # set up the client/ui module structure.
    if project_type == 'GUI':
        # Set the imgui flag of the project to true
        project.uses_imgui_ui_module = True

        # Module --> client
        client_module = CModule('client')

        # System --> ui
        ui_system = CSystem('ui')

        # Class --> ClientApplication
        client_app = CClass('ClientApplication')
        
        # Main public functionality of
        # the client application class.
        init_fn = CFunction('init', 'Initializes the client application and its resources.')
        shutdown_fn = CFunction('shutdown', 'Destroys the client application and frees up its resources.')
        render_fn = CFunction('render', 'Renders the application\'s user interface. Called every frame.')

        # Setup the class'es public functions
        client_app.public_functions.append(init_fn)
        client_app.public_functions.append(shutdown_fn)
        client_app.public_functions.append(render_fn)

        # Setup the system
        ui_system.classes.append(client_app)

        # Setup the module
        client_module.systems.append(ui_system)

        # Add the client module to the project
        project.modules.append(client_module)

    clear_screen()

    show_project_controls(console, project)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

    print()
