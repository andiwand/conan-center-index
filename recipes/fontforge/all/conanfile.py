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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = ["libjpeg/9d", "libtiff/4.3.0", "libpng/1.6.37", "freetype/2.10.4", "giflib/5.2.1", "libxml2/2.9.12", "pango/1.49.3", "cairo/1.17.4", "spiro/20200505", "libuninameslist/20211114"]
    build_requires = ["gettext/0.21"]

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
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["ENABLE_GUI"] = False
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.definitions["ENABLE_PYTHON_SCRIPTING"] = False
        self._cmake.definitions["ENABLE_PYTHON_EXTENSION"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "fontforge"
        self.cpp_info.names["cmake_find_package_multi"] = "fontforge"
        self.cpp_info.names["pkgconfig"] = "libfontforge"
        self.cpp_info.libs = ["fontforge"]
