# setup
1. the first section handles events that currently means if a quit is triggered the program stops
2. the second section would handle frame updates there aren't any programmed yet so it's not doing anything
3. the third section fills the screen and pushes it to the display it also sets the tick update speed of the game
4. the sections have to happen in this order because if a quit is triggered and resources are being used you don't want the quit block to get skipped, the updates then happen because you don't want your game to be a frame behind what the player sees, after that the frame is displayed to the screen
# 2A
1. when the circle reaches the edge the velocity inverts causing it's velocity to invert in the other direction depending on which side was hit
# 2C
1. the print fires 60 times a second because the update rate of the program is 60 frames per second
# 3A
1. when the mouse is pressed particles are spawned and a random vector is generated with randint this is combined with a number for gravity as well to result in an arc away from the mouse
# 3B