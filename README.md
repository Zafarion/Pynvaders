# Pynvaders
Just a Python Space Invaders emulator, but you can select some options (mono colored, inverted colors, with some colors, with more colors, with background image, etc) before the game starts. 

IMAGES:

![](https://github.com/Zafarion/Pynvaders/blob/6c17577b0d614c464bc79d6e68859a7b3bc86d2d/pics/PyInvaders0.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders1.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders2.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders3.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders4.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders5.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders6.png)
![](https://github.com/Zafarion/Pynvaders/blob/b40945d2a334e4a5596a4c1bd62e3b2ea73848aa/pics/Pyvaders7.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders8.png)
![](https://github.com/Zafarion/Pynvaders/blob/6c17577b0d614c464bc79d6e68859a7b3bc86d2d/pics/PyInvaders9.png)
![](https://github.com/Zafarion/Pynvaders/blob/6c17577b0d614c464bc79d6e68859a7b3bc86d2d/pics/PyInvaders10.png)
![](https://github.com/Zafarion/Pynvaders/blob/6c17577b0d614c464bc79d6e68859a7b3bc86d2d/pics/PyInvaders11.png)

INSTRUCTIONS


Insert Coin: SPACE

Player 1 Start: W

Player 1 Move Left: A

Player 1 Move Right:  D

Player 1 Shoot:  S

Player 2 Start: UP ARROW

Player 2 Left: LEFT ARROW

Player 2 Right: RIGHT ARROW

Player 2 Shoot: DOWN ARROW.


UPDATE (28/06/2026):

Major changes in this release.

First, I decided to implement the full Intel 8080 instruction set. Previously, I had only coded the instructions necessary to run *Space Invaders*. Now I wanted to run i8080 ROM tests and considered reusing the code to build a Master System emulator (Z80 CPU).

After implementing the missing instructions and running the tests, I discovered several bugs in the existing instructions (though, surprisingly, *Space Invaders* had been running fine). I fixed them all and successfully passed the tests, releasing this version as 1.2 in the `PyI8080-old.py` file.

However, with the help of AI, I learned a lot about emulator programming and realized my code was terrible... It was just one massive `match/case` block to decode every opcode. I soon discovered much more elegant alternatives and decided to rewrite almost the entire codebase!

I ditched the `match/case` approach and implemented a dispatch table to decode opcodes. I also changed how the screen is rendered; previously, I drew 8 pixels every time an instruction was called to wrote a byte to VRAM. Now, for every frame, I scan the entire VRAM and convert it all into screen pixels using Surfarray—along with various other improvements.

The result is that the game now runs at double the speed, and the source code is half the length, despite now supporting three new games (ROMs not included) and three ROM tests that you can download from my repository and run immediately.

For now I decided to include support for these games: Ballon Bomber, Galaxy Wars and Lunar Rescue. I decided for these because I noticed that they use basically the same memory map, input ports & bits for button presses than space invaders. The output ports are also compatible, with some wrong/missing sounds but nothing game breaking.

The difference is that now you need to put the respective roms (same format as MAME) in these folders: Space Invaders, Balloon Bomber, Galaxy Wars and Lunar Rescue. All folders need to be in the same directory as PyI8080.exe or PyI8080.py (if you are compiling the source-code by yourself).


UPDATE (01/12/2025):

I had released only the source-code in 2022 and after that, I stopped working on this.
Now I came back with programming, made some improvements and decided to build an executable.

Whats new in this 1.0 release:

- Improved speed a lot after fixing the (mistakely) resizing of the background image on every frame. Also applied the "convert()" function on the loaded background image and this also greatly improved performance when selecting the background image option;
- Removed some "if's" from the code to also slightly improve performance;
- Made the code now count the correct number of cycles of each instruction to make the interrupts more cycle accucate and run in the real arcade speed;
- Implemented a clock tick to limit the emulator running faster than the game in the real hardware.
- Changed the code to read the Space Invaders ROM divided in 4 parts (I noticed the 4 parts ROM is more common).
  

UPDATE (12/10/2022):

- Included missing sound (lifegained.wav) and implemented code to play this sound. You need to download the new file and put in the same directory as the other sound files.
- The original arcade has switches that lets the owner set the number of lives, display coin information, score total to gain a new life/ship, etc. Now these switches can be changed on the emulator directly in the IN_PORT2 variable by just setting the starting bits. The values are explained in the beggining of the source code.
- Minor changes in the keyboard listening routine and input/output ports handling.
