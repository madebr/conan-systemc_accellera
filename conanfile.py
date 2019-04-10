from conans import CMake, ConanFile, tools
from conans.errors import ConanException
from conans.client.tools.oss import detected_os
from conans.client.build.compiler_flags import architecture_flag
import os
import string


class LibnameConan(ConanFile):
    name = "systemc_accellera"
    version = "2.3.3"
    description = "SystemC is a set of C++ classes and macros which provide an event-driven simulation interface"
    topics = ("conan", "systemc", "hdl", "simulation", "verification", "system", )
    url = "https://github.com/bincrafters/conan-libname"
    homepage = "https://accellera.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Apache-2.0"

    exports = ["LICENSE.md", ]
    exports_sources = ["CMakeLists.txt", ]

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "pthread": [True, False],
        "virtual_bind": [True, False],
        "immediate_self_notifications": [True, False],
        "early_maxtime_creation": [True, False],
        "assertions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "pthread": False,
        "virtual_bind": True,
        "immediate_self_notifications": False,
        "early_maxtime_creation": True,
        "assertions": True,
    }

    generators = "cmake",

    _source_subfolder = "source_subfolder"

    @property
    def _cppstd(self):
        return "".join(filter(lambda c: c in string.digits, str(self.settings.compiler.cppstd)))

    def configure(self):
        if not self.settings.compiler.cppstd:
            raise ConanException("Need a valid cpp standard")

    def build_requirements(self):
        if detected_os() == "Windows":
            self.build_requires("msys2_installer/20161025@bincrafters/stable")

    def config_options(self):
        if self.settings.compiler == 'Visual Studio' or self.options.shared:
            del self.options.fPIC

    def package_id(self):
        # Alias gnu98 and 98, gnu11 and 11, etc.
        self.info.settings.compiler.cppstd = self._cppstd

    def source(self):
        source_url = "https://accellera.org/images/downloads/standards/systemc/systemc-{}.tar.gz".format(self.version)
        tools.get(source_url, sha256="5781b9a351e5afedabc37d145e5f7edec08f3fd5de00ffeb8fa1f3086b1f7b3f")
        extracted_dir = "systemc-{}".format(self.version)

        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _extra_defines(self):
        defines = []
        if not self.options.virtual_bind:
            defines.append("SC_DISABLE_VIRTUAL_BIND")
        if self.options.immediate_self_notifications:
            defines.append("SC_ENABLE_IMMEDIATE_SELF_NOTIFICATION")
        if self.options.early_maxtime_creation:
            defines.append("SC_ENABLE_EARLY_MAXTIME_CREATION")
        return defines

    def build(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_COPYRIGHT_MESSAGE"] = True
        cmake.definitions["ENABLE_PTHREADS"] = self.options.pthread
        cmake.definitions["DISABLE_VIRTUAL_BIND"] = not self.options.virtual_bind
        cmake.definitions["ENABLE_IMMEDIATE_SELF_NOTIFICATIONS"] = self.options.immediate_self_notifications
        cmake.definitions["ENABLE_EARLY_MAXTIME_CREATION"] = self.options.early_maxtime_creation
        cmake.definitions["ENABLE_ASSERTIONS"] = self.options.assertions
        cmake.definitions["CMAKE_CXX_STANDARD"] = self._cppstd
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions["CMAKE_ASM_FLAGS"] = architecture_flag(compiler=self.settings.compiler, os=self.settings.os,
                                                                 arch=self.settings.arch)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines = self._extra_defines

        if self.options.pthread:
            self.cpp_info.libs.append("pthread")
