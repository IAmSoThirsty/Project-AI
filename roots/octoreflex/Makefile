# Yggdrasil OctoReflex build
CC = clang
BPF_CFLAGS = -O2 -target bpf -c -g

SOURCES = src/dns_intercept.bpf.c src/hardened_intercept.bpf.c
OBJECTS = $(SOURCES:.c=.o)

all: $(OBJECTS)

%.o: %.c
	$(CC) $(BPF_CFLAGS) -o $@ $<

load: hardened_intercept.o
	sudo bpftool prog load src/hardened_intercept.o /sys/fs/bpf/octoreflex
	sudo bpftool net attach ingress src/hardened_intercept dev eth0

clean:
	rm -f src/*.o *.o
