from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class SpiroConan(ConanFile):
    name = "spiro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fontforge/libspiro/"
    description = "Spiro is the creation of Raph Levien. It simplifies the drawing of beautiful curves."
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
    build_requires = ["autoconf/2.71", "automake/1.16.4", "libtool/2.4.6"]

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        pass

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True)

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = ["--enable-static=yes", "--enable-shared=no"] if not self.options.shared else ["--enable-static=no", "--enable-shared=yes"]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()
 
    def package(self):
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
