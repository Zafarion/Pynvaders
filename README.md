# Pynvaders
Just a Python Space Invaders emulator, but you can select some options (mono colored, inverted colors, with some colors, with more colors, with background image, etc) before the game starts. 

IMAGES:

![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders1.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders2.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders3.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders4.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders5.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders6.png)
![](https://github.com/Zafarion/Pynvaders/blob/b40945d2a334e4a5596a4c1bd62e3b2ea73848aa/pics/Pyvaders7.png)
![](https://github.com/Zafarion/Pynvaders/blob/53cc0942e0f83948283f7de4293eac1553ba94ad/pics/Pyvaders8.png)

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


UPDATE (01/12/2025):
I released just the source-code in 2022 and after stopped working on this.
Now I came back with programming, made some improvements and decided to build an executable.

New with this 1.0 release:

- Improved speed a lot after fixing the (wrongly) resizing of the background image on every frame. Also applied the "convert()" function on the loaded background image and this also greatly improved performance when selecting the background image option;
- Removed some "if's" from the code to also slightly improve performance;
- Made the code count the correct number of cycles of each instruction to make the interrupts more cycle accucate and run in the real arcade speed;
- Implemented a clock tick to limit the emulator running faster than the game in the real hardware.
- Changed the code to read the Space Invaders ROM divided in 4 parts (I noticed the 4 parts ROM is more common).
  

UPDATE (12/10/2022):
- Included missing sound (lifegained.wav) and implemented code to play this sound. You need to download the new file and put in the same directory as the other sound files.
- The original arcade has switches that lets the owner set the number of lives, display coin information, score total to gain a new life/ship, etc. Now these switches can be changed on the emulator directly in the IN_PORT2 variable by just setting the starting bits. The values are explained in the beggining of the source code.
- Minor changes in the keyboard listening routine and input/output ports handling.
