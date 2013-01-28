CC=gcc
EXT=.cpp
EXE=%(project_name)s
CFLAGS=-Wall -g0 -O3
INCLUDES=
LFLAGS=
LIBS=-lstdc++

SRCS=$(strip $(shell find *$(EXT) -type f))
OBJS=$(SRCS:$(EXT)=.o)

.PHONY: depend clean install

all: $(SRCS) $(EXE)
	@echo $(EXE) has been compiled

debug: CFLAGS+= -DDEBUG -g3 -O0
debug:
	@echo "Compiling Debug Version..."
debug: all

$(EXE): $(OBJS)
	@echo Compiling executable...
	$(CC) $(OBJS) $(LFLAGS) $(LIBS) -o $(EXE)

$(EXT).o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -rf *.o *~ $(EXE)

install:
	cp $(EXE) /usr/local/bin

depend: dep

dep: $(SRCS)
	makedepend $(INCLUDES) $^

# DO NOT DELETE THIS LINE -- make depend needs it
