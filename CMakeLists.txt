cmake_minimum_required(VERSION 2.8.9)

project(SlicerScreenCapture)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/lassoan/SlicerScreenCapture")
set(EXTENSION_CATEGORY "Utilities")
set(EXTENSION_CONTRIBUTORS "Andras Lasso (PerkLab, Queen's")
set(EXTENSION_DESCRIPTION "Modules for recording screen catpure videos")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SlicerCapture.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerCapture/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ScreenCapture)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
