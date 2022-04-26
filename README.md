# cbuilder

Whenever programmers, especially beginners, start a new project, they tend to jump straight to coding without thinking about the overall structure and architecture of the application or the library they are building. __cbuilder__ is a cross-platform C++ project generation tool that forces programmers to first think about the overall underlying structure of the project and encourages developers to think in a more abstract, high-level view of the project.<br/>
__cbuilder__ enforces the architecture where the project is consisted of modules, which further hold systems/components, which in turn actually have the C++ classes and actual code.<br/>
Additionally, __cbuilder__ allows you to generate cross-platform GUI project powered by ImGui. It generates the entry point and the boilerplate code to start your GUI app, so when you compile the project, it will already have a window created with a ClientApplication class provided for you to write your UI code in.

## Contents
- [Platform](#platform)
- [Requirements](#requirements)
- [Tutorial](#tutorial)
- [Contributing](#contributing)
- [License](#license)


## Platform

| Linux | Windows | MacOS |
|:--------:| :-: | :-: |
| ✓    | ✓ | ✓

[Note] On Windows, you would use .bat building and installation scripts, while on Linux and MacOS you would use .sh scripts.

## Requirements

* __Generating Console Projects__
    * None

<br/>

* __Generating GUI Projects__
    * __Windows__ 
        - `DirectX 11`

    <br/>

    * __MacOS__: 
        - `brew install glfw3`
        - `brew install GL`

    <br/>

    * __Linux__: 
        - `sudo apt-get install libglfw3 libglfw3-dev libgl1-mesa-dev`

    <br/>

## Tutorial

__cbuilder__ is very easy to use. Simply launch the script with `python3 cbuilder.py` from any directory and follow the steps.
<br/>

First you get to select the project type and name. cbuilder is able to generate either console app projects or cross-platform GUI projects powered by ImGui and native graphics APIs.

<img src="https://github.com/FlareCoding/cbuilder/raw/master/screenshots/project-type.png" width="500" height="191" /><br/>
<img src="https://github.com/FlareCoding/cbuilder/raw/master/screenshots/project-name.png" width="640" height="191" /><br/>

Next you will be greeted with your project's main menu. From there cbuilder forces you to think about your project in terms of modules and components/systems rather than diving in into specifics of the code. This enforces a more abstract and often better structure, and allows easily generating a lot of boiler plate code.

![tutorial_step_4](https://media.giphy.com/media/fwKLx07oVUYdfs4E3V/giphy.gif) <br/>

Finally, to generate the project on the filesystem, choose option 5: <br/>
![tutorial_step_5](https://media.giphy.com/media/xWzlbnqVHalTWMj6Eh/giphy.gif) <br/>

What this will do is create the appropriate directory structure including CMake files and some boilerplate plate for all your added classes and systems :)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[LGPL-2](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)