EXTRA_DIST = src/*.h patches src/*.def
bin_PROGRAMS = evegen
evegen_SOURCES = src/main.cpp src/patch.cpp src/db.cpp src/devtools.cpp
evegen_CXXFLAGS = -Wall -pedantic -std=c++11 $(PYTHON_CPPFLAGS) @MYSQL_CFLAGS@
evegen_LDFLAGS = -lpython2.7 @MYSQL_LDFLAGS@
evegen_LIBS = @MYSQL_LIBS@

