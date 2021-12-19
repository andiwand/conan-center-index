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
    }
    requires = [
        # poppler requires
        #"freetype/2.10.4", "fontconfig/2.13.93", "cairo/1.17.4", "libjpeg/9d", "libpng/1.6.37", "boost/1.76.0", "zlib/1.2.11",
        "poppler/0.89.0",
        # fontforge requires
        "fontforge/20200314",
        # pdf2htmlEX requires
        "cairo/1.17.4",
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
                  destination=os.path.join(self._source_subfolder, "pdf2htmlEX"), strip_root=True)
        for dependency in self.conan_data["dependencies"][self.version]:    
            tools.get(**self.conan_data["dependencies"][self.version][dependency],
                    destination=os.path.join(self._source_subfolder, dependency), strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.configure(source_folder=os.path.join(self._source_subfolder, "pdf2htmlEX", "pdf2htmlEX"), build_folder=self._build_subfolder)
        return self._cmake

    def _build_poppler(self):
        cmake = CMake(self)

        cmake.definitions["ENABLE_UNSTABLE_API_ABI_HEADERS"] = False
        cmake.definitions["BUILD_GTK_TESTS"] = False
        cmake.definitions["BUILD_QT5_TESTS"] = False
        cmake.definitions["BUILD_CPP_TESTS"] = False
        cmake.definitions["ENABLE_SPLASH"] = True
        cmake.definitions["ENABLE_UTILS"] = False
        cmake.definitions["ENABLE_CPP"] = False
        cmake.definitions["ENABLE_GLIB"] = True
        cmake.definitions["ENABLE_GOBJECT_INTROSPECTION"] = False
        cmake.definitions["ENABLE_GTK_DOC"] = False
        cmake.definitions["ENABLE_QT5"] = False
        cmake.definitions["ENABLE_LIBOPENJPEG"] = "none"
        cmake.definitions["ENABLE_CMS"] = "none"
        cmake.definitions["ENABLE_DCTDECODER"] = "libjpeg"
        cmake.definitions["ENABLE_LIBCURL"] = False
        cmake.definitions["ENABLE_ZLIB"] = True
        cmake.definitions["ENABLE_ZLIB_UNCOMPRESS"] = False
        cmake.definitions["ENABLE_JPEG"] = True
        cmake.definitions["USE_FLOAT"] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = False
        cmake.definitions["RUN_GPERF_IF_PRESENT"] = False
        cmake.definitions["EXTRA_WARN"] = False
        cmake.definitions["WITH_JPEG"] = True
        cmake.definitions["WITH_PNG"] = True
        cmake.definitions["WITH_TIFF"] = False
        cmake.definitions["WITH_NSS3"] = False
        cmake.definitions["WITH_Cairo"] = True
        
        cmake.configure(source_folder=os.path.join(self._source_subfolder, "poppler"),
            build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def _build_fontforge(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = False
        cmake.configure(source_folder=os.path.join(self._source_subfolder, "fontforge"),
            build_folder=os.path.join(self._build_subfolder, "fontforge"))
        cmake.build()
        cmake.install()

    def build(self):
        #self._build_poppler()
        #self._build_fontforge()

        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "pdf2htmlEX"
        self.cpp_info.names["cmake_find_package_multi"] = "pdf2htmlEX"
        self.cpp_info.names["pkgconfig"] = "libpdf2htmlEX"
        self.cpp_info.libs = ["pdf2htmlEX"]
