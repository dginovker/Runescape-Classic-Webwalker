from PIL import Image

pixels = None
def walkable_tile(coords):
    global pixels
    if not pixels:
      img = Image.open("./map.png")
      pixels = img.load()
    
    # Extract the coordinates
    x, y = coords
    x = 900 - x
    
    # Get the color of the tile at the given coordinates
    color = pixels[x, y]
    
    # Determine if the tile is walkable (not black)
    return color != 0
