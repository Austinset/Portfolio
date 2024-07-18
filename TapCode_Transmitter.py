import time
import sys
from pcdr.unstable.flow import OsmoSingleFreqTransmitter


long = 3   # Long Hum length in seconds (Preamble)
shortS = 1.75    # 'Section' Short Hum length in seconds
shortL = 1    # 'Letter' Short Hum length in seconds

tap_code = {
    'A': (1, 1), 'B': (1, 2), 'C': (1, 3), 'D': (1, 4), 'E': (1, 5), 'F': (1, 6),
    'G': (2, 1), 'H': (2, 2), 'I': (2, 3), 'J': (2, 4), 'K': (2, 5), ' ': (2, 6),
    'L': (3, 1), 'M': (3, 2), 'N': (3, 3), 'O': (3, 4), 'P': (3, 5), '.': (3, 6),
    'Q': (4, 1), 'R': (4, 2), 'S': (4, 3), 'T': (4, 4), 'U': (4, 5), '!': (4, 6),
    'V': (5, 1), 'W': (5, 2), 'X': (5, 3), 'Y': (5, 4), 'Z': (5, 5), ',': (5, 6)
}

answer = input("What word would you like to make? ").upper()

for letter in answer:
    if letter not in tap_code.keys():
        print("Only Latin letters (A-Z) are supported.")
        sys.exit()

transmitter = OsmoSingleFreqTransmitter("hackrf=0", 6e6)
transmitter.start()
print("Transmission started.")
on_gain = 35
off_gain = 0
transmitter.set_if_gain(on_gain)

# Function to transmit hums
def transmit_hum(hum_duration):
    print("On.")
    transmitter.set_if_gain(on_gain)
    print(f"Waiting {hum_duration} seconds.")
    time.sleep(hum_duration)
    print("Off.")
    transmitter.set_if_gain(off_gain)

# Transmit the word
for letter in answer:
    transmit_hum(long)
    time.sleep(1)
    section, letter_position = tap_code[letter]
    print(f"Section: {section}. Letter: {letter_position}")
    # Short hum for section
    for _ in range(section):
        transmit_hum(shortS)
        time.sleep(.25)
    time.sleep(.5)
    for _ in range(letter_position):
        transmit_hum(shortL)
        time.sleep(.25) 
    # Short hum for letter
    
  
print("Transmission complete.") 
sys.exit()

