import pygame, os
from settings import DATA_PATH

def load_img(name, scale=None, height=None):
    path = os.path.join(DATA_PATH, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if height:
            w, h = img.get_size()
            scale = (int(height * (w / h)), height)
        if scale: img = pygame.transform.smoothscale(img, scale)
        return img
    return None

def draw_button(surface, img, rect, mouse_pos):
    if img is None: return
    if rect.collidepoint(mouse_pos):
        w, h = img.get_size()
        zoomed = pygame.transform.smoothscale(img, (int(w * 1.1), int(h * 1.1)))
        surface.blit(zoomed, zoomed.get_rect(center=rect.center))
    else:
        surface.blit(img, rect)