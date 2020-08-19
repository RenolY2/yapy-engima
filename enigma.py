from io import StringIO

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
I = 1
II = 2
III = 3
IV = 4
V = 5
VI = 6
VII = 7
VIII = 8

def offset(letter):
    return ALPHABET.find(letter)


class RotorPiece(object):
    def __init__(self, in_map, out_map, ring_setting, turnover_at, turnover_at2=None):
        self.in_map = in_map 
        self.out_map = out_map 
        self.ring_setting = ring_setting
        self.turnover_at = turnover_at # what is visible in window when notch is engaged 
        self.turnover_at2 = turnover_at2 # second notch for Kriegsmarine Rotors 
        self.rotation = 0
        
    def advance(self):
        self.rotation = (self.rotation+1) % len(self.in_map)
    
    def advance_cw(self):
        if self.rotation == 0:
            self.rotation = len(self.in_map)-1
        else:
            self.rotation = (self.rotation-1) % len(self.in_map)
    
    def rotate(self, position):
        if not isinstance(position, int):
            position = self.in_map.find(position)
        self.rotation = position % len(self.in_map)

    def encode(self, letter):
        #ring setting acts like a inverse offset
        ring_offset = len(self.in_map) - self.ring_setting 
        pos = (self.in_map.find(letter) + self.rotation + ring_offset) % len(self.in_map)
        
        
        #print(pos)
        outpos = self.in_map.find(self.out_map[pos])
        #print("in:", letter, "intermediate:", self.in_map[pos], "maps to", self.out_map[pos])
        outpos = (outpos + (len(self.in_map) - self.rotation) + self.ring_setting ) % len(self.in_map)
        return self.in_map[outpos]
        
    def encode_back(self, letter):
        ring_offset = len(self.in_map) - self.ring_setting 
        pos = (self.in_map.find(letter) + self.rotation + ring_offset) % len(self.in_map)
        
        
        #print(pos)
        inpos = self.out_map.find(self.in_map[pos])
        #print("in:", letter, "intermediate:", self.in_map[pos], "maps to", self.out_map[pos])
        inpos = (inpos + (len(self.in_map) - self.rotation) + self.ring_setting ) % len(self.in_map)
        return self.in_map[inpos]
        
    def turnover(self):
        return self.rotation == self.turnover_at or self.rotation == self.turnover_at2


class NonRotatableRotor(RotorPiece):
    def advance(self):
        # The fourth rotor does not step during the encryption or decryption process
        pass 
        
    def turnover(self):
        return False 
    
    
class Stator(NonRotatableRotor):
    def __init__(self, in_map, out_map):
        super().__init__(in_map, out_map, 0, None)


class Reflector(RotorPiece):
    def __init__(self, in_map, out_map, ring_setting=0, turnover_at=None, turnover_at2=None):
        super().__init__(in_map, out_map, ring_setting, turnover_at, turnover_at2)


class EnigmaMachine(object):
    def __init__(self, reflector=None, rotors=[], etw=None, plugboard=None, rotatable_reflector=False):
        self.rotors = []
        for rotor in rotors:
            self.rotors.append(rotor)
        self.etw = etw 
        self.reflector = reflector 
        self.plugboard = {}
        if plugboard is not None:
            for a,b in plugboard:
                assert a not in self.plugboard
                assert b not in self.plugboard
                
                self.plugboard[a] = b
                self.plugboard[b] = a
        
        self.rotatable_reflector = rotatable_reflector
    
    def _plug(self, letter):
        if letter in self.plugboard:
            return self.plugboard[letter]
        else:
            return letter 
    
    def push_key(self, letter):
        if letter == " ":
            return letter
        # Plugboard
        letter = self._plug(letter)
        
        # rotate all rotors 
        curr_rotor_steps = True 
        next_rotor_steps = False 
        
        if self.etw is not None:
            letter = self.etw.encode(letter)
            
        for i, rotor in enumerate(reversed(self.rotors)):
            next_rotor_steps = rotor.turnover()
            if curr_rotor_steps:
                rotor.advance()
            curr_rotor_steps = next_rotor_steps
        
        # Encode letter
        for rotor in reversed(self.rotors):
            letter = rotor.encode(letter)
        
        # Reflect letter 
        letter = self.reflector.encode(letter)
            
        # Encode letter back 
        for rotor in self.rotors:
            letter = rotor.encode_back(letter)
        
        if self.etw is not None:
            letter = self.etw.encode_back(letter)
            
        
        # Plugboard again
        letter = self._plug(letter)
        
        return letter 
    
    def encode(self, text):
        result = StringIO()
        
        for letter in text:
            result.write(self.push_key(letter))
        
        return result.getvalue()
    
    def set_ring(self, *args):
        if self.rotatable_reflector:
            self.reflector.ring_setting = args[0]
            
            for i, val in enumerate(args[1:]):
                self.rotors[i].ring_setting = val
        else:
            for i, val in enumerate(args):
                self.rotors[i].ring_setting = val
    
    def set_rotor_state(self, state):
        if not self.rotatable_reflector:
            assert len(state) == len(self.rotors)
                
            for i, rotor in enumerate(self.rotors):
                rotor.rotation = offset(state[i])

        else:
            assert len(state) == len(self.rotors)+1
            self.reflector.rotation = offset(state[0])
                
            for i, rotor in enumerate(self.rotors):
                rotor.rotation = offset(state[i+1])
    
    def get_rotor_state(self):
        if not self.rotatable_reflector:
            return "".join(ALPHABET[rotor.rotation] for rotor in self.rotors)
        else:
            return ALPHABET[self.reflector.rotation] + "".join(ALPHABET[rotor.rotation] for rotor in self.rotors)


def rotor(num, off=offset("A")):
    if num == 1:
        return RotorPiece(ALPHABET, "EKMFLGDQVZNTOWYHXUSPAIBRCJ", off, offset("Q"))
    elif num == 2:
        return RotorPiece(ALPHABET, "AJDKSIRUXBLHWTMCQGZNPYFVOE", off, offset("E"))
    elif num == 3: 
        return RotorPiece(ALPHABET, "BDFHJLCPRTXVZNYEIWGAKMUSQO", off, offset("V"))
    elif num == 4:
        return RotorPiece(ALPHABET, "ESOVPZJAYQUIRHXLNFTGKDCMWB", off, offset("J"))
    elif num == 5:
        return RotorPiece(ALPHABET, "VZBRGITYUPSDNHLXAWMJQOFECK", off, offset("Z"))
    elif num == 6:
        return RotorPiece(ALPHABET, "JPGVOUMFYQBENHZRDKASXLICTW", off, offset("Z"), offset("M"))
    elif num == 7:
        return RotorPiece(ALPHABET, "NZJHGRCXMYSWBOUFAIVLPEKQDT", off, offset("Z"), offset("M"))
    elif num == 8:
        return RotorPiece(ALPHABET, "FKQHTLXOCBJSPDZRAMEWNIUYGV", off, offset("Z"), offset("M"))
    else:
        raise RuntimeError("Unsupported rotor: {0}".format(num))
        
        
if __name__ == "__main__":
    refa = Reflector(ALPHABET, "EJMZALYXVBWFCRQUONTSPIKHGD") # A retail enigma rotor?
    refb = Reflector(ALPHABET, "YRUHQSLDPXNGOKMIEBFZCWVJAT")
    refc = Reflector(ALPHABET, "FVPJIAOYEDRZXWGCTKUQSBNMHL")
    
    refbthin = Reflector(ALPHABET, "ENKQAUYWJICOPBLMDXZVFTHRGS")
    refcthin = Reflector(ALPHABET, "RDOBJNTKVEHMLFCWZAXGYIPSUQ")
    
    beta = NonRotatableRotor(ALPHABET, "LEYJVCNIXWPBQMDRTAKZGFUHOS", offset("A"), None)
    gamma = NonRotatableRotor(ALPHABET, "FSOKANUERHMBTIYCWLQPZXVGJD", offset("A"), None)
    
    etw_army = Stator(ALPHABET, ALPHABET)
    etw_commercial = Stator(ALPHABET, "QWERTZUIOASDFGHJKPYXCVBNML")
    etw_tirpitz =  Stator(ALPHABET, "KZROUQHYAIGBLWVSTDXFPNMCJE")
    
    #railway enigma k 
    refrail = Reflector(ALPHABET, "QYHOGNECVPUZTFDJAXWMKISRBL")
    rotorrailI = RotorPiece(ALPHABET, "JGDQOXUSCAMIFRVTPNEWKBLZYH", 0, offset("N"))
    rotorrailII = RotorPiece(ALPHABET, "NTZPSFBOKMWRCJDIVLAEYUXHGQ", 0, offset("E"))
    rotorrailIII = RotorPiece(ALPHABET, "JVIUBHTCDYAKEQZPOSGXNRMWFL", 0, offset("Y"))
    """enigma = EnigmaMachine(refa, [rotor(II), rotor(I), rotor(III)], plugboard = [
        "AM", "FI", "NV", "PS", "TU", "WZ"])
    enigma.set_rotor_state("ABL")
    enigma.set_ring(24-1, 13-1, 22-1)
    val = enigma.encode("GCDSE AHUGW TQGRK VLFGX UCALX VYMIG MMNMF DXTGN VHVRM MEVOU YFZSL RHDRR XFJWC FHUHM UNZEF RDISI KBGPM YVXUZ")
    print(val)"""
    
    """enigma = EnigmaMachine(refb, [rotor(II), rotor(IV), rotor(V)], plugboard = [
        "AV", "BS", "CG", "DL", "FU", "HZ", "IN", "KM", "OW", "RX"])
    enigma.set_rotor_state("BLA")
    enigma.set_ring(2-1, 21-1, 12-1)
    val = enigma.encode("EDPUD NRGYS ZRCXN UYTPO MRMBO FKTBZ REZKM LXLVE FGUEY SIOZV EQMIK UBPMM YLKLT TDEIS MDICA GYKUA CTCDO MOHWX MUUIA UBSTS LRNBZ SZWNR FXWFY SSXJZ VIJHI DISHP RKLKA YUPAD TXQSP INQMA TLPIF SVKDA SCTAC DPBOP VHJK")
    print(val)"""
    
    """enigma = EnigmaMachine(refb, [rotor(II), rotor(IV), rotor(V)], plugboard = [
        "AV", "BS", "CG", "DL", "FU", "HZ", "IN", "KM", "OW", "RX"])
    enigma.set_rotor_state("BLA")
    enigma.set_ring(2-1, 21-1, 12-1)
    val = enigma.encode("EDPUD NRGYS ZRCXN UYTPO MRMBO FKTBZ REZKM LXLVE FGUEY SIOZV EQMIK UBPMM YLKLT TDEIS MDICA GYKUA CTCDO MOHWX MUUIA UBSTS LRNBZ SZWNR FXWFY SSXJZ VIJHI DISHP RKLKA YUPAD TXQSP INQMA TLPIF SVKDA SCTAC DPBOP VHJK")
    print(val)"""
    
    enigma = EnigmaMachine(
        refrail, 
        [rotorrailIII, rotorrailI, rotorrailII], 
        Stator(ALPHABET, "jwulcmnohpqzyxiradkegvbtsf".upper()),
        rotatable_reflector=True)
        
    enigma.set_rotor_state("JEZA")
    enigma.set_ring(26-1,17-1, 16-1, 13-1)
    val = enigma.encode("QSZVI DVMPN EXACM RWWXU IYOTY NGVVX DZ")
    print(val)
    
    
    
    """assert len(ALPHABET) == 26
    for i, letter in enumerate(ALPHABET):
        assert refb.encode(letter) == "YRUHQSLDPXNGOKMIEBFZCWVJAT"[i]
        assert refc.encode(letter) == "FVPJIAOYEDRZXWGCTKUQSBNMHL"[i]
    
    out = "".join(rotorI.encode(x) for x in ALPHABET)
    print(out)
    assert out == "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
    print(rotorI.encode("A"))
    assert rotorI.encode("A") == "E"
    rotorI.rotation = 1 #B 
    print(rotorI.encode("A"))
    assert rotorI.encode("A") == "J"
    
    print("=====")
    rotorI.rotation = 0 # A 
    rotorI.ring_setting = 1 # B
    
    print(rotorI.encode("A"))
    
    
    rotorI.rotation = ALPHABET.find("Y") # Y
    rotorI.ring_setting = 5 # F
    print(rotorI.encode("A"))"""

    #print(enigma.encode("A"))