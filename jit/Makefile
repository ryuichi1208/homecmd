CC = gcc
CFLAGS = -Wall -Wextra
TARGET = simple_compiler
TEST_SOURCE = hello.c
TEST_ASM = hello_asm_exe
TEST_C = hello_exe

all: $(TARGET)

$(TARGET): simple_compiler.c
	$(CC) $(CFLAGS) -o $@ $<

test: $(TARGET) test_asm test_c

test_asm: $(TARGET)
	./$(TARGET) $(TEST_SOURCE)
	./$(TEST_ASM)

test_c: $(TARGET)
	./$(TARGET) $(TEST_SOURCE)
	./$(TEST_C)

clean:
	rm -f $(TARGET) $(TEST_ASM) $(TEST_C) *.o *.asm *_generated.c

.PHONY: all test test_asm test_c clean
