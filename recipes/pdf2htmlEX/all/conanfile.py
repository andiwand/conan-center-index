from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class Pdf2htmlEXConan(ConanFile):
    name = "pdf2htmlEX"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pdf2htmlEX/pdf2htmlEX/"
    description = "Convert PDF to HTML without losing text or format."
    topics = "pdf", "html", "converter"
    license = "GPL-3.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,

        "glib*:with_mount": False,
        "glib*:with_selinux": False,

        "cairo*:with_xlib": False,
        "cairo*:with_xlib_xrender": False,
        "cairo*:with_xcb": False,
        "cairo*:with_opengl": False,

        "pango*:with_xft": False,

        "poppler:shared": False,
        "poppler*:fPIC": True,
        "poppler:cpp": False,
        "poppler:fontconfiguration": "fontconfig",
        "poppler:with_cairo": True,
        "poppler:splash": True,
        "poppler:with_glib": True,
        "poppler:with_gobject_introspection": False,
        "poppler:with_qt": False,
        "poppler:with_gtk": False,
        "poppler:with_openjpeg": True,
        "poppler:with_lcms": False,
        "poppler:with_libjpeg": "libjpeg",
        "poppler:with_png": True,
        "poppler:with_nss": False,
        "poppler:with_tiff": False,
        "poppler:with_libcurl": False,
        "poppler:with_zlib": True,
        "poppler:float": False,

        "fontforge:shared": False,
        "fontforge*:fPIC": True,
        "fontforge:native_scripting": True,
        "fontforge:python_scripting": False,
        "fontforge:python_extension": False,
        "fontforge:with_spiro": False,
        "fontforge:with_uninameslist": False,
        "fontforge:with_gif": False,
        "fontforge:with_jpeg": True,
        "fontforge:with_png": True,
        "fontforge:with_readline": False,
        "fontforge:with_tiff": False,
        "fontforge:with_woff2": False,
    }
    requires = [
        "poppler/0.89.0",
        "fontforge/20200314",
        "cairo/1.17.2",
        "glib/2.65.3",
        "freetype/2.11.1",
    ]

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package", "pkg_config"
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(source_folder=os.path.join(self._source_subfolder, "pdf2htmlEX"), build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", src=os.path.join(self._source_subfolder, "pdf2htmlEX", "src"), dst="include/pdf2htmlEX")

        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pdf2htmlEX"]
        self.cpp_info.includedirs.append(os.path.join("include", "pdf2htmlEX"))

        self.cpp_info.names["cmake_find_package"] = "pdf2htmlEX"
        self.cpp_info.names["cmake_find_package_multi"] = "pdf2htmlEX"
        self.cpp_info.names["pkgconfig"] = "libpdf2htmlEX"
