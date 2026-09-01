from pathlib import Path
from PIL import Image, ImageDraw

out = Path('D:/Hermes/cache/images/scene_template_programmatic_3840x2160.png')
W, H = 3840, 2160
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
wall = (48, 55, 65)
floor = (238, 231, 216)
wood = (150, 105, 65)
blue = (91, 133, 170)
dark = (42, 45, 50)
steel = (170, 178, 184)
green = (72, 145, 78)
red = (190, 85, 65)
x0, y0, x1, y1 = 220, 180, 3620, 1980
# One continuous open-plan room.
d.rectangle((x0, y0, x1, y1), fill=floor, outline=wall, width=34)
d.rectangle((x0 + 34, y0 + 34, 1900, y1 - 34), fill=(244, 238, 226))
d.rectangle((1940, y0 + 34, x1 - 34, y1 - 34), fill=(242, 237, 226))
d.line((1920, y0 + 40, 1920, y1 - 40), fill=(205, 194, 176), width=8)
# Living room: one television, cabinet, sofa, and coffee table.
d.rectangle((350, 350, 900, 520), fill=wood, outline=dark, width=10)
d.rectangle((470, 265, 780, 350), fill=dark, outline=dark, width=8)
d.rounded_rectangle((420, 1250, 1480, 1570), radius=35, fill=(215, 210, 198), outline=dark, width=10)
d.rectangle((500, 1300, 1400, 1450), fill=(226, 222, 211))
d.rectangle((650, 780, 1250, 1040), fill=wood, outline=dark, width=10)
# One window and one vine landmark.
d.rectangle((1200, 180, 1750, 250), fill=(185, 215, 230), outline=dark, width=10)
d.line((1400, 250, 1400, 430), fill=green, width=16)
d.ellipse((1365, 330, 1435, 400), fill=green)
d.ellipse((1425, 390, 1495, 460), fill=green)
# One continuous kitchen counter with one sink, stove, refrigerator, board.
d.rectangle((2360, 360, 3420, 560), fill=(220, 220, 214), outline=dark, width=10)
d.rectangle((2500, 410, 2740, 500), fill=steel, outline=dark, width=8)
d.rectangle((2920, 390, 3200, 540), fill=dark, outline=dark, width=8)
d.ellipse((2990, 425, 3070, 505), fill=(90, 90, 90))
d.rectangle((3230, 360, 3420, 1050), fill=steel, outline=dark, width=10)
d.rectangle((2780, 425, 2880, 510), fill=wood, outline=dark, width=8)
# One pot and one strainer at the one stove.
d.ellipse((2960, 420, 3160, 560), fill=(110, 115, 120), outline=dark, width=8)
d.ellipse((3200, 620, 3350, 760), outline=dark, width=12)
# One dining table and four chairs.
d.rectangle((1980, 980, 3000, 1540), fill=blue, outline=dark, width=12)
for bx, by in ((1860, 1060), (1860, 1390), (3060, 1060), (3060, 1390)):
    d.rectangle((bx, by, bx + 150, by + 170), fill=wood, outline=dark, width=8)
# Prep -> shaping -> tray -> stove -> dining path.
d.ellipse((2070, 1080, 2290, 1300), fill=(205, 175, 135), outline=dark, width=8)
d.rectangle((2320, 1080, 2460, 1200), fill=(248, 246, 235), outline=dark, width=8)
d.line((2500, 1220, 2730, 1220), fill=wood, width=30)
d.rectangle((2600, 1320, 2850, 1450), outline=dark, width=8)
for i in range(5):
    d.ellipse((2090 + i * 90, 1390, 2160 + i * 90, 1460), fill=(238, 238, 225), outline=dark, width=5)
# Reserved entrance-side area for Zhou Ye's bag.
d.rectangle((500, 1720, 850, 1900), fill=(55, 75, 105), outline=dark, width=10)
# Three portal-only connections: entrance, bedroom, bathroom. Blank beyond.
d.rectangle((950, 1940, 1350, 1990), fill='white', outline=wall, width=10)
d.rectangle((2350, 170, 2750, 220), fill='white', outline=wall, width=10)
d.rectangle((2850, 170, 3250, 220), fill='white', outline=wall, width=10)
# One camera marker for downstream staging.
d.ellipse((1660, 820, 1740, 900), fill=red)
d.line((1700, 900, 1700, 1080), fill=red, width=12)
d.polygon(((1660, 1060), (1740, 1060), (1700, 1140)), fill=red)
im.save(out, 'PNG', optimize=True)
print(out)
print(im.size)
print(out.stat().st_size)
