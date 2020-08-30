from enigma import *


def print_options(options):
    for i, v in enumerate(options):
        name = v[0]
        print("{0}. {1}".format(i+1, name))
        
        
def ask_input(text, maxcount):
    while True:
        try:
            value = input(text)
            value = int(value) - 1
            if value < 0 or value >= maxcount:
                print("Value cannot be smaller than 1 or bigger than {0}".format(maxcount))
            else:
                break
        except:
            print("Invalid input, needs to be a number!")
    
    return value 
    
    
class EnigmaPreset(object):
    def __init__(self):
        self.reflectors = []
        self.rotors = []
        self.stators = []
        self.required_rotors = 3
        self.rotatable_reflector = False 
        
        self._reflector_choice = None 
        self._rotors_choice = [] 
        self._stator_choice = None
        

    def ask_multiple_input(self, text, maxcount, required_count=None):
        while True:
            values = input(text).split(" ")
            for i in range(values.count("")):
                values.remove("") 
            
            if required_count is not None and len(values) != required_count:
                print("You need to put in exactly {0} values separated by a space!".format(required_count))
            else:
                newvalues = []
                values_correct = True 
                
                for value in values:
                    try:
                        value = int(value) - 1
                    except:
                        print("Invalid input, needs to be a number!")
                        values_correct = False 
                    else:
                        if value < 0 or value >= maxcount:
                            print("Value cannot be smaller than 1 or bigger than {0}".format(maxcount))
                            values_correct = False 
                        else:
                            newvalues.append(value)
                    
                if values_correct:
                    break 
        
        return newvalues 
    
    def ask_options_reflector(self):
        if len(self.reflectors) == 1:
            self._reflector_choice = 0
            return 
            
        print_options(self.reflectors)
        choice = ask_input("Choose reflector: ", len(self.reflectors))
        
        self._reflector_choice = choice 
    
    def ask_options_stator(self):
        if len(self.stators) == 1:
            self._stator_choice = 0
            return 
            
        print_options(self.stators)
        choice = ask_input("Choose stator: ", len(self.stators))
        
        self._reflector_choice = choice 
    
    def ask_options_rotors(self):
        print_options(self.rotors)
        choice = self.ask_multiple_input("Choose {0} rotors (separated by spaces): ".format(self.required_rotors), 
            len(self.rotors), self.required_rotors)
        
        self._rotors_choice = choice 
        
        
    def create(self):
        ref = self.reflectors[self._reflector_choice][1]
        rotors = []
        for choice in self._rotors_choice:
            rotors.append(self.rotors[choice][1])
        stator = self.stators[self._stator_choice][1]
        
        return EnigmaMachine(ref, rotors, stator, rotatable_reflector=self.rotatable_reflector)
        
        
class EnigmaM3Preset(EnigmaPreset):
    def __init__(self):
        super().__init__()
        self.reflectors = [("Reflector B", refb), ("Reflector C", refc)]
        self.rotors = [("Rotor I", rotor(1)), ("Rotor II", rotor(2)),
                        ("Rotor III", rotor(3)), ("Rotor IV", rotor(4)),
                        ("Rotor V", rotor(1))]
        self.stators = [("ETW Army", etw_army)]


class EnigmaM4Preset(EnigmaPreset):
    def __init__(self):
        super().__init__()
        self.reflectors = [("Reflector B Thin", refbthin), ("Reflector C Thin", refcthin)]
        self.rotors = [("Rotor I", rotor(1)), ("Rotor II", rotor(2)),
                        ("Rotor III", rotor(3)), ("Rotor IV", rotor(4)),
                        ("Rotor V", rotor(5)), ("Rotor VI", rotor(6)),
                        ("Rotor VII", rotor(7)), ("Rotor VIII", rotor(8)),
                        ("Rotor VII", rotor(7)), ("Rotor VIII", rotor(8))]
        self.stators = [("ETW Army", etw_army)]


class EnigmaRocketPreset(EnigmaPreset):
    def __init__(self):
        super().__init__()
        self.reflectors = [("Reflector B", refb), ("Reflector C", refc)]
        self.rotors = [("Rotor I", rotor(1)), ("Rotor II", rotor(2)),
                        ("Rotor III", rotor(3)), ("Rotor IV", rotor(4)),
                        ("Rotor V", rotor(1))]
        self.stators = [("ETW Army", etw_army)]




enigmas = [("Enigma M3", EnigmaM3Preset)]

if __name__ == "__main__":  
    stop = False 
    while not stop:
        print_options(enigmas)
        choice = ask_input("Choose an Enigma: ", len(enigmas))
        
        enigma_name, enigma_cls = enigmas[choice]
        enigma = enigma_cls()
        print("Chosen:", enigma_name)
        print("Configure the Enigma:")
        enigma.ask_options_reflector()
        enigma.ask_options_rotors()
        enigma.ask_options_stator()
        
        enigma_machine = enigma.create()
        print("Everything is set, you can now type or use commands.")
        run = True 
        while run:
            in_text = input()
            
            if in_text.startswith(":"):
                # command
                args = in_text.split(" ")
                cmd = args[0]
                if cmd == ":state":
                    print("Enigma Rotor State: ", enigma_machine.get_rotor_state())
                elif cmd == ":setstate":
                    state = args[1]
                    enigma_machine.set_rotor_state(state)
                    print("Set Enigma Rotor State to", state)
                elif cmd == ":setrings":
                    values = args[1:]
                    if values[0].isdigit():
                        ringsettings = [int(x)-1 for x in values]
                    else:
                        ringsettings = offsets("".join(values).upper())
                    
                    enigma_machine.set_ring(*ringsettings)
                    
                elif cmd == ":changerotors":
                    enigma = enigma_cls()
                    print("Configure the Enigma:")
                    enigma.ask_options_reflector()
                    enigma.ask_options_rotors()
                    enigma.ask_options_stator()
                    
                    enigma_machine = enigma.create()
                elif cmd == ":quit":
                    run = False 
                    stop = True 
            else:
                print(enigma_machine.encode(in_text.upper()))
            
    