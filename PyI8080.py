import pygame
import sys
import numpy as np

clock = pygame.time.Clock()
pygame.init()

# CPU registers
A = 0
B = 0
C = 0
D = 0
E = 0
H = 0
L = 0
PC = 0
SP = 0
BC = 0
DE = 0
HL = 0

# CPU flags
SIGN = False
ZERO = False
HALFCARRY = False
CARRY = False
INTERRUPT = False

# Input/Output ports
IN_PORT0 = 0b00001110 #Hardware mapped but unused

IN_PORT1 = 0b00001000 #Bit 0: Unused.
                      #Bit 1-3: Player 1 move left/right/shoot when set to 1, then reset.
                      #Bit 4: Always 1.
                      #Bit 5: Player 1 start, then reset.
                      #Bit 6: Player 2 start, then reset.
                      #Bit 7: Insert coin, then reset.

IN_PORT2 = 0b00001011 #Bit 0: Coin info displayed in demo screen (0=ON).
                      #Bit 1-3: Player 2 move left/right/shoot when set to 1, then reset.
                      #Bit 4: 0 = extra ship at 1500 points, 1 = extra ship at 1000.
                      #Bit 5: Display TILT info when set to 1.
                      #Bits 6-7: 00 = 3 ships, 01 = 4 ships,  10 = 5 ships, 11 = 6 ships.
                        
#IN_PORT3 = 0 #In the real hardware, this port always have this formula: (((OUT_PORT4HI << 8) | OUT_PORT4LO) << OUT_PORT2) >> 8. In the emulador we only calculate and add when this port is read
OUT_PORT2 = 0
OUT_PORT3 = 0
OUT_PORT4LO = 0
OUT_PORT4HI = 0
OUT_PORT5 = 0
OUT_PORT6 = 0

# Aux variables
last_OUT_PORT3 = 0
last_OUT_PORT5 = 0
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
#pixelArray = pygame.surfarray.pixels2d(frame_buffer)
#pixelArray = pygame.PixelArray(frame_buffer)
screen = pygame.display.set_mode((width, height))
center = 0
pygame.display.set_caption("Another Python Space Invaders emulator (Intel 8080 CPU). v1.0")

# Menu to choose color scheme
font = pygame.font.SysFont("Retro.ttf", 30)
screen.blit(font.render('Click in a color scheme below:', True, white), (0, 0))
screen.blit(font.render('SV version (Sprites are white. Background is black)', True, yellow), (0, 60))
screen.blit(font.render('SV with inverted colors (Sprites are black. Background is white)', True, orchid), (0, 90))
screen.blit(font.render('TV & Midway versions (Sprites are green, red and white. Background is black)', True, green), (0, 120))
screen.blit(font.render('CV version (Multicolored sprites. Background is black)', True, blue), (0, 150))
screen.blit(font.render('TV & Midway versions with wide screen and background image', True, turquoise), (0, 180))
screen.blit(font.render('CV version with wide screen and background image', True, red), (0, 210))
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
                color_scheme = pos
                click = True
                break

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

match color_scheme:
    case 60:
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][1] = white
        screen = pygame.display.set_mode((width, height))
    case 90:
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][0] = white
        screen = pygame.display.set_mode((width, height))
    case 120:
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][1] = white
        for x in range(224):
            for y in range(29, 60):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(175, 235):
                pixelColor[x][y][1] = green
        for x in range(24, 135):
            for y in range(236, 256):
                pixelColor[x][y][1] = green
        screen = pygame.display.set_mode((width, height))
        
    case 150:                      
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][1] = white
        for x in range(74):
            for y in range(21):
                pixelColor[x][y][1] = turquoise
        for x in range(74, 148):
            for y in range(29):
                pixelColor[x][y][1] = blue
        for x in range(148, 224):
            for y in range(29):
                pixelColor[x][y][1] = yellow
        for x in range(224):
            for y in range(29, 37):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(37, 46):
                pixelColor[x][y][1] = orchid
        for x in range(224):
            for y in range(46, 60):
                pixelColor[x][y][1] = blue
        for x in range(224):
            for y in range(60, 95):
                pixelColor[x][y][1] = green
        for x in range(224):
            for y in range(95, 120):
                pixelColor[x][y][1] = turquoise
        for x in range(224):
            for y in range(120, 155):
                pixelColor[x][y][1] = orchid
        for x in range(224):
            for y in range(155, 190):
                pixelColor[x][y][1] = yellow
        for x in range(224):
            for y in range(190, 210):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(210, 225):
                pixelColor[x][y][1] = turquoise
        for x in range(224):
            for y in range(225, 235):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(235, 256):
                pixelColor[x][y][1] = turquoise
        for x in range(130, 190):
            for y in range(235, 246):
                pixelColor[x][y][1] = orchid
        screen = pygame.display.set_mode((width, height))
                              
    case 180:
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][1] = white
        for x in range(224):
            for y in range(29, 60):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(175, 235):
                pixelColor[x][y][1] = green
        for x in range(24, 135):
            for y in range(236, 256):
                pixelColor[x][y][1] = green
        center = ((width * 1.5) / 2) - (width / 2)
        bg = pygame.image.load("Background.png").convert()
        frame_buffer.set_colorkey(black)
        screen = pygame.display.set_mode((width * 1.5, height))
        resized_background = pygame.transform.smoothscale(bg, (width * 1.5, height))
    case 210:
        pixelColor = np.zeros((224, 256, 2, 3))
        for x in range(224):
            for y in range(256):
                pixelColor[x][y][1] = white
        for x in range(74):
            for y in range(21):
                pixelColor[x][y][1] = turquoise
        for x in range(74, 148):
            for y in range(29):
                pixelColor[x][y][1] = blue
        for x in range(148, 224):
            for y in range(29):
                pixelColor[x][y][1] = yellow
        for x in range(224):
            for y in range(29, 37):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(37, 46):
                pixelColor[x][y][1] = orchid
        for x in range(224):
            for y in range(46, 60):
                pixelColor[x][y][1] = blue
        for x in range(224):
            for y in range(60, 95):
                pixelColor[x][y][1] = green
        for x in range(224):
            for y in range(95, 120):
                pixelColor[x][y][1] = turquoise
        for x in range(224):
            for y in range(120, 155):
                pixelColor[x][y][1] = orchid
        for x in range(224):
            for y in range(155, 190):
                pixelColor[x][y][1] = yellow
        for x in range(224):
            for y in range(190, 210):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(210, 225):
                pixelColor[x][y][1] = turquoise
        for x in range(224):
            for y in range(225, 235):
                pixelColor[x][y][1] = red
        for x in range(224):
            for y in range(235, 256):
                pixelColor[x][y][1] = turquoise
        for x in range(130, 190):
            for y in range(235, 246):
                pixelColor[x][y][1] = orchid
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

# Loading whole ROM into memory (ROM -> 0000-1FFF. RAM -> 2000-23FF. VRAM -> 2400-3FFF)
#memory = bytearray(open("invaders.h", "rb").read())
memory = bytearray(open("invaders.h", "rb").read()) + bytearray(open("invaders.g", "rb").read()) + bytearray(open("invaders.f", "rb").read()) + bytearray(open("invaders.e", "rb").read())

# Extend memory in 0x2400 bytes
for x in range(0x2400):
    memory.append(0)
    
# Function to draw a line of 8 pixels when a byte is written to memory area
def paintScreen(addr, pixels):
        
    y = (addr >> 5)
    x = ((31 - (addr % 32)) << 3)

    frame_buffer.set_at((y, x + 0), pixelColor[y][x][pixels >> 7 & 1])
    frame_buffer.set_at((y, x + 1), pixelColor[y][x][pixels >> 6 & 1])
    frame_buffer.set_at((y, x + 2), pixelColor[y][x][pixels >> 5 & 1])
    frame_buffer.set_at((y, x + 3), pixelColor[y][x][pixels >> 4 & 1])
    frame_buffer.set_at((y, x + 4), pixelColor[y][x][pixels >> 3 & 1])
    frame_buffer.set_at((y, x + 5), pixelColor[y][x][pixels >> 2 & 1])
    frame_buffer.set_at((y, x + 6), pixelColor[y][x][pixels >> 1 & 1])
    frame_buffer.set_at((y, x + 7), pixelColor[y][x][pixels >> 0 & 1])

    """with pygame.PixelArray(frame_buffer) as pixelArray:
        pixelArray[y][x + 0] = pixelColor[y][x][pixels >> 7 & 1]
        pixelArray[y][x + 1] = pixelColor[y][x][pixels >> 6 & 1]
        pixelArray[y][x + 2] = pixelColor[y][x][pixels >> 5 & 1]
        pixelArray[y][x + 3] = pixelColor[y][x][pixels >> 4 & 1]
        pixelArray[y][x + 4] = pixelColor[y][x][pixels >> 3 & 1]
        pixelArray[y][x + 5] = pixelColor[y][x][pixels >> 2 & 1]
        pixelArray[y][x + 6] = pixelColor[y][x][pixels >> 1 & 1]
        pixelArray[y][x + 7] = pixelColor[y][x][pixels >> 0 & 1]"""

    

# Função que incrementa o registrador PC e retorna o valor anterior (em outras linguagens é só fazer PC++ direto no array, mas o Python não aceita)
def IPC():
    global PC
    PC += 1
    return PC - 1

# Função que incrementa o registrador SP e retorna o valor anterior (em outras linguagens é só fazer SP++ direto no array, mas o Python não aceita)
def ISP():
    global SP
    SP += 1
    return SP - 1

# Função que decrementa o registrador SP e retorna o valor (em outras linguagens é só fazer --SP direto no array, mas o Python não aceita)
def DSP():
    global SP
    SP -= 1
    return SP

# Main loop
while not crashed:
    # Fetch opcode
    match memory[IPC()]:
        case 0x00: # NOP
            cpu_cycles += 4
        case 0xC7: # RST 0
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x0
            cpu_cycles += 11
        case 0xCF: # RST 1
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x8
            cpu_cycles += 11
        case 0xD7: # RST 2
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x10
            cpu_cycles += 11
        case 0xDF: # RST 3
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x18
            cpu_cycles += 11
        case 0xE7: # RST 4
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x20
            cpu_cycles += 11
        case 0xEF: # RST 5
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x28
            cpu_cycles += 11
        case 0xF7: # RST 6
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x30
            cpu_cycles += 11
        case 0xFF: # RST 7
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            PC = 0x38
            cpu_cycles += 11
        case 0xC3: # JMP
            PC = memory[PC] + (memory[PC + 1] << 8)
            cpu_cycles += 10
        case 0xC2: # JNZ
            if (ZERO == False): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0xCA: # JZ
            if (ZERO == True): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0xD2: # JNC
            if (CARRY == False): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0xDA: # JC
            if (CARRY == True): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0xF2: # JP
            if (SIGN == False): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0xFA: # JM
            if (SIGN == True): PC = memory[PC] + (memory[PC + 1] << 8)
            else: PC += 2
            cpu_cycles += 10
        case 0x01: # LXI,BC
            C = memory[IPC()]
            B = memory[IPC()]
            BC = (B << 8) + C
            cpu_cycles += 10
        case 0x11: # LXI,DE
            E = memory[IPC()]
            D = memory[IPC()]
            DE = (D << 8) + E
            cpu_cycles += 10
        case 0x21: # LXI,HL
            L = memory[IPC()]
            H = memory[IPC()]
            HL = (H << 8) + L
            cpu_cycles += 10
        case 0x31: # LXI,SP
            SP = memory[IPC()] + (memory[IPC()] << 8)
            cpu_cycles += 10
        case 0x3E: # MVI,A
            A = memory[IPC()]
            cpu_cycles += 7
        case 0x06: # MVI,B
            B = memory[IPC()]
            BC = (B << 8) + C
            cpu_cycles += 7
        case 0x0E: # MVI,C
            C = memory[IPC()]
            BC = (B << 8) + C
            cpu_cycles += 7
        case 0x16: # MVI,D
            D = memory[IPC()]
            DE = (D << 8) + E
            cpu_cycles += 7
        case 0x1E: # MVI,E
            E = memory[IPC()]
            DE = (D << 8) + E
            cpu_cycles += 7
        case 0x26: # MVI,H
            H = memory[IPC()]
            HL = (H << 8) + L
            cpu_cycles += 7
        case 0x2E: # MVI,L
            L = memory[IPC()]
            HL = (H << 8) + L
            cpu_cycles += 7
        case 0x36: # MVI,[HL]
            memory[HL] = memory[IPC()]
            #if (HL >= 0x2400 and HL < 0x4000):
            #Video memory written. Update screen
            paintScreen(HL - 0x2400, memory[HL])
            cpu_cycles += 10
        case 0xCD: # CALL
            memory[DSP()] = (PC + 2) >> 8
            memory[DSP()] = (PC + 2) & 0xFF
            PC = memory[PC] + (memory[PC + 1] << 8)
            cpu_cycles += 17
        case 0xC4: # CALL NZ
            if (ZERO == False):
                memory[DSP()] = (PC + 2) >> 8
                memory[DSP()] = (PC + 2) & 0xFF
                PC = memory[PC] + (memory[PC + 1] << 8)
                cpu_cycles += 17
            else:
               PC += 2
               cpu_cycles += 11
        case 0xCC: # CALL Z
            if (ZERO == True):
                memory[DSP()] = (PC + 2) >> 8
                memory[DSP()] = (PC + 2) & 0xFF
                PC = memory[PC] + (memory[PC + 1] << 8)
                cpu_cycles += 17
            else:
                PC += 2
                cpu_cycles += 11
        case 0xD4: # CALL NC
            if (CARRY == False):
                memory[DSP()] = (PC + 2) >> 8
                memory[DSP()] = (PC + 2) & 0xFF
                PC = memory[PC] + (memory[PC + 1] << 8)
                cpu_cycles += 17
            else:
                PC += 2
                cpu_cycles += 11
        case 0xDC: # CALL C
            if (CARRY == True):
                memory[DSP()] = (PC + 2) >> 8
                memory[DSP()] = (PC + 2) & 0xFF
                PC = memory[PC] + (memory[PC + 1] << 8)
                cpu_cycles += 17
            else:
                PC += 2
                cpu_cycles += 11
        case 0xC9: # RET
            PC = memory[ISP()] + (memory[ISP()] << 8)
            cpu_cycles += 10
        case 0xC0: # RET NZ
            if (ZERO is False):
                PC = memory[ISP()] + (memory[ISP()] << 8)
                cpu_cycles += 11
            else: cpu_cycles += 5
        case 0xC8: # RET Z
            if (ZERO is True):
                PC = memory[ISP()] + (memory[ISP()] << 8)
                cpu_cycles += 11
            else: cpu_cycles += 5
        case 0xD0: # RET NC
            if (CARRY is False):
                PC = memory[ISP()] + (memory[ISP()] << 8)
                cpu_cycles += 11
            else: cpu_cycles += 5
        case 0xD8: # RET C
            if (CARRY is True):
                PC = memory[ISP()] + (memory[ISP()] << 8)
                cpu_cycles += 11
            else: cpu_cycles += 5
        case 0x0A: # LDA,BC
            A = memory[BC]
            cpu_cycles += 7
        case 0x1A: # LDA,DE
            A = memory[DE]
            cpu_cycles += 7
        case 0x3A: # LDA
            A = memory[memory[IPC()] + (memory[IPC()] << 8)]
            cpu_cycles += 13
        case 0xC5: # PUSH,BC
            memory[DSP()] = B & 0xFF
            memory[DSP()] = C & 0xFF
            cpu_cycles += 11
        case 0xD5: # PUSH,DE
            memory[DSP()] = D & 0xFF
            memory[DSP()] = E & 0xFF
            cpu_cycles += 11
        case 0xE5: # PUSH,HL
            memory[DSP()] = H & 0xFF
            memory[DSP()] = L & 0xFF
            cpu_cycles += 11
        case 0xF5: # PUSH,AF
            aux = A << 8
            if (SIGN): aux = aux | 0x80
            if (ZERO): aux = aux | 0x40
            if (INTERRUPT): aux = aux | 0x20
            if (HALFCARRY): aux = aux | 0x10
            if (CARRY): aux = aux | 0x1
            memory[DSP()] = (aux >> 8) & 0xFF
            memory[DSP()] = aux & 0xFF
            cpu_cycles += 11
        case 0xC1: # POP,BC
            C = memory[ISP()]
            B = memory[ISP()]
            BC = (B << 8) + C
            cpu_cycles += 10
        case 0xD1: # POP,DE
            E = memory[ISP()]
            D = memory[ISP()]
            DE = (D << 8) + E
            cpu_cycles += 10
        case 0xE1: # POP,HL
            L = memory[ISP()]
            H = memory[ISP()]
            HL = (H << 8) + L
            cpu_cycles += 10
        case 0xF1: #POP,AF
            aux = memory[ISP()] + (memory[ISP()] << 8)
            A = (aux >> 8) & 0xFF
            SIGN = bool(aux & 0x80)
            ZERO = bool(aux & 0x40)
            INTERRUPT = bool(aux & 0x20)
            HALFCARRY = bool(aux & 0x10)
            CARRY = bool(aux & 0x1)
            cpu_cycles += 10
        case 0x77: # MOV,HL A
            memory[HL] = A & 0xFF
            if (HL >= 0x2400 and HL < 0x4000):
            #Video memory written. Update screen
                paintScreen(HL - 0x2400, memory[HL])
            cpu_cycles += 7
        case 0x70: # MOV,HL B 
            memory[HL] = B & 0xFF
            cpu_cycles += 7
        case 0x71: # MOV,HL C
            memory[HL] = C & 0xFF
            cpu_cycles += 7
        case 0x72: # MOV,HL D
            memory[HL] = D & 0xFF
            cpu_cycles += 7
        case 0x73: # MOV,HL E
            memory[HL] = E & 0xFF
            cpu_cycles += 7
        case 0x74: # MOV,HL H
            memory[HL] = H & 0xFF
            cpu_cycles += 7
        case 0x75: # MOV,HL L
            memory[HL] = L & 0xFF
            cpu_cycles += 7
        case 0x7F: # MOV,A A
            A = A
            cpu_cycles += 5
        case 0x78: # MOV,A B
            A = B
            cpu_cycles += 5
        case 0x79: # MOV,A C
            A = C
            cpu_cycles += 5
        case 0x7A: # MOV,A D
            A = D
            cpu_cycles += 5
        case 0x7B: # MOV,A E
            A = E
            cpu_cycles += 5
        case 0x7C: # MOV,A H
            A = H
            cpu_cycles += 5
        case 0x7D: # MOV,A L
            A = L
            cpu_cycles += 5
        case 0x7E: # MOV,A [HL]
            A = memory[HL]
            cpu_cycles += 7
        case 0x47: # MOV,B A
            B = A
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x40: # MOV,B B
            B = B
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x41: # MOV,B C
            B = C
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x42: # MOV,B D
            B = D
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x43: # MOV,B E
            B = E 
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x44: # MOV,B H
            B = H
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x45: # MOV,B L
            B = L
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x46: # MOV,B [HL] 
            B = memory[HL]
            BC = (B << 8) + C
            cpu_cycles += 7
        case 0x4F: # MOV,C A
            C = A
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x48: # MOV,C B
            C = B
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x49: # MOV,C C
            C = C
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x4A: # MOV,C D
            C = D 
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x4B: # MOV,C E
            C = E
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x4C: # MOV,C H
            C = H
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x4D: # MOV,C L 
            C = L
            BC = (B << 8) + C
            cpu_cycles += 5
        case 0x4E: # MOV,C [HL]
            C = memory[HL]
            BC = (B << 8) + C
            cpu_cycles += 7
        case 0x57: # MOV,D A
            D = A
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x50: # MOV,D B
            D = B
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x51: #MOV,D C
            D = C
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x52: # MOV,D D
            D = D
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x53: # MOV,D E
            D = E
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x54: # MOV,D H
            D = H
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x55: # MOV,D L
            D = L
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x56: # MOV,D [HL]
            D = memory[HL]
            DE = (D << 8) + E
            cpu_cycles += 7
        case 0x5F: # MOV,E A
            E = A
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x58: # MOV,E B
            E = B
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x59: # MOV,E C
            E = C
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x5A: # MOV,E D
            E = D
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x5B: # MOV,E E
            E = E
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x5C: # MOV,E H 
            E = H
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x5D: # MOV,E L
            E = L
            DE = (D << 8) + E
            cpu_cycles += 5
        case 0x5E: # MOV,E [HL]
            E = memory[HL]
            DE = (D << 8) + E
            cpu_cycles += 7
        case 0x67: # MOV,H A 
            H = A
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x60: # MOV,H B 
            H = B
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x61: # MOV,H C
            H = C
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x62: # MOV,H D 
            H = D
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x63: # MOV,H E
            H = E
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x64: # MOV,H H
            H = H
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x65: # MOV,H L
            H = L
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x66: # MOV,H [HL]
            H = memory[HL]
            HL = (H << 8) + L
            cpu_cycles += 7
        case 0x6F: # MOV,L A 
            L = A
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x68: # MOV,L B
            L = B
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x69: # MOV,L C
            L = C
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x6A: # MOV,L D 
            L = D
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x6B: # MOV,L E
            L = E
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x6C: # MOV,L H
            L = H
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x6D: # MOV,L L
            L = L
            HL = (H << 8) + L
            cpu_cycles += 5
        case 0x6E: # MOV,L [HL]
            L = memory[HL]
            HL = (H << 8) + L
            cpu_cycles += 7
        case 0x03: # INX,BC
            BC = (BC + 1) & 0xFFFF
            B = BC >> 8
            C = BC & 0xFF
            cpu_cycles += 5
        case 0x13: # INX,DE
            DE = (DE + 1) & 0xFFFF
            D = DE >> 8
            E = DE & 0xFF
            cpu_cycles += 5
        case 0x23: # INX,HL
            HL = (HL + 1) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 5
        case 0x33: # INX,SP
            SP = (SP + 1) & 0xFFFF
            cpu_cycles += 5
        case 0x09: # DAD HL,BC
            CARRY = ((HL + BC) > 0xFFFF)
            HL = (HL + BC) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 10
        case 0x19: # DAD HL,DE
            CARRY = ((HL + DE) > 0xFFFF)
            HL = (HL + DE) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 10
        case 0x29: # DAD HL, HL
            CARRY = ((HL + HL) > 0xFFFF)
            HL = (HL + HL) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 10
        case 0x39: # DAD HL, SP
            CARRY = ((HL + SP) > 0xFFFF)
            HL = (HL + SP) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 10
        case 0x0B: # DCX,BC
            BC = (BC - 1) & 0xFFFF
            B = BC >> 8
            C = BC & 0xFF
            cpu_cycles += 5
        case 0x1B: # DCX,DE
            DE = (DE - 1) & 0xFFFF
            D = DE >> 8
            E = DE & 0xFF
            cpu_cycles += 5
        case 0x2B: # DCX,HL
            HL = (HL - 1) & 0xFFFF
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 5
        case 0x3B: # DCX,SP
            SP = (SP - 1) & 0xFFFF
            cpu_cycles += 5
        case 0x3D: # DEC,A 
            A = (A - 1) & 0xFF
            HALFCARRY = ((A & 0xF) == 0)
            ZERO = ((A & 255) == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 5
        case 0x05: # DEC,B
            B = (B - 1) & 0xFF
            BC = (B << 8) + C
            HALFCARRY = ((B & 0xF) == 0)
            ZERO = ((B & 255) == 0)
            SIGN = bool(B & 128)
            cpu_cycles += 5
        case 0x0D: # DEC,C
            C = (C - 1) & 0xFF
            BC = (B << 8) + C
            HALFCARRY = ((C & 0xF) == 0)
            ZERO = ((C & 255) == 0)
            SIGN = bool(C & 128)
            cpu_cycles += 5
        case 0x15: # DEC,D
            D = (D - 1) & 0xFF
            DE = (D << 8) + E
            HALFCARRY = ((D & 0xF) == 0)
            ZERO = ((D & 255) == 0)
            SIGN = bool(D & 128)
            cpu_cycles += 5
        case 0x1D: # DEC,E
            E = (E - 1) & 0xFF
            DE = (D << 8) + E
            HALFCARRY = ((E & 0xF) == 0)
            ZERO = ((E & 255) == 0)
            SIGN = bool(E & 128)
            cpu_cycles += 5
        case 0x25: # DEC,H
            H = (H - 1) & 0xFF
            HL = (H << 8) + L
            HALFCARRY = ((H & 0xF) == 0)
            ZERO = ((H & 255) == 0)
            SIGN = bool(H & 128)
            cpu_cycles += 5
        case 0x2D: # DEC,L
            L = (L - 1) & 0xFF
            HL = (H << 8) + L
            HALFCARRY = ((L & 0xF) == 0)
            ZERO = ((L & 255) == 0)
            SIGN = bool(L & 128)
            cpu_cycles += 5
        case 0x35: # DEC,[HL]
            memory[HL] = (memory[HL] - 1) & 0xFF
            HALFCARRY = ((memory[HL] & 0xF) == 0)
            ZERO = ((memory[HL] & 255) == 0)
            SIGN = bool(memory[HL] & 128)
            cpu_cycles += 10
        case 0x3C: # INC,A
            A = (A + 1) & 0xFF
            HALFCARRY = ((A & 0xF) != 0)
            ZERO = ((A & 255) == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 5
        case 0x04: # INC,B
            B = (B + 1) & 0xFF
            BC = (B << 8) + C
            HALFCARRY = ((B & 0xF) != 0)
            ZERO = ((B & 255) == 0)
            SIGN = bool(B & 128)
            cpu_cycles += 5
        case 0x0C: # INC,C
            C = (C + 1) & 0xFF
            BC = (B << 8) + C
            HALFCARRY = ((C & 0xF) != 0)
            ZERO = ((C & 255) == 0)
            SIGN = bool(C & 128)
            cpu_cycles += 5
        case 0x14: # INC,D
            D = (D + 1) & 0xFF
            DE = (D << 8) + E
            HALFCARRY = ((D & 0xF) != 0)
            ZERO = ((D & 255) == 0)
            SIGN = bool(D & 128)
            cpu_cycles += 5
        case 0x1C: # INC,E
            E = (E + 1) & 0xFF
            DE = (D << 8) + E
            HALFCARRY = ((E & 0xF) != 0)
            ZERO = ((E & 255) == 0)
            SIGN = bool(E & 128)
            cpu_cycles += 5
        case 0x24: # INC,H
            H = (H + 1) & 0xFF
            HL = (H << 8) + L
            HALFCARRY = ((H & 0xF) != 0)
            ZERO = ((H & 255) == 0)
            SIGN = bool(H & 128)
            cpu_cycles += 5
        case 0x2C: # INC,L
            L = (L + 1) & 0xFF
            HL = (H << 8) + L
            HALFCARRY = ((L & 0xF) != 0)
            ZERO = ((L & 255) == 0)
            SIGN = bool(L & 128)
            cpu_cycles += 5
        case 0x34: # INC,[HL]
            memory[HL] = (memory[HL] + 1) & 0xFF
            HALFCARRY = ((memory[HL] & 0xF) != 0)
            ZERO = ((memory[HL] & 255) == 0)
            SIGN = bool(memory[HL] & 128)
            cpu_cycles += 10
        case 0xA7: # AND,A
            A = (A & A) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA0: # AND,B
            A = (A & B) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA1: # AND,C 
            A = (A & C) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA2: # AND,D 
            A = (A & D) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA3: # AND,E
            A = (A & E) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA4: # AND,H
            A = (A & H) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA5: # AND,L
            A = (A & L) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA6: # AND,[HL]
            A = (A & memory[HL]) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xE6: # AND,[PC]
            A = (A & memory[IPC()]) & 0xFF
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xAF: # XOR,A
            A = A ^ A
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA8: # XOR,B
            A = A ^ B
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xA9: # XOR,C
            A = A ^ C
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xAA: # XOR,D
            A = A ^ D
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xAB: # XOR,E
            A = A ^ E
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xAC: # XOR,H 
            A = A ^ H
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xAD: # XOR,L 
            A = A ^ L
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xAE: # XOR,[HL]
            A = A ^ memory[HL]
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xEE: # XOR,[PC]
            A = A ^ memory[IPC()]
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xB7: # OR,A
            A = A | A
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB0: # OR,B
            A = A | B
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB1: # OR,C
            A = A | C
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB2: # OR,D
            A = A | D
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB3: # OR,E
            A = A | E
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB4: # OR,H
            A = A | H
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB5: # OR,L
            A = A | L
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0xB6: # OR,[HL]
            A = A | memory[HL]
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xF6: # OR,[PC]
            A = A | memory[IPC()]
            CARRY = False
            HALFCARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0x87: # ADD,A 
            aux = (A + A) & 0xFF
            HALFCARRY = bool((A ^ A ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x80: # ADD,B
            aux = (A + B) & 0xFF
            HALFCARRY = bool((A ^ B ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x81: # ADD,C
            aux = (A + C) & 0xFF
            HALFCARRY = bool((A ^ C ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x82: # ADD,D
            aux = (A + D) & 0xFF
            HALFCARRY = bool((A ^ D ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x83: # ADD,E
            aux = (A + E) & 0xFF
            HALFCARRY = bool((A ^ E ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x84: # ADD,H
            aux = (A + H) & 0xFF
            HALFCARRY = bool((A ^ H ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x85: # ADD,L
            aux = (A + L) & 0xFF
            HALFCARRY = bool((A ^ L ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x86: # ADD,[HL]
            aux = (A + memory[HL]) & 0xFF
            HALFCARRY = bool((A ^ memory[HL] ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xC6: # ADD,[PC]
            aux = (A + memory[PC]) & 0xFF
            HALFCARRY = bool((A ^ memory[IPC()] ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0x8F: # ADC,A
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + A + aux2) & 0xFF
            HALFCARRY = bool((A ^ A ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x88: # ADC,B
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + B + aux2) & 0xFF
            HALFCARRY = bool((A ^ B ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x89: # ADC,C
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + C + aux2) & 0xFF
            HALFCARRY = bool((A ^ C ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x8A: # ADC,D
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + D + aux2) & 0xFF
            HALFCARRY = bool((A ^ D ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x8B: # ADC,E
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + E + aux2) & 0xFF
            HALFCARRY = bool((A ^ E ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x8C: # ADC,H
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + H + aux2) & 0xFF
            HALFCARRY = bool((A ^ H ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x8D: # ADC,L
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + L + aux2) & 0xFF
            HALFCARRY = bool((A ^ L ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x8E: # ADC,[HL]
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + memory[HL] + aux2) & 0xFF
            HALFCARRY = bool((A ^ memory[HL] ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xCE: # ADC,[PC]
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A + memory[PC] + aux2) & 0xFF
            HALFCARRY = bool((A ^ memory[IPC()] ^ aux) & 0x10)
            A = aux
            CARRY = (aux > 255)
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0x97: # SUB,A
            aux = (A - A) & 0xFF
            CARRY = (aux >= A) and bool(A)
            HALFCARRY = bool((A ^ A ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x90: # SUB,B
            aux = (A - B) & 0xFF
            CARRY = (aux >= A) and bool(B)
            HALFCARRY = bool((A ^ B ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x91: # SUB,C
            aux = (A - C) & 0xFF
            CARRY = (aux >= A) and bool(C)
            HALFCARRY = bool((A ^ C ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x92: # SUB,D
            aux = (A - D) & 0xFF
            CARRY = (aux >= A) and bool(D)
            HALFCARRY = bool((A ^ D ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x93: # SUB,E
            aux = (A - E) & 0xFF
            CARRY = (aux >= A) and bool(E)
            HALFCARRY = bool((A ^ E ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x94: # SUB,H
            aux = (A - H) & 0xFF
            CARRY = (aux >= A) and bool(H)
            HALFCARRY = bool((A ^ H ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x95: # SUB,L
            aux = (A - L) & 0xFF
            CARRY = (aux >= A) and bool(L)
            HALFCARRY = bool((A ^ L ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x96: # SUB,[HL]
            aux = (A - memory[HL]) & 0xFF
            CARRY = (aux >= A) and bool(memory[HL])
            HALFCARRY = bool((A ^ memory[HL] ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xD6: # SUB,[PC]
            aux = (A - memory[PC]) & 0xFF
            CARRY = (aux >= A) and bool(memory[PC])
            HALFCARRY = bool((A ^ memory[IPC()] ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xDE: # SBBI
            if (CARRY): aux2 = 1
            else: aux2 = 0
            aux = (A - memory[PC] - aux2) & 0xFF
            CARRY = (aux >= A) and bool(memory[PC] | aux2)
            HALFCARRY = bool((A ^ memory[IPC()] ^ aux) & 0x10)
            A = aux
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 7
        case 0xBF: # CMP,A
            aux = (A - A) & 0xFF
            CARRY = (aux >= A) and bool(A)
            HALFCARRY = bool((A ^ A ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xB8: # CMP,B
            aux = (A - B) & 0xFF
            CARRY = (aux >= A) and bool(B)
            HALFCARRY = bool((A ^ B ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xB9: # CMP,C
            aux = (A - C) & 0xFF
            CARRY = (aux >= A) and bool(C)
            HALFCARRY = bool((A ^ C ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xBA: # CMP,D
            aux = (A - D) & 0xFF
            CARRY = (aux >= A) and bool(D)
            HALFCARRY = bool((A ^ D ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xBB: # CMP,E
            aux = (A - E) & 0xFF
            CARRY = (aux >= A) and bool(E)
            HALFCARRY = bool((A ^ E ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xBC: # CMP,H
            aux = (A - H) & 0xFF
            CARRY = (aux >= A) and bool(H)
            HALFCARRY = bool((A ^ H ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xBD: # CMP,L
            aux = (A - L) & 0xFF
            CARRY = (aux >= A) and bool(L)
            HALFCARRY = bool((A ^ L ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 4
        case 0xBE: # CMP,[HL]
            aux = (A - memory[HL]) & 0xFF
            CARRY = (aux >= A) and bool(memory[HL])
            HALFCARRY = bool((A ^ memory[HL] ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 7
        case 0xFE: # CMP,[PC]
            aux = (A - memory[PC]) & 0xFF
            CARRY = (aux >= A) and bool(memory[PC])
            HALFCARRY = bool((A ^ memory[IPC()] ^ aux) & 0x10)
            ZERO = (aux == 0)
            SIGN = bool(aux & 128)
            cpu_cycles += 7
        case 0xEB: # XCHG,DE<->HL
            aux = DE
            DE = HL
            D = DE >> 8
            E = DE & 0xFF
            HL = aux
            H = HL >> 8
            L = HL & 0xFF
            cpu_cycles += 5
        case 0xE3: # XTHL, HL<->[SP]
            aux = H
            H = memory[SP + 1]
            memory[SP + 1] = aux
            aux = L
            L = memory[SP]
            memory[SP] = aux
            HL = (H << 8) + L
            cpu_cycles += 18
        case 0xD3: # OUTP A
            match memory[IPC()]:
                case 2:
                    OUT_PORT2 = A
                case 3:
                    OUT_PORT3 = A
                    if (OUT_PORT3 & 0x1) and not (last_OUT_PORT3 & 0x1):
                        ufo_highpitch.play(-1)
                    if not (OUT_PORT3 & 0x1) and (last_OUT_PORT3 & 0x1):
                        ufo_highpitch.stop()
                    if (OUT_PORT3 & 0x2) and not (last_OUT_PORT3 & 0x2):
                        invaderkilled.play()
                    if (OUT_PORT3 & 0x4) and not (last_OUT_PORT3 & 0x4):
                        explosion.play()
                    if (OUT_PORT3 & 0x8) and not (last_OUT_PORT3 & 0x8):
                        shoot.play()
                    if (OUT_PORT3 & 0x10) and not (last_OUT_PORT3 & 0x10):
                        lifegained.play()
                    last_OUT_PORT3 = OUT_PORT3
                    #OUT_PORT3 &= 0b10000000 #O bit do som correspondente deve ser zerado após tocar (exceto o MSB), porém no emulador não fez diferença zerá-lo, então deixei comentado.
                case 4:
                    OUT_PORT4LO = OUT_PORT4HI
                    OUT_PORT4HI = A   
                case 5:
                    OUT_PORT5 = A
                    if (OUT_PORT5 & 0x1) and not(last_OUT_PORT5 & 0x1):
                        fastinvader3.play()
                    if (OUT_PORT5 & 0x2) and not(last_OUT_PORT5 & 0x2):
                        fastinvader4.play()
                    if (OUT_PORT5 & 0x4) and not(last_OUT_PORT5 & 0x4):
                        fastinvader1.play()
                    if (OUT_PORT5 & 0x8) and not(last_OUT_PORT5 & 0x8):
                        fastinvader2.play()
                    if (OUT_PORT5 & 0x10) and not(last_OUT_PORT5 & 0x10):
                        ufo_lowpitch.play()
                    last_OUT_PORT5 = OUT_PORT5
                    #OUT_PORT5 = 0 #O bit do som correspondente deve ser zerado após tocar, porém no emulador não fez diferença zerá-lo, então deixei comentado.
                case 6:
                    OUT_PORT6 = A
                case _:
                    crashed = True
                    print("Undefined Output port: ", memory[PC - 1])
            cpu_cycles += 10 
        case 0xDB: # INP A
            match memory[IPC()]:
                case 0:
                    A = IN_PORT0
                case 1:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    keycode = pygame.key.get_pressed()
                    if keycode[pygame.K_SPACE]:# Insert coin
                        IN_PORT1 |= 0x1
                    if keycode[pygame.K_w]:    # Player 1 Start
                        IN_PORT1 |= 0x4
                    if keycode[pygame.K_DOWN]:  # Player 2 Start (need 2 or more coins)
                        IN_PORT1 |= 0x2
                    if keycode[pygame.K_a]:  # Player 1 move left
                        IN_PORT1 |= 0x20
                    if keycode[pygame.K_d]: # Player 1 move right
                        IN_PORT1 |= 0x40
                    if keycode[pygame.K_s]: # Player 1 shoot
                        IN_PORT1 |= 0x10
                        
                    A = IN_PORT1
                    IN_PORT1 &= 0b10001000
        
                case 2:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    keycode = pygame.key.get_pressed()
                    if keycode[pygame.K_LEFT]:  # Player 2 move left
                        IN_PORT2 |= 0x20
                    if keycode[pygame.K_RIGHT]: # Player 2 move right
                        IN_PORT2 |= 0x40
                    if keycode[pygame.K_DOWN]: # Player 2 shoot
                        IN_PORT2 |= 0x10
                        
                    A = IN_PORT2
                    IN_PORT2 &= 0b10001111
                    
                case 3:
                    A = (((OUT_PORT4HI << 8) | OUT_PORT4LO) << OUT_PORT2) >> 8
                case _:
                    crashed = True
                    print("Undefined Input port: ", memory[PC - 1])
            cpu_cycles += 10
        case 0xE9: # PCHL, PC<-HL
            PC = HL
            cpu_cycles += 5
        case 0xF9: # SPHL, SP<-HL
            SP = HL
            cpu_cycles += 5
        case 0x07: # RLC A
            A = (A << 1) | (A >> 7)
            CARRY = bool(A & 0x1)
            cpu_cycles += 4
        case 0x17: # RAL A
            aux = A
            A = A << 1
            if (CARRY): A = A | 0x1
            CARRY = bool(aux & 0x80)
            cpu_cycles += 4
        case 0x0F: # RRC A
            A = (A >> 1) | (A << 7)
            CARRY = bool(A & 0x80)
            cpu_cycles += 4
        case 0x1F: # RAR A
            aux = A
            A = A >> 1
            if (CARRY): A = A | 0x80
            CARRY = bool(aux & 0x1)
            cpu_cycles += 4
        case 0x02: # STA BC
            memory[BC] = A & 0xFF
            cpu_cycles += 7
        case 0x12: # STA DE
            memory[DE] = A & 0xFF
            cpu_cycles += 7
        case 0x32: # STA [PC]
            aux = memory[IPC()] + (memory[IPC()] << 8)
            memory[aux] = A & 0xFF
            cpu_cycles += 13
        case 0xF3: # DI
            INTERRUPT = False
            cpu_cycles += 4
        case 0xFB: # EI
            INTERRUPT = True
            cpu_cycles += 4
        case 0x37: # STC
            CARRY = True
            cpu_cycles += 4
        case 0x3F: # CMC
            CARRY = not CARRY
            cpu_cycles += 4
        case 0x2A: # LHLD
            aux = memory[IPC()] + (memory[IPC()] << 8)
            L = memory[aux]
            H = memory[aux + 1]
            HL = (H << 8) + L
            cpu_cycles += 16
        case 0x22: # SHLD
            aux = memory[IPC()] + (memory[IPC()] << 8)
            memory[aux] = L
            memory[aux + 1] = H
            cpu_cycles += 16
        case 0x27: # DAA
            if (((A & 0xF) > 9) or HALFCARRY):
                A += 0x6
                HALFCARRY = True
            else:
                HALFCARRY = False
            if ((A > 0x9F) or CARRY):
                A += 0x60
                CARRY = True
            else:
                CARRY = False
            ZERO = (A == 0)
            SIGN = bool(A & 128)
            cpu_cycles += 4
        case 0x2F: # CMA
            A = A ^ 255
            cpu_cycles += 4
        case _:
            crashed = True
            print("Undefined opcode: ", hex(memory[PC - 1]))

    # Debug Stuff
    #print(cpu_cycles, 'PC:', hex(PC), 'SP:', hex(SP), 'BC:', hex(BC), 'DE:', hex(DE), 'HL:', hex(HL))
    #input()

    # Interrupt stuff
    if cpu_cycles >= 16768:
        if INTERRUPT: 
            memory[DSP()] = PC >> 8
            memory[DSP()] = PC & 0xFF
            INTERRUPT = False
            if not vblank:
                PC = 0x8
                """resized_screen = pygame.transform.scale(frame_buffer, (width, height))
                if color_scheme >= 180:
                    screen.blit(resized_background, (0, 0), (0, 0, width + (center * 2), height / 2))
                screen.blit(resized_screen, (0, 0), (0, 0, width, height / 2))
                pygame.display.update(0, 0, width + (center * 2), height / 2)"""                
            else:
                PC = 0x10
                """resized_screen = pygame.transform.scale(frame_buffer, (width, height))
                if color_scheme >= 180:
                    screen.blit(resized_background, (0, height / 2), (0, height / 2, width + (center * 2), height / 2))
                screen.blit(resized_screen, (center, height / 2), (0, height / 2, width + (center * 2), height / 2))
                pygame.display.update(0, height / 2, width + (center * 2), height / 2)"""
                
                resized_screen = pygame.transform.scale(frame_buffer, (width, height))
                if color_scheme >= 180:
                    screen.blit(resized_background, (0, 0))
                screen.blit(resized_screen, (center, 0))
                pygame.display.flip()
                clock.tick(60)
            vblank = 1 - vblank
            cpu_cycles = 0

            

        
