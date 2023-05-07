from PIL import Image, ImageSequence

# Open the GIF file
gif = Image.open("G:\Projects\D.M\static\images\left.gif")

# Create a new sequence of GIF frames
new_frames = []

# Iterate over each frame in the GIF
for frame in ImageSequence.Iterator(gif):
    # Reduce the colors in the frame
    frame = frame.quantize(colors=256)

    # Add the frame to the new sequence
    new_frames.append(frame)

# Create a new GIF image from the compressed frames
new_gif = new_frames[0]
new_gif.save("compressed.gif", save_all=True, append_images=new_frames[1:], optimize=True, duration=100, loop=0)
