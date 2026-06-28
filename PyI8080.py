import pygame
import sys
import numpy as np
from functools import partial

clock = pygame.time.Clock()
pygame.init()

# CPU registers
reg = {
    'A': 0,
    'B': 0,
    'C': 0,
    'D': 0,
    'E': 0,
    'H': 0,
    'L': 0,
    'PC': 0,
    'SP': 0
    }

# CPU flags
flag = {
    'SIGN': False,
    'ZERO': False,
    'HALFCARRY': False,
    'PARITY': False,
    'CARRY': False,
    'INTERRUPT': False,
    'TRUE': True,
    'FALSE': False
}

# Input/Output ports
port = {
'IN_PORT0': 0b00001110,#Hardware mapped but unused in Space Invaders

'IN_PORT1': 0b00001000,#Bit 0: Unused.
                       #Bit 1-3: Player 1 move left/right/shoot when set to 1, then reset.
                       #Bit 4: Always 1.
                       #Bit 5: Player 1 start, then reset.
                       #Bit 6: Player 2 start, then reset.
                       #Bit 7: Insert coin, then reset.

'IN_PORT2': 0b00001011,#Bit 0: Coin info displayed in demo screen (0=ON).
                       #Bit 1-3: Player 2 move left/right/shoot when set to 1, then reset.
                       #Bit 4: 0 = extra ship at 1500 points, 1 = extra ship at 1000.
                       #Bit 5: Display TILT info when set to 1.
                       #Bits 6-7: 00 = 3 ships, 01 = 4 ships,  10 = 5 ships, 11 = 6 ships.
                        
#'IN_PORT3': 0, #In the real hardware, this port always have this formula: (((OUT_PORT4HI << 8) | OUT_PORT4LO) << OUT_PORT2) >> 8. In the emulador we only calculate and add when this port is read
'OUT_PORT2': 0,
'OUT_PORT3': 0,
'OUT_PORT4LO': 0,
'OUT_PORT4HI': 0,
'OUT_PORT5': 0,
'OUT_PORT6': 0,

# General use variables
'last_OUT_PORT3': 0,
'last_OUT_PORT5': 0
}
vram = [0x2400, 0x4000] #VRAM location
cpu_cycles = 0
vblank = 0
crashed = False

# Display variables
width = 800
height = 300
black = (0, 0, 0) #0x0
white = (255, 255, 255) #0xFFFFFF 
red = (248, 59, 58) #0xF83B3A
yellow = (235, 223, 100) #0xEBDF64
green = (98, 222, 109) #0x62DE6D
orchid = (219, 85, 221) #0xDB55DD
blue = (83, 83, 241) #0x5353F1
turquoise = (66, 233, 244) #0x42E9F4

frame_buffer = pygame.Surface((224, 256))
pixel_array = np.zeros((224, 256, 3), dtype=np.uint8)
pixel_color = np.zeros((224, 256, 3), dtype=np.uint8)
screen = pygame.display.set_mode((width, height))
pixel_color[...] = white
center = 0
invert_colors = False
pygame.display.set_caption("A 100% Python-coded emulator for old arcade games (Intel 8080 CPU). v1.3")

# Menu to choose game or test rom
font = pygame.font.SysFont("Retro.ttf", 30)
screen.blit(font.render('Click in a game or test below:', True, white), (0, 0))
screen.blit(font.render('Space Invaders', True, yellow), (0, 60))
screen.blit(font.render('Balloon Bomber', True, blue), (0, 90))
screen.blit(font.render('Galaxy Wars', True, green), (0, 120))
screen.blit(font.render('Lunar Rescue', True, turquoise), (0, 150))
screen.blit(font.render('8080PRE.COM (Intel 8080 test rom)', True, red), (0, 180))
screen.blit(font.render('TST8080.COM (Intel 8080 test rom)', True, red), (0, 210))
screen.blit(font.render('CPUTEST.COM (Intel 8080 test rom)', True, red), (0, 240))
pygame.display.flip()

click = False
while not click:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse = pygame.mouse.get_pos()
        for pos in range(60, 270, 30):
            if (mouse[1] >= pos and mouse[1] < pos + 30):
                game_selected = pos
                click = True
                break

# Menu to choose color scheme
screen.fill(black)
screen.blit(font.render('Click in a color scheme below:', True, white), (0, 0))
screen.blit(font.render('SV version (Sprites are white. Background is black)', True, yellow), (0, 60))
screen.blit(font.render('SV with inverted colors (Sprites are black. Background is white)', True, blue), (0, 90))
screen.blit(font.render('TV & Midway versions (Sprites are green, red and white. Background is black)', True, green), (0, 120))
screen.blit(font.render('TV & Midway versions with wide screen and background image', True, turquoise), (0, 150))
screen.blit(font.render('CV version with wide screen and background image', True, red), (0, 180))
pygame.display.flip()

click = False
while not click:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse = pygame.mouse.get_pos()
        for pos in range(60, 210, 30):
            if (mouse[1] >= pos and mouse[1] < pos + 30):
                color_scheme = pos
                click = True
                break
            
# Menu to choose game resolution
screen.fill(black)
screen.blit(font.render('Now choose a screen resolution:', True, white), (0, 0))
screen.blit(font.render('Native (224 x 256)', True, white), (0, 60))
screen.blit(font.render('2x size (448 x 512)', True, white), (0, 90))
screen.blit(font.render('4x size (896 x 1024)', True, white), (0, 120))
screen.blit(font.render('8x size (1792 x 2048)', True, white), (0, 150))
pygame.display.flip()

click = False
while not click:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse = pygame.mouse.get_pos()
        for pos in range(60, 180, 30):
            if (mouse[1] >= pos and mouse[1] < pos + 30):
                resolution = pos
                click = True
                break

match resolution:
    case 60:
        width = 224
        height = 256
    case 90:
        width = 224 * 2
        height = 256 * 2
    case 120:
        width = 224 * 4
        height = 256 * 4
    case 150:
        width = 224 * 8
        height = 256 * 8

def Set_Colors():
    for x in range(224):
        for y in range(256):
            pixel_color[x][y] = white
        for x in range(224):
            for y in range(32, 64):
                pixel_color[x][y] = red
        for x in range(224):
            for y in range(176, 241):
                pixel_color[x][y] = green
        for x in range(21, 135):
            for y in range(241, 256):
                pixel_color[x][y] = green

match color_scheme:
    case 60:
        screen = pygame.display.set_mode((width, height))
    case 90:
        invert_colors = True
        screen = pygame.display.set_mode((width, height))
    case 120:
        Set_Colors()
        screen = pygame.display.set_mode((width, height))
    case 150:
        Set_Colors()
        center = ((width * 1.5) / 2) - (width / 2)
        bg = pygame.image.load("Background.png").convert()
        frame_buffer.set_colorkey(black)
        screen = pygame.display.set_mode((width * 1.5, height))
        resized_background = pygame.transform.smoothscale(bg, (width * 1.5, height))
    case 180:
        Set_Colors()
        center = ((width * 1.5) / 2) - (width / 2)
        bg = pygame.image.load("Background2.png").convert()
        frame_buffer.set_colorkey(black)
        screen = pygame.display.set_mode((width * 1.5, height))
        resized_background = pygame.transform.smoothscale(bg, (width * 1.5, height))

# Sound init
shoot = pygame.mixer.Sound('shoot.wav')
explosion = pygame.mixer.Sound('explosion.wav')
invaderkilled = pygame.mixer.Sound('invaderkilled.wav')
lifegained = pygame.mixer.Sound('lifegained.wav')
fastinvader1 = pygame.mixer.Sound('fastinvader1.wav')
fastinvader2 = pygame.mixer.Sound('fastinvader2.wav')
fastinvader3 = pygame.mixer.Sound('fastinvader3.wav')
fastinvader4 = pygame.mixer.Sound('fastinvader4.wav')
ufo_lowpitch = pygame.mixer.Sound('ufo_lowpitch.wav')
ufo_highpitch = pygame.mixer.Sound('ufo_highpitch.wav')

match game_selected:
    case 60:
        memory = bytearray(open("Space Invaders/invaders.h", "rb").read()) + bytearray(open("Space Invaders/invaders.g", "rb").read()) + bytearray(open("Space Invaders/invaders.f", "rb").read()) + bytearray(open("Space Invaders/invaders.e", "rb").read() + b'\x00' * 0x2400)
    case 90:
        memory = bytearray(open("Balloon Bomber/tn01", "rb").read()) + bytearray(open("Balloon Bomber/tn02", "rb").read()) + bytearray(open("Balloon Bomber/tn03", "rb").read()) + bytearray(open("Balloon Bomber/tn04", "rb").read()) + b'\x00' * 0x2000 + bytearray(open("Balloon Bomber/tn05-1", "rb").read()) + bytearray(open("Balloon Bomber/tn06", "rb").read()) + bytearray(open("Balloon Bomber/tn07", "rb").read())
    case 120:
        memory = bytearray(open("Galaxy Wars/galxwars.0", "rb").read()) + bytearray(open("Galaxy Wars/galxwars.1", "rb").read()) + bytearray(open("Galaxy Wars/galxwars.2", "rb").read()) + bytearray(open("Galaxy Wars/galxwars.3", "rb").read()) + b'\x00' * 0x3000 + bytearray(open("Galaxy Wars/galxwars.4", "rb").read()) + bytearray(open("Galaxy Wars/galxwars.5", "rb").read())
    case 150:
        memory = bytearray(open("Lunar Rescue/lrescue.1", "rb").read()) + bytearray(open("Lunar Rescue/lrescue.2", "rb").read()) + bytearray(open("Lunar Rescue/lrescue.3", "rb").read()) + bytearray(open("Lunar Rescue/lrescue.4", "rb").read()) + b'\x00' * 0x2000 + bytearray(open("Lunar Rescue/lrescue.5", "rb").read()) + bytearray(open("Lunar Rescue/lrescue.6", "rb").read())
    case 180:
        memory = bytearray(b'\x00' * 0x100) + open("8080PRE.COM", "rb").read() + b'\x00' * 0x400
        reg['PC'] = 0x100
        memory[0] = 0x76
        memory[5] = 0xC9
        pygame.quit()
    case 210:
        memory = bytearray(b'\x00' * 0x100) + open("TST8080.COM", "rb").read() + b'\x00' * 0x400
        reg['PC'] = 0x100
        memory[0] = 0x76
        memory[5] = 0xC9
        pygame.quit()
    case 240:
        memory = bytearray(b'\x00' * 0x100) + open("CPUTEST.COM", "rb").read() + b'\x00' * 0x400
        reg['PC'] = 0x100
        memory[0] = 0x76
        memory[5] = 0xC9
        pygame.quit()

def Read_Register(register_name):
    return reg[register_name]

def Read_Memory_HL():
    HL = (reg['H'] << 8) + reg['L']
    return memory[HL]

def Read_Memory_PC():
    data = memory[reg['PC']]
    reg['PC'] += 1
    return data

def Set_ZSP_flags(value):
    flag['ZERO'] = (value == 0)
    flag['SIGN'] = ((value & 128) != 0)
    flag['PARITY'] = ((value.bit_count() % 2) == 0)

def INVALID_OPCODE():
    global crashed
    crashed = True
    print("Undefined opcode: ", hex(memory[reg['PC'] - 1]))

# Intel 8080 instruction set starts here
def NOP(cycles):
    return cycles

def RST(program_counter, cycles):
    reg['SP'] -= 1; memory[reg['SP']] = (reg['PC'] >> 8) & 0xFF 
    reg['SP'] -= 1; memory[reg['SP']] = reg['PC'] & 0xFF
    reg['PC'] = program_counter
    return cycles

def JMP(f, boolean, cycles):
    if flag[f] == flag[boolean]: reg['PC'] = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8)
    else: reg['PC'] += 2
    return cycles

def LXI(register1, register2, cycles):
    reg[register1] = memory[reg['PC']]; reg['PC'] += 1
    reg[register2] = memory[reg['PC']]; reg['PC'] += 1
    return cycles

def LXI_SP(cycles):
    reg['SP'] = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8); reg['PC'] += 2    
    return cycles

def MVI(register, cycles):
    reg[register] = memory[reg['PC']]; reg['PC'] += 1
    return cycles

def MVI_HL(cycles):
    HL = (reg['H'] << 8) + reg['L']
    memory[HL] = memory[reg['PC']]; reg['PC'] += 1
    return cycles

def CALL(f, boolean, cycles, cycles2):
    if flag[f] == flag[boolean]:
        aux = reg['PC'] + 2
        reg['SP'] -= 1; memory[reg['SP']] = (aux >> 8) & 0xFF 
        reg['SP'] -= 1; memory[reg['SP']] = aux & 0xFF
        reg['PC'] = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8)
        if reg['PC'] == 5:
            if reg['C'] == 2:
                print(chr(reg['E']), end="")
            elif reg['C'] == 9:
                DE = (reg['D'] << 8) + reg['E']
                pos = 0
                while chr(memory[DE + pos]) != '$':
                    print(chr(memory[DE + pos]), end="")
                    pos += 1
        return cycles
    else:
        reg['PC'] += 2
        return cycles2

def RET(f, boolean, cycles, cycles2):
    if flag[f] == flag[boolean]:
        reg['PC'] = memory[reg['SP']] + (memory[reg['SP'] + 1] << 8); reg['SP'] += 2
        return cycles
    else:
        return cycles2

def LDA(cycles):
    reg['A'] = memory[memory[reg['PC']] + (memory[reg['PC'] + 1] << 8)]; reg['PC'] += 2
    return cycles

def LDA_BC_DE(register1, register2, cycles):
    aux = (reg[register1] << 8) + reg[register2]
    reg['A'] = memory[aux]
    return cycles

def PUSH(register1, register2, cycles):
    reg['SP'] -= 1; memory[reg['SP']] = reg[register1]
    reg['SP'] -= 1; memory[reg['SP']] = reg[register2]
    return cycles

def PUSH_AF(cycles):
    aux = (flag['SIGN'] << 7) | (flag['ZERO'] << 6) | (0 << 5) | (flag['HALFCARRY'] << 4) | (0 << 3) | (flag['PARITY'] << 2) | (1 << 1) | flag['CARRY']
    reg['SP'] -= 1; memory[reg['SP']] = reg['A']
    reg['SP'] -= 1; memory[reg['SP']] = aux
    return cycles

def POP(register1, register2, cycles):
    reg[register1] = memory[reg['SP']]; reg['SP'] += 1
    reg[register2] = memory[reg['SP']]; reg['SP'] += 1
    return cycles

def POP_AF(cycles):
    aux = memory[reg['SP']]; reg['SP'] += 1
    reg['A'] = memory[reg['SP']]; reg['SP'] += 1
    flag['SIGN'] = (aux & 0x80) != 0
    flag['ZERO'] = (aux & 0x40) != 0
    flag['HALFCARRY'] = (aux & 0x10) != 0
    flag['PARITY'] = (aux & 0x4) != 0
    flag['CARRY'] = (aux & 0x1) != 0
    return cycles

def MOV(register, Value, cycles):
    reg[register] = Value()
    return cycles

def MOV_HL(register, cycles):
    HL = (reg['H'] << 8) + reg['L']
    memory[HL] = reg[register]
    return cycles

def INX(register1, register2, cycles):
    aux = (reg[register1] << 8) + reg[register2]
    aux = (aux + 1) & 0xFFFF
    reg[register1] = (aux >> 8)
    reg[register2] = aux & 0xFF
    return cycles

def INX_SP(cycles):
    reg['SP'] = (reg['SP'] + 1) & 0xFFFF
    return cycles

def DAD(register1, register2, cycles):
    aux = (reg[register1] << 8) + reg[register2]
    HL = (reg['H'] << 8) + reg['L']
    flag['CARRY'] = ((HL + aux) > 0xFFFF)
    HL = (HL + aux) & 0xFFFF
    reg['H'] = (HL >> 8)
    reg['L'] = HL & 0xFF
    return cycles

def DAD_SP(cycles):
    HL = (reg['H'] << 8) + reg['L']
    flag['CARRY'] = ((HL + reg['SP']) > 0xFFFF)
    HL = (HL + reg['SP']) & 0xFFFF
    reg['H'] = (HL >> 8)
    reg['L'] = HL & 0xFF
    return cycles

def DCX(register1, register2, cycles):
    aux = (reg[register1] << 8) + reg[register2]
    aux = (aux - 1) & 0xFFFF
    reg[register1] = (aux >> 8)
    reg[register2] = aux & 0xFF
    return cycles

def DCX_SP(cycles):
    reg['SP'] = (reg['SP'] - 1) & 0xFFFF
    return cycles

def DEC(register, cycles):
    aux = reg[register]
    reg[register] = (reg[register] - 1) & 0xFF
    #flag['HALFCARRY'] = ((aux & 0xF) == 0)
    flag['HALFCARRY'] = ((aux ^ 1 ^ reg[register]) & 0x10) == 0
    Set_ZSP_flags(reg[register])
    return cycles

def DEC_HL(cycles):
    HL = (reg['H'] << 8) + reg['L']
    aux = memory[HL]
    memory[HL] = (memory[HL] - 1) & 0xFF
    #flag['HALFCARRY'] = ((aux & 0xF) == 0)
    flag['HALFCARRY'] = ((aux ^ 1 ^ memory[HL]) & 0x10) == 0
    Set_ZSP_flags(memory[HL])
    return cycles

def INC(register, cycles):
    aux = reg[register]
    reg[register] = (reg[register] + 1) & 0xFF
    #flag['HALFCARRY'] = ((A & 0xF) != 0)
    flag['HALFCARRY'] = ((aux ^ 1 ^ reg[register]) & 0x10) != 0
    Set_ZSP_flags(reg[register])
    return cycles

def INC_HL(cycles):
    HL = (reg['H'] << 8) + reg['L']
    aux = memory[HL]
    memory[HL] = (memory[HL] + 1) & 0xFF
    #flag['HALFCARRY'] = ((memory[HL] & 0xF) != 0)
    flag['HALFCARRY'] = ((aux ^ 1 ^ memory[HL]) & 0x10) != 0
    Set_ZSP_flags(memory[HL])
    return cycles

def AND(Value, cycles):
    data = Value()
    flag['CARRY'] = False
    flag['HALFCARRY'] = (((reg['A'] | data) & 0x8) != 0)
    reg['A'] = (reg['A'] & data)
    Set_ZSP_flags(reg['A'])
    return cycles

def XOR(Value, cycles):
    data = Value()
    reg['A'] = reg['A'] ^ data
    flag['CARRY'] = False
    flag['HALFCARRY'] = False
    Set_ZSP_flags(reg['A'])
    return cycles

def OR(Value, cycles):
    data = Value()
    reg['A'] = reg['A'] | data
    flag['CARRY'] = False
    flag['HALFCARRY'] = False
    Set_ZSP_flags(reg['A'])
    return cycles

def ADD_ADC(Value, boolean, cycles):
    data = Value()
    aux = (reg['A'] + data + flag[boolean]) & 0xFF
    flag['CARRY'] = ((reg['A'] + data + flag[boolean]) > 255)
    flag['HALFCARRY'] = (((reg['A'] ^ data ^ aux) & 0x10) != 0)
    reg['A'] = aux
    Set_ZSP_flags(reg['A'])
    return cycles

def SUB_SBB(Value, boolean, cycles):
    data = Value()
    aux = (reg['A'] - data - flag[boolean]) & 0xFF
    flag['CARRY'] = ((reg['A'] - data - flag[boolean]) < 0)
    flag['HALFCARRY'] = ((reg['A'] ^ data ^ aux) & 0x10) == 0
    reg['A'] = aux
    Set_ZSP_flags(reg['A'])
    return cycles

def CMP(Value, cycles):
    data = Value()
    aux = (reg['A'] - data) & 0xFF
    flag['CARRY'] = ((reg['A'] - data) < 0)
    flag['HALFCARRY'] = ((reg['A'] ^ data ^ aux) & 0x10) == 0
    Set_ZSP_flags(aux)
    return cycles

def XCHG(cycles):
    reg['H'], reg['L'], reg['D'], reg['E'] = reg['D'], reg['E'], reg['H'], reg['L']
    return cycles

def XTHL(cycles):
    reg['H'], reg['L'], memory[reg['SP']], memory[reg['SP'] + 1] = memory[reg['SP'] + 1], memory[reg['SP']], reg['L'], reg['H']
    return cycles

def PCHL_SPHL(register, cycles):
    HL = (reg['H'] << 8) + reg['L']
    reg[register] = HL
    return cycles

def RLC(cycles):
    aux = (reg['A'] << 1) | (reg['A'] >> 7)
    reg['A'] = ((reg['A'] << 1) | (reg['A'] >> 7)) & 0xFF
    flag['CARRY'] = ((aux & 0x1) != 0)
    return cycles

def RAL(cycles):
    aux = reg['A']
    reg['A'] = (reg['A'] << 1) & 0xFF
    if (flag['CARRY']): reg['A'] = reg['A'] | 0x1
    flag['CARRY'] = ((aux & 0x80) != 0)
    return cycles

def RRC(cycles):
    aux =(reg['A'] >> 1) | (reg['A'] << 7)
    reg['A'] = ((reg['A'] >> 1) | (reg['A'] << 7)) & 0xFF
    flag['CARRY'] = ((aux & 0x80) != 0)
    return cycles

def RAR(cycles):
    aux = reg['A']
    reg['A'] = (reg['A'] >> 1) & 0xFF
    if (flag['CARRY']): reg['A'] = reg['A'] | 0x80
    flag['CARRY'] = ((aux & 0x1) != 0)
    return cycles

def STA(register1, register2, cycles):
    aux = (reg[register1] << 8) + reg[register2]
    memory[aux] = reg['A']
    return cycles

def STA_PC(cycles):
    aux = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8); reg['PC'] += 2
    memory[aux] = reg['A']
    return cycles

def DI_EI(boolean, cycles):
    flag['INTERRUPT'] = flag[boolean]
    return cycles

def STC_CMC(boolean, cycles):
    flag['CARRY'] = not flag[boolean]
    return cycles

def LHLD(cycles):
    aux = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8); reg['PC'] += 2
    reg['L'] = memory[aux]
    reg['H'] = memory[aux + 1]
    return cycles

def SHLD(cycles):
    aux = memory[reg['PC']] + (memory[reg['PC'] + 1] << 8); reg['PC'] += 2
    memory[aux] = reg['L']
    memory[aux + 1] = reg['H']
    return cycles

def DAA(cycles):
    if (((reg['A'] & 0xF) > 9) or flag['HALFCARRY']):
        aux = reg['A'] + 0x6
        reg['A'] = (reg['A'] + 0x6) & 0xFF
        flag['HALFCARRY'] = ((aux ^ 1 ^ reg['A']) & 0x10) != 0
    if ((reg['A'] > 0x9F) or flag['CARRY']):
        aux = reg['A'] + 0x60
        reg['A'] = (reg['A'] + 0x60) & 0xFF
        flag['CARRY'] = (aux > 255) or flag['CARRY']
    Set_ZSP_flags(reg['A'])
    return cycles

def CMA(cycles):
    reg['A'] = reg['A'] ^ 255
    return cycles

def HLT(cycles):
    input() #Pauses execution and wait any console input
    return cycles

def OUTP(cycles):
    global crashed
    reg['PC'] += 1
    match memory[reg['PC'] - 1]:
        #case 0:
        case 1:
        #    print(chr(reg['A']), end="")
            pass
        case 2:
            port['OUT_PORT2'] = reg['A']
        case 3:
            port['OUT_PORT3'] = reg['A']
            if (port['OUT_PORT3'] & 0x1) and not (port['last_OUT_PORT3'] & 0x1):
                ufo_highpitch.play(-1)
            if not (port['OUT_PORT3'] & 0x1) and (port['last_OUT_PORT3'] & 0x1):
                ufo_highpitch.stop()
            if (port['OUT_PORT3'] & 0x2) and not (port['last_OUT_PORT3'] & 0x2):
                invaderkilled.play()
            if (port['OUT_PORT3'] & 0x4) and not (port['last_OUT_PORT3'] & 0x4):
                explosion.play()
            if (port['OUT_PORT3'] & 0x8) and not (port['last_OUT_PORT3'] & 0x8):
                shoot.play()
            if (port['OUT_PORT3'] & 0x10) and not (port['last_OUT_PORT3'] & 0x10):
                lifegained.play()
            port['last_OUT_PORT3'] = port['OUT_PORT3']
        case 4:
            port['OUT_PORT4LO'] = port['OUT_PORT4HI']
            port['OUT_PORT4HI'] = reg['A']
        case 5:
            port['OUT_PORT5'] = reg['A']
            if (port['OUT_PORT5'] & 0x1) and not(port['last_OUT_PORT5'] & 0x1):
                fastinvader3.play()
            if (port['OUT_PORT5'] & 0x2) and not(port['last_OUT_PORT5'] & 0x2):
                fastinvader4.play()
            if (port['OUT_PORT5'] & 0x4) and not(port['last_OUT_PORT5'] & 0x4):
                fastinvader1.play()
            if (port['OUT_PORT5'] & 0x8) and not(port['last_OUT_PORT5'] & 0x8):
                 fastinvader2.play()
            if (port['OUT_PORT5'] & 0x10) and not(port['last_OUT_PORT5'] & 0x10):
                ufo_lowpitch.play()
                port['last_OUT_PORT5'] = port['OUT_PORT5']
        case 6:
            port['OUT_PORT6'] = reg['A']
        case _:
            crashed = True
            print("Undefined Output port: ", memory[reg['PC'] - 1])
    return cycles

def INP(cycles):
    global crashed
    reg['PC'] += 1
    match memory[reg['PC'] - 1]:
        case 0:
            reg['A'] = port['IN_PORT0']
        case 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            keycode = pygame.key.get_pressed()
            if keycode[pygame.K_SPACE]:# Insert coin
                port['IN_PORT1'] |= 0x1
            if keycode[pygame.K_w]:    # Player 1 Start
                port['IN_PORT1'] |= 0x4
            if keycode[pygame.K_DOWN]: # Player 2 Start (need 2 or more coins)
                port['IN_PORT1'] |= 0x2
            if keycode[pygame.K_a]:    # Player 1 move left
                port['IN_PORT1'] |= 0x20
            if keycode[pygame.K_d]:    # Player 1 move right
                port['IN_PORT1'] |= 0x40
            if keycode[pygame.K_s]:    # Player 1 shoot
                port['IN_PORT1'] |= 0x10
                        
            reg['A'] = port['IN_PORT1']
            port['IN_PORT1'] &= 0b10001000
        
        case 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            keycode = pygame.key.get_pressed()
            if keycode[pygame.K_LEFT]:  # Player 2 move left
                port['IN_PORT2'] |= 0x20
            if keycode[pygame.K_RIGHT]: # Player 2 move right
                port['IN_PORT2'] |= 0x40
            if keycode[pygame.K_DOWN]:  # Player 2 shoot
                port['IN_PORT2'] |= 0x10
                        
            reg['A'] = port['IN_PORT2']
            port['IN_PORT2'] &= 0b10001111
                    
        case 3:
            reg['A'] = ((((port['OUT_PORT4HI'] << 8) | port['OUT_PORT4LO']) << port['OUT_PORT2']) >> 8) & 0xFF
        case _:
            crashed = True
            print("Undefined Input port: ", memory[reg['PC'] - 1])
    return cycles

#Instructions dispatch table/list
Instruction = [INVALID_OPCODE] * 256
Instruction[0x00] = Instruction[0x08] = Instruction[0x10] = Instruction[0x18] = Instruction[0x20] = Instruction[0x28] = Instruction[0x30] = Instruction[0x38] = partial(NOP, 4)
Instruction[0xC7] = partial(RST, 0x00, 11)
Instruction[0xCF] = partial(RST, 0x08, 11)
Instruction[0xD7] = partial(RST, 0x10, 11)
Instruction[0xDF] = partial(RST, 0x18, 11)
Instruction[0xE7] = partial(RST, 0x20, 11)
Instruction[0xEF] = partial(RST, 0x28, 11)
Instruction[0xF7] = partial(RST, 0x30, 11)
Instruction[0xFF] = partial(RST, 0x38, 11)
Instruction[0xC3] = Instruction[0xCB] = partial(JMP, 'TRUE', 'TRUE', 10)
Instruction[0xC2] = partial(JMP, 'ZERO', 'FALSE', 10)
Instruction[0xCA] = partial(JMP, 'ZERO', 'TRUE', 10)
Instruction[0xD2] = partial(JMP, 'CARRY', 'FALSE', 10)
Instruction[0xDA] = partial(JMP, 'CARRY', 'TRUE', 10)
Instruction[0xF2] = partial(JMP, 'SIGN', 'FALSE', 10)
Instruction[0xFA] = partial(JMP, 'SIGN', 'TRUE', 10)
Instruction[0xE2] = partial(JMP, 'PARITY', 'FALSE', 10)
Instruction[0xEA] = partial(JMP, 'PARITY', 'TRUE', 10)
Instruction[0x01] = partial(LXI, 'C', 'B', 10)
Instruction[0x11] = partial(LXI, 'E', 'D', 10)
Instruction[0x21] = partial(LXI, 'L', 'H', 10)
Instruction[0x31] = partial(LXI_SP, 10)
Instruction[0x3E] = partial(MVI, 'A', 7)
Instruction[0x06] = partial(MVI, 'B', 7)
Instruction[0x0E] = partial(MVI, 'C', 7)
Instruction[0x16] = partial(MVI, 'D', 7)
Instruction[0x1E] = partial(MVI, 'E', 7)
Instruction[0x26] = partial(MVI, 'H', 7)
Instruction[0x2E] = partial(MVI, 'L', 7)
Instruction[0x36] = partial(MVI_HL, 10)
Instruction[0xCD] = Instruction[0xDD] = Instruction[0xED] = Instruction[0xFD] = partial(CALL, 'TRUE', 'TRUE', 17, 11)
Instruction[0xC4] = partial(CALL, 'ZERO', 'FALSE', 17, 11)
Instruction[0xCC] = partial(CALL, 'ZERO', 'TRUE', 17, 11)
Instruction[0xD4] = partial(CALL, 'CARRY', 'FALSE', 17, 11)
Instruction[0xDC] = partial(CALL, 'CARRY', 'TRUE', 17, 11)
Instruction[0xE4] = partial(CALL, 'PARITY', 'FALSE', 17, 11)
Instruction[0xEC] = partial(CALL, 'PARITY', 'TRUE', 17, 11)
Instruction[0xF4] = partial(CALL, 'SIGN', 'FALSE', 17, 11)
Instruction[0xFC] = partial(CALL, 'SIGN', 'TRUE', 17, 11)
Instruction[0xC9] = Instruction[0xD9] = partial(RET, 'TRUE', 'TRUE', 10, 5)
Instruction[0xC0] = partial(RET, 'ZERO', 'FALSE', 11, 5)
Instruction[0xC8] = partial(RET, 'ZERO', 'TRUE', 11, 5)
Instruction[0xD0] = partial(RET, 'CARRY', 'FALSE', 11, 5)
Instruction[0xD8] = partial(RET, 'CARRY', 'TRUE', 11, 5)
Instruction[0xE0] = partial(RET, 'PARITY', 'FALSE', 11, 5)
Instruction[0xE8] = partial(RET, 'PARITY', 'TRUE', 11, 5)
Instruction[0xF0] = partial(RET, 'SIGN', 'FALSE', 11, 5)
Instruction[0xF8] = partial(RET, 'SIGN', 'TRUE', 11, 5)
Instruction[0x0A] = partial(LDA_BC_DE, 'B', 'C', 7)
Instruction[0x1A] = partial(LDA_BC_DE, 'D', 'E', 7)
Instruction[0x3A] = partial(LDA, 13)
Instruction[0xC5] = partial(PUSH, 'B', 'C', 11)
Instruction[0xD5] = partial(PUSH, 'D', 'E', 11)
Instruction[0xE5] = partial(PUSH, 'H', 'L', 11)
Instruction[0xF5] = partial(PUSH_AF, 11)
Instruction[0xC1] = partial(POP, 'C', 'B', 10)
Instruction[0xD1] = partial(POP, 'E', 'D', 10)
Instruction[0xE1] = partial(POP, 'L', 'H', 10)
Instruction[0xF1] = partial(POP_AF, 10)
Instruction[0x77] = partial(MOV_HL, 'A', 7)
Instruction[0x70] = partial(MOV_HL, 'B', 7)
Instruction[0x71] = partial(MOV_HL, 'C', 7)
Instruction[0x72] = partial(MOV_HL, 'D', 7)
Instruction[0x73] = partial(MOV_HL, 'E', 7)
Instruction[0x74] = partial(MOV_HL, 'H', 7)
Instruction[0x75] = partial(MOV_HL, 'L', 7)
Instruction[0x7F] = partial(MOV, 'A', partial(Read_Register, 'A'), 5)
Instruction[0x78] = partial(MOV, 'A', partial(Read_Register, 'B'), 5)
Instruction[0x79] = partial(MOV, 'A', partial(Read_Register, 'C'), 5)
Instruction[0x7A] = partial(MOV, 'A', partial(Read_Register, 'D'), 5)
Instruction[0x7B] = partial(MOV, 'A', partial(Read_Register, 'E'), 5)
Instruction[0x7C] = partial(MOV, 'A', partial(Read_Register, 'H'), 5)
Instruction[0x7D] = partial(MOV, 'A', partial(Read_Register, 'L'), 5)
Instruction[0x7E] = partial(MOV, 'A', Read_Memory_HL, 7)
Instruction[0x47] = partial(MOV, 'B', partial(Read_Register, 'A'), 5)
Instruction[0x40] = partial(MOV, 'B', partial(Read_Register, 'B'), 5)
Instruction[0x41] = partial(MOV, 'B', partial(Read_Register, 'C'), 5)
Instruction[0x42] = partial(MOV, 'B', partial(Read_Register, 'D'), 5)
Instruction[0x43] = partial(MOV, 'B', partial(Read_Register, 'E'), 5)
Instruction[0x44] = partial(MOV, 'B', partial(Read_Register, 'H'), 5)
Instruction[0x45] = partial(MOV, 'B', partial(Read_Register, 'L'), 5)                     
Instruction[0x46] = partial(MOV, 'B', Read_Memory_HL, 7)
Instruction[0x4F] = partial(MOV, 'C', partial(Read_Register, 'A'), 5)
Instruction[0x48] = partial(MOV, 'C', partial(Read_Register, 'B'), 5)
Instruction[0x49] = partial(MOV, 'C', partial(Read_Register, 'C'), 5)
Instruction[0x4A] = partial(MOV, 'C', partial(Read_Register, 'D'), 5)
Instruction[0x4B] = partial(MOV, 'C', partial(Read_Register, 'E'), 5)
Instruction[0x4C] = partial(MOV, 'C', partial(Read_Register, 'H'), 5)
Instruction[0x4D] = partial(MOV, 'C', partial(Read_Register, 'L'), 5)
Instruction[0x4E] = partial(MOV, 'C', Read_Memory_HL, 7)
Instruction[0x57] = partial(MOV, 'D', partial(Read_Register, 'A'), 5)
Instruction[0x50] = partial(MOV, 'D', partial(Read_Register, 'B'), 5)
Instruction[0x51] = partial(MOV, 'D', partial(Read_Register, 'C'), 5)
Instruction[0x52] = partial(MOV, 'D', partial(Read_Register, 'D'), 5)
Instruction[0x53] = partial(MOV, 'D', partial(Read_Register, 'E'), 5)
Instruction[0x54] = partial(MOV, 'D', partial(Read_Register, 'H'), 5)
Instruction[0x55] = partial(MOV, 'D', partial(Read_Register, 'L'), 5)
Instruction[0x56] = partial(MOV, 'D', Read_Memory_HL, 7)
Instruction[0x5F] = partial(MOV, 'E', partial(Read_Register, 'A'), 5)
Instruction[0x58] = partial(MOV, 'E', partial(Read_Register, 'B'), 5)
Instruction[0x59] = partial(MOV, 'E', partial(Read_Register, 'C'), 5)
Instruction[0x5A] = partial(MOV, 'E', partial(Read_Register, 'D'), 5)
Instruction[0x5B] = partial(MOV, 'E', partial(Read_Register, 'E'), 5)
Instruction[0x5C] = partial(MOV, 'E', partial(Read_Register, 'H'), 5)
Instruction[0x5D] = partial(MOV, 'E', partial(Read_Register, 'L'), 5)
Instruction[0x5E] = partial(MOV, 'E', Read_Memory_HL, 7)                       
Instruction[0x67] = partial(MOV, 'H', partial(Read_Register, 'A'), 5)
Instruction[0x60] = partial(MOV, 'H', partial(Read_Register, 'B'), 5)
Instruction[0x61] = partial(MOV, 'H', partial(Read_Register, 'C'), 5)
Instruction[0x62] = partial(MOV, 'H', partial(Read_Register, 'D'), 5)
Instruction[0x63] = partial(MOV, 'H', partial(Read_Register, 'E'), 5)
Instruction[0x64] = partial(MOV, 'H', partial(Read_Register, 'H'), 5)
Instruction[0x65] = partial(MOV, 'H', partial(Read_Register, 'L'), 5)
Instruction[0x66] = partial(MOV, 'H', Read_Memory_HL, 7)
Instruction[0x6F] = partial(MOV, 'L', partial(Read_Register, 'A'), 5)
Instruction[0x68] = partial(MOV, 'L', partial(Read_Register, 'B'), 5)
Instruction[0x69] = partial(MOV, 'L', partial(Read_Register, 'C'), 5)
Instruction[0x6A] = partial(MOV, 'L', partial(Read_Register, 'D'), 5)
Instruction[0x6B] = partial(MOV, 'L', partial(Read_Register, 'E'), 5)
Instruction[0x6C] = partial(MOV, 'L', partial(Read_Register, 'H'), 5)
Instruction[0x6D] = partial(MOV, 'L', partial(Read_Register, 'L'), 5)
Instruction[0x6E] = partial(MOV, 'L', Read_Memory_HL, 7)
Instruction[0x03] = partial(INX, 'B', 'C', 5)
Instruction[0x13] = partial(INX, 'D', 'E', 5)
Instruction[0x23] = partial(INX, 'H', 'L', 5)
Instruction[0x33] = partial(INX_SP, 5)
Instruction[0x09] = partial(DAD, 'B', 'C', 10)
Instruction[0x19] = partial(DAD, 'D', 'E', 10)
Instruction[0x29] = partial(DAD, 'H', 'L', 10)
Instruction[0x39] = partial(DAD_SP, 10)
Instruction[0x0B] = partial(DCX, 'B', 'C', 5)
Instruction[0x1B] = partial(DCX, 'D', 'E', 5)
Instruction[0x2B] = partial(DCX, 'H', 'L', 5)
Instruction[0x3B] = partial(DCX_SP, 5)
Instruction[0x3D] = partial(DEC, 'A', 5)
Instruction[0x05] = partial(DEC, 'B', 5)
Instruction[0x0D] = partial(DEC, 'C', 5)
Instruction[0x15] = partial(DEC, 'D', 5)
Instruction[0x1D] = partial(DEC, 'E', 5)
Instruction[0x25] = partial(DEC, 'H', 5)
Instruction[0x2D] = partial(DEC, 'L', 5)
Instruction[0x35] = partial(DEC_HL, 10)
Instruction[0x3C] = partial(INC, 'A', 5)
Instruction[0x04] = partial(INC, 'B', 5)
Instruction[0x0C] = partial(INC, 'C', 5)
Instruction[0x14] = partial(INC, 'D', 5)
Instruction[0x1C] = partial(INC, 'E', 5)
Instruction[0x24] = partial(INC, 'H', 5)
Instruction[0x2C] = partial(INC, 'L', 5)
Instruction[0x34] = partial(INC_HL, 10)
Instruction[0xA7] = partial(AND, partial(Read_Register, 'A'), 4)
Instruction[0xA0] = partial(AND, partial(Read_Register, 'B'), 4)
Instruction[0xA1] = partial(AND, partial(Read_Register, 'C'), 4)
Instruction[0xA2] = partial(AND, partial(Read_Register, 'D'), 4)
Instruction[0xA3] = partial(AND, partial(Read_Register, 'E'), 4)
Instruction[0xA4] = partial(AND, partial(Read_Register, 'H'), 4)
Instruction[0xA5] = partial(AND, partial(Read_Register, 'L'), 4)
Instruction[0xA6] = partial(AND, Read_Memory_HL, 7)
Instruction[0xE6] = partial(AND, Read_Memory_PC, 7)
Instruction[0xAF] = partial(XOR, partial(Read_Register, 'A'), 4)
Instruction[0xA8] = partial(XOR, partial(Read_Register, 'B'), 4)
Instruction[0xA9] = partial(XOR, partial(Read_Register, 'C'), 4)
Instruction[0xAA] = partial(XOR, partial(Read_Register, 'D'), 4)
Instruction[0xAB] = partial(XOR, partial(Read_Register, 'E'), 4)
Instruction[0xAC] = partial(XOR, partial(Read_Register, 'H'), 4)
Instruction[0xAD] = partial(XOR, partial(Read_Register, 'L'), 4)
Instruction[0xAE] = partial(XOR, Read_Memory_HL, 7)
Instruction[0xEE] = partial(XOR, Read_Memory_PC, 7)
Instruction[0xB7] = partial(OR, partial(Read_Register, 'A'), 4)
Instruction[0xB0] = partial(OR, partial(Read_Register, 'B'), 4)
Instruction[0xB1] = partial(OR, partial(Read_Register, 'C'), 4)
Instruction[0xB2] = partial(OR, partial(Read_Register, 'D'), 4)
Instruction[0xB3] = partial(OR, partial(Read_Register, 'E'), 4)
Instruction[0xB4] = partial(OR, partial(Read_Register, 'H'), 4)
Instruction[0xB5] = partial(OR, partial(Read_Register, 'L'), 4)
Instruction[0xB6] = partial(OR, Read_Memory_HL, 7)
Instruction[0xF6] = partial(OR, Read_Memory_PC, 7)
Instruction[0x87] = partial(ADD_ADC, partial(Read_Register, 'A'), 'FALSE', 4)
Instruction[0x80] = partial(ADD_ADC, partial(Read_Register, 'B'), 'FALSE', 4)
Instruction[0x81] = partial(ADD_ADC, partial(Read_Register, 'C'), 'FALSE', 4)
Instruction[0x82] = partial(ADD_ADC, partial(Read_Register, 'D'), 'FALSE', 4)
Instruction[0x83] = partial(ADD_ADC, partial(Read_Register, 'E'), 'FALSE', 4)
Instruction[0x84] = partial(ADD_ADC, partial(Read_Register, 'H'), 'FALSE', 4)
Instruction[0x85] = partial(ADD_ADC, partial(Read_Register, 'L'), 'FALSE', 4)
Instruction[0x86] = partial(ADD_ADC, Read_Memory_HL, 'FALSE', 7)
Instruction[0xC6] = partial(ADD_ADC, Read_Memory_PC, 'FALSE', 7)
Instruction[0x8F] = partial(ADD_ADC, partial(Read_Register, 'A'), 'CARRY', 4)
Instruction[0x88] = partial(ADD_ADC, partial(Read_Register, 'B'), 'CARRY', 4)
Instruction[0x89] = partial(ADD_ADC, partial(Read_Register, 'C'), 'CARRY', 4)
Instruction[0x8A] = partial(ADD_ADC, partial(Read_Register, 'D'), 'CARRY', 4)
Instruction[0x8B] = partial(ADD_ADC, partial(Read_Register, 'E'), 'CARRY', 4)
Instruction[0x8C] = partial(ADD_ADC, partial(Read_Register, 'H'), 'CARRY', 4)
Instruction[0x8D] = partial(ADD_ADC, partial(Read_Register, 'L'), 'CARRY', 4)
Instruction[0x8E] = partial(ADD_ADC, Read_Memory_HL, 'CARRY', 7)
Instruction[0xCE] = partial(ADD_ADC, Read_Memory_PC, 'CARRY', 7)
Instruction[0x97] = partial(SUB_SBB, partial(Read_Register, 'A'), 'FALSE', 4)
Instruction[0x90] = partial(SUB_SBB, partial(Read_Register, 'B'), 'FALSE', 4)
Instruction[0x91] = partial(SUB_SBB, partial(Read_Register, 'C'), 'FALSE', 4)
Instruction[0x92] = partial(SUB_SBB, partial(Read_Register, 'D'), 'FALSE', 4)
Instruction[0x93] = partial(SUB_SBB, partial(Read_Register, 'E'), 'FALSE', 4)
Instruction[0x94] = partial(SUB_SBB, partial(Read_Register, 'H'), 'FALSE', 4)
Instruction[0x95] = partial(SUB_SBB, partial(Read_Register, 'L'), 'FALSE', 4)
Instruction[0x96] = partial(SUB_SBB, Read_Memory_HL, 'FALSE', 7)
Instruction[0xD6] = partial(SUB_SBB, Read_Memory_PC, 'FALSE', 7)
Instruction[0x9F] = partial(SUB_SBB, partial(Read_Register, 'A'), 'CARRY', 4)
Instruction[0x98] = partial(SUB_SBB, partial(Read_Register, 'B'), 'CARRY', 4)
Instruction[0x99] = partial(SUB_SBB, partial(Read_Register, 'C'), 'CARRY', 4)
Instruction[0x9A] = partial(SUB_SBB, partial(Read_Register, 'D'), 'CARRY', 4)
Instruction[0x9B] = partial(SUB_SBB, partial(Read_Register, 'E'), 'CARRY', 4)
Instruction[0x9C] = partial(SUB_SBB, partial(Read_Register, 'H'), 'CARRY', 4)
Instruction[0x9D] = partial(SUB_SBB, partial(Read_Register, 'L'), 'CARRY', 4)
Instruction[0x9E] = partial(SUB_SBB, Read_Memory_HL, 'CARRY', 7)
Instruction[0xDE] = partial(SUB_SBB, Read_Memory_PC, 'CARRY', 7)
Instruction[0xBF] = partial(CMP, partial(Read_Register, 'A'), 4)
Instruction[0xB8] = partial(CMP, partial(Read_Register, 'B'), 4)
Instruction[0xB9] = partial(CMP, partial(Read_Register, 'C'), 4)
Instruction[0xBA] = partial(CMP, partial(Read_Register, 'D'), 4)
Instruction[0xBB] = partial(CMP, partial(Read_Register, 'E'), 4)
Instruction[0xBC] = partial(CMP, partial(Read_Register, 'H'), 4)
Instruction[0xBD] = partial(CMP, partial(Read_Register, 'L'), 4)
Instruction[0xBE] = partial(CMP, Read_Memory_HL, 7)
Instruction[0xFE] = partial(CMP, Read_Memory_PC, 7)
Instruction[0xEB] = partial(XCHG, 5)
Instruction[0xE3] = partial(XTHL, 18)
Instruction[0xD3] = partial(OUTP, 10)
Instruction[0XDB] = partial(INP, 10)
Instruction[0xE9] = partial(PCHL_SPHL, 'PC', 5)  
Instruction[0xF9] = partial(PCHL_SPHL, 'SP', 5)
Instruction[0x07] = partial(RLC, 4)
Instruction[0x17] = partial(RAL, 4)
Instruction[0x0F] = partial(RRC, 4)
Instruction[0x1F] = partial(RAR, 4)
Instruction[0x02] = partial(STA, 'B', 'C', 7)
Instruction[0x12] = partial(STA, 'D', 'E', 7)
Instruction[0x32] = partial(STA_PC, 13)
Instruction[0xF3] = partial(DI_EI, 'FALSE', 4)
Instruction[0xFB] = partial(DI_EI, 'TRUE', 4)
Instruction[0x37] = partial(STC_CMC, 'FALSE', 4)
Instruction[0x3F] = partial(STC_CMC, 'CARRY', 4)
Instruction[0x2A] = partial(LHLD, 16)
Instruction[0x22] = partial(SHLD, 16)
Instruction[0x27] = partial(DAA, 4)
Instruction[0x2F] = partial(CMA, 4)
Instruction[0x76] = partial(HLT, 7)
    
# Main loop
while not crashed:

    # Debug Stuff
    #print('PC:', hex(reg['PC']), 'AF:', hex((reg['A'] << 8) + (flag['SIGN'] << 7) | (flag['ZERO'] << 6) | (0 << 5) | (flag['HALFCARRY'] << 4) | (0 << 3) | (flag['PARITY'] << 2) | (1 << 1) | flag['CARRY']), 'BC:', hex((reg['B'] << 8) + reg['C']), 'DE:', hex((reg['D'] << 8) + reg['E']), 'HL:', hex((reg['H'] << 8) + reg['L']), 'SP:', hex(reg['SP']), 'CYC:', cpu_cycles, '(', hex(memory[reg['PC']]), hex(memory[reg['PC']+1]), hex(memory[reg['PC']+2]), hex(memory[reg['PC']+3]), ')')
    #input()
    
    opcode = memory[reg['PC']]; reg['PC'] += 1
    cpu_cycles += Instruction[opcode]() # Fetch opcode

    # Interrupt stuff
    if cpu_cycles >= 16768:
        if flag['INTERRUPT']:
            reg['SP']-= 1; memory[reg['SP']] = reg['PC'] >> 8
            reg['SP']-= 1; memory[reg['SP']] = reg['PC'] & 0xFF
            flag['INTERRUPT'] = False
            if not vblank:
                reg['PC'] = 0x8           
            else:
                reg['PC'] = 0x10
                vram_bytes = np.frombuffer(memory[vram[0]:vram[1]], dtype=np.uint8)
                vram_bits = np.unpackbits(vram_bytes, bitorder='little')
                landscape_screen = vram_bits.reshape((256, 224), order='F') ^ invert_colors
                portrait_screen = np.rot90(landscape_screen, k=3)
                pixel_array[:] = pixel_color
                pixel_array[portrait_screen == 0] = 0
                pygame.surfarray.blit_array(frame_buffer, pixel_array)
                resized_screen = pygame.transform.scale(frame_buffer, (width, height))
                if color_scheme >= 150:
                    screen.blit(resized_background, (0, 0))
                screen.blit(resized_screen, (center, 0))
                pygame.display.flip()
                clock.tick(60)
            vblank = 1 - vblank
            cpu_cycles -= 16768
