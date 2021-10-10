cmake_minimum_required(VERSION 3.16)
project(evegen)

set(CMAKE_CXX_STANDARD 14)

include("cmake/FindMariaDBClient.cmake")

include_directories(src)

find_package(Python 2.7 COMPONENTS Development REQUIRED)

add_executable(evegen
        src/db.cpp
        src/db.h
        src/devtools.cpp
        src/devtools.h
        src/main.cpp
        src/patch.cpp
        src/patch.h
        src/stb_c_lexer.h)

target_include_directories(evegen PRIVATE ${Python_INCLUDE_DIRS} ${MariaDBClient_INCLUDE_DIR})
target_link_libraries(evegen ${Python_LIBRARIES} ${MariaDBClient_LIBRARIES})

if (EXISTS "${Python_INCLUDE_DIRS}/Stackless")
    message(STATUS "Stackless Python installation detected, making include corrections")
    target_include_directories(evegen PRIVATE "${Python_INCLUDE_DIRS}/Stackless")
endif()
