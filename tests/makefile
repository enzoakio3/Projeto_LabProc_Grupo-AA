CXX = g++
CXXFLAGS = -Wall -I/usr/local/include
LDFLAGS = -L/usr/local/lib
LIBS = -lwiringPi

TARGET = teste_buzzer
SRC = teste_buzzer.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS) $(LIBS)

run: $(TARGET)
	sudo ./$(TARGET)

clean:
	rm -f $(TARGET)