CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
TARGET = cs2cpp_test
SOURCES = CSharpToCppTransformer.cpp main.cpp
OBJECTS = $(SOURCES:.cpp=.o)

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(OBJECTS) $(TARGET)

# Dependencies
CSharpToCppTransformer.o: CSharpToCppTransformer.cpp CSharpToCppTransformer.h
main.o: main.cpp CSharpToCppTransformer.h