#AC_INIT([FULL-PACKAGE-NAME], [VERSION], [BUG-REPORT-ADDRESS], [TAR-NAME], [URL])
AC_INIT([evegen], [0.1.0], [nick@maximumtwang.com], [evegen], [http://www.maximumtwang.com])

# Force autoconf to be at least this version number.
AC_PREREQ([2.68])

# Put autotools auxiliary files in a subdir, so they don't clutter top dir.
# I am not actually doing this at the moment because there should be relatively
# little in the top directory anyway.
#AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([m4])
#AC_PROG_CC([gcc-4.9 gcc cc])
AC_PROG_CXX([g++-4.9 g++ c++])

# Enable "automake" to simplify creating makefiles. foreign relaxes some GNU
# checks. -Wall and -Werror are instructions to Automake, not gcc.
# Because this is a non-recursive automake, we use subdir-objects to tell
# automake to create objects such as .o in sub-directories rather than placing
# all artifacts in the top level directory.
AM_INIT_AUTOMAKE([subdir-objects foreign -Wall -Werror])

# These are the files to be generated.
AC_CONFIG_FILES([Makefile])

# Safety check - list a source file that wouldn't be in other directories.
AC_CONFIG_SRCDIR([src/main.cpp])
AC_CONFIG_SRCDIR([src/patch.cpp])
AC_CONFIG_SRCDIR([src/db.cpp])
AC_CONFIG_SRCDIR([src/devtools.cpp])

# Put configuration results in this file for us to #include in our program.
AC_CONFIG_HEADERS([config.h])

# Check for libraries, headers, data etc here.

#AC_CHECK_LIB([python2.7], [Py_Initialize], [], [AC_MSG_ERROR([Python 2.7 was not found])])
AM_PATH_PYTHON(,[PYTHON_FOUND=true],[PYTHON_FOUND=false])
PYTHON_CPPFLAGS=
PYTHON_LDFLAGS=
AX_PYTHON_DEVEL

WITH_MYSQL()
MYSQL_USE_CLIENT_API()
MYSQL_SUBST()

# Last line: actually generate all required output files.
AC_OUTPUT
