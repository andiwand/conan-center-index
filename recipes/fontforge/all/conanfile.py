from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class FontForgeConan(ConanFile):
    name = "fontforge"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fontforge/fontforge/"
    description = "Free (libre) font editor for Windows, Mac OS X and GNU+Linux"
    topics = "font"
    license = "GPL-3.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "native_scripting": [True, False],
        "python_scripting": [True, False],
        "python_extension": [True, False],
        "with_spiro": [True, False],
        "with_uninameslist": [True, False],
        "with_gif": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_readline": [True, False],
        "with_tiff": [True, False],
        "with_woff2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "native_scripting": True,
        "python_scripting": False,
        "python_extension": False,
        "with_spiro": False,
        "with_uninameslist": False,
        "with_gif": False,
        "with_jpeg": True,
        "with_png": True,
        "with_readline": False,
        "with_tiff": False,
        "with_woff2": False,
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        "spiro/20200505", "libuninameslist/20211114"
        self.requires("freetype/2.10.4")
        self.requires("libxml2/2.9.12")
        self.requires("pango/1.49.3")
        self.requires("cairo/1.17.2")
        self.requires("glib/2.70.1")
        if self.options.get_safe("with_jpeg"):
            self.requires("libjpeg/9d")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.3.0")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.37")
        if self.options.get_safe("with_gif"):
            self.requires("giflib/5.2.1")
        if self.options.get_safe("with_spiro"):
            self.requires("spiro/20200505")
        if self.options.get_safe("with_libuninameslist"):
            self.requires("libuninameslist/20211114")
    
    def build_requirements(self):
        self.build_requires("gettext/0.21")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # disable building fontforgeexe
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "add_subdirectory(fontforgeexe)",
            "#add_subdirectory(fontforgeexe)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["ENABLE_NATIVE_SCRIPTING"] = self.options.native_scripting
        self._cmake.definitions["ENABLE_PYTHON_SCRIPTING"] = self.options.python_scripting
        self._cmake.definitions["ENABLE_PYTHON_EXTENSION"] = self.options.python_extension
        self._cmake.definitions["ENABLE_LIBSPIRO"] = self.options.with_spiro
        self._cmake.definitions["ENABLE_LIBUNINAMESLIST"] = self.options.with_uninameslist
        self._cmake.definitions["ENABLE_LIBGIF"] = self.options.with_gif
        self._cmake.definitions["ENABLE_LIBJPEG"] = self.options.with_jpeg
        self._cmake.definitions["ENABLE_LIBPNG"] = self.options.with_png
        self._cmake.definitions["ENABLE_LIBREADLINE"] = self.options.with_readline
        self._cmake.definitions["ENABLE_LIBTIFF"] = self.options.with_tiff
        self._cmake.definitions["ENABLE_WOFF2"] = self.options.with_woff2

        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["ENABLE_GUI"] = False
        self._cmake.definitions["ENABLE_X11"] = False
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.definitions["ENABLE_CODE_COVERAGE"] = False
        self._cmake.definitions["ENABLE_DEBUG_RAW_POINTS"] = False
        self._cmake.definitions["ENABLE_FONTFORGE_EXTRAS"] = False
        self._cmake.definitions["ENABLE_MAINTAINER_TOOLS"] = False
        self._cmake.definitions["ENABLE_TILE_PATH"] = False
        self._cmake.definitions["ENABLE_WRITE_PFM"] = False
        self._cmake.definitions["ENABLE_SANITIZER"] = "none"
        self._cmake.definitions["ENABLE_FREETYPE_DEBUGGER"] = ""
        self._cmake.definitions["SPHINX_USE_VENV"] = False
        self._cmake.definitions["REAL_TYPE"] = "double"
        self._cmake.definitions["THEME"] = "tango"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", src=os.path.join(self._source_subfolder, "fontforge"), dst="include/fontforge")

        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fontforge"]
        self.cpp_info.includedirs.append(os.path.join("include", "fontforge"))

        self.cpp_info.names["cmake_find_package"] = "fontforge"
        self.cpp_info.names["cmake_find_package_multi"] = "fontforge"
        self.cpp_info.names["pkgconfig"] = "libfontforge"
