import pygame
import os
import numpy as np
import sys
import time
import string 
import random 
import asyncio

# ====================================================================
# I. 初期設定とパス・定数定義
# ====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(*relative_paths):
    return os.path.join(BASE_DIR, *relative_paths)

def load_word_list(filename):
    path = get_path(filename)
    default_words = ["banana", "carrot", "strawberry", "hamburger", "milk", "ketchup", "pudding", "sandwich", "waffle", "chocolate"]
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
            return words if words else default_words
        else:
            return default_words
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return default_words

pygame.init()
pygame.mixer.init() 

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("あぶくどタイピング")
clock = pygame.time.Clock()

# カラー定義
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(150,150,150)
DARK_GRAY=(80,80,80); BLUE=(0,100,200); LIGHT_BLUE=(173,216,230) 
RED=(200,0,0); GREEN=(0,150,0); ORANGE=(255,165,0); PURPLE=(128,0,128)
BLUE_LIGHT=(100,150,255); RED_LIGHT=(255,100,100); YELLOW=(255,255,0)
DARK_GREEN=(0, 100, 0); BROWN=(139, 69, 19)

# フォント設定
font_path = get_path('NotoSansJP-VariableFont_wght.ttf')
font_path_phonetic = get_path('AglaiaPhoneticSymbol.ttf')

try:
    font_small=pygame.font.Font(font_path, 30)
    font_medium=pygame.font.Font(font_path, 38) 
    font_large=pygame.font.Font(font_path, 60)
    font_extra_large=pygame.font.Font(font_path, 90)
    font_timer=pygame.font.Font(font_path, 50) 
    font_replay_button = pygame.font.Font(font_path, 20) 
    font_pass_button = pygame.font.Font(font_path, 28)
    font_menu_title = pygame.font.Font(font_path, 70)
    font_small_ph = pygame.font.Font(font_path_phonetic, 30)
    font_medium_ph = pygame.font.Font(font_path_phonetic, 45)
    font_score = pygame.font.Font(font_path, 45)
    font_score.set_bold(True)
except:
    font_small=pygame.font.SysFont(None, 35); font_medium=pygame.font.SysFont(None, 50)
    font_large=pygame.font.SysFont(None, 70); font_extra_large=pygame.font.SysFont(None, 100)
    font_timer=pygame.font.SysFont(None, 60); font_small_ph = font_small; font_medium_ph = font_medium
    font_replay_button = pygame.font.SysFont(None, 25); font_menu_title = pygame.font.SysFont(None, 80)
    font_pass_button = font_replay_button
    font_score = pygame.font.SysFont(None, 55)

# ディレクトリ設定
SOUNDS_DIR = 'Sounds'
SHORT_VOWEL_DIR = get_path(SOUNDS_DIR, 'short')
LONG_VOWEL_DIR = get_path(SOUNDS_DIR, 'long')
WORD_SOUND_DIR = get_path(SOUNDS_DIR, 'word')
OTHER_SOUND_DIR = get_path(SOUNDS_DIR, 'Other')
RESULT_SOUND_DIR = get_path(SOUNDS_DIR, 'result')
IMAGE_DIR = 'image'
WORDS_IMG_DIR = get_path(IMAGE_DIR, 'words')

class DummySound:
    def play(self, loops=0): pass
    def stop(self): pass

def load_sound_safe(path):
    try:
        if os.path.exists(path): return pygame.mixer.Sound(path)
        return DummySound()
    except: return DummySound()

HIT_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'hit.ogg'))
MISS_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'miss.ogg'))
CORRECT_WORD_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'correct.ogg'))
CLICK_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'coin.ogg'))
CHOICE_MUSIC = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'ChoiceMusic.ogg'))
DOORBELL_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'Doorbell.ogg'))
LOW_BOING_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'LowBoing.ogg'))
SQUEAKY_TOY_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'SqueakyToy.ogg'))
OPENING_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'opening.ogg'))
CLEAR_SOUND = load_sound_safe(os.path.join(OTHER_SOUND_DIR, 'clear.ogg'))

RESULT_SOUNDS = {k: load_sound_safe(os.path.join(RESULT_SOUND_DIR, f'{v}.ogg')) for k, v in 
                 [('amazing','amaging'),('excellent','Excellent'),('verygood','VeryGood'),('good','good'),('poor','poor'),('ohmygod','OhMyGod')]}

WORD_LIST = load_word_list('words.txt')

# モード・ステート定義
MODE_ABC="ABC_ORDER"; MODE_ABC_PHONICS="ABC_PHONICS"; MODE_LONG_VOWEL="LONG_VOWEL" 
MODE_RANDOM="RANDOM"; MODE_WORD="WORD"; MODE_WORD_TEST="WORD_TEST"
STATE_TITLE=0; STATE_GAME=1; STATE_TRANSITION=2; STATE_RESULT=3; STATE_WORD_MENU=4
TRANSITION_DURATION = 1000 

ALPHABET_DATA = [
    ("A", "æ", "a.ogg"), ("B", "b", "d.ogg"), ("C", "k", "c.ogg"), ("D", "d", "d.ogg"), 
    ("E", "e", "e.ogg"), ("F", "f", "f.ogg"), ("G", "g", "g.ogg"), ("H", "h", "h.ogg"), 
    ("I", "ɪ", "i.ogg"), ("J", "dʒ", "j.ogg"), ("K", "k", "k.ogg"), ("L", "l", "l.ogg"), 
    ("M", "m", "m.ogg"), ("N", "n", "n.ogg"), ("O", "ɒ", "o.ogg"), ("P", "p", "p.ogg"), 
    ("Q", "kw", "q.ogg"), ("R", "r", "r.ogg"), ("S", "s", "s.ogg"), ("T", "t", "t.ogg"), 
    ("U", "ʌ", "u.ogg"), ("V", "v", "v.ogg"), ("W", "w", "w.ogg"), ("X", "ks", "x.ogg"), 
    ("Y", "j", "y.ogg"), ("Z", "z", "z.ogg")
]
ALPHABET_LIST = list(string.ascii_uppercase)

PHONIC_SOUNDS = {}
for char in ALPHABET_LIST:
    PHONIC_SOUNDS[char] = load_sound_safe(os.path.join(SHORT_VOWEL_DIR, f'S-{char}.ogg'))
    PHONIC_SOUNDS[f"LONG_{char}"] = load_sound_safe(os.path.join(LONG_VOWEL_DIR, f'L-{char}.ogg'))

# 画像読み込み設定
BG_DIR = get_path(IMAGE_DIR, 'Background')
RABBIT_DIR = get_path(IMAGE_DIR, 'Rabbit')
SHORT_IMG_DIR = get_path(IMAGE_DIR, 'Short')
LONG_IMG_DIR = get_path(IMAGE_DIR, 'Long')
OTHER_IMG_DIR = get_path(IMAGE_DIR, 'Other')

def load_img(path, size_or_tuple):
    try:
        raw = pygame.image.load(path).convert_alpha()
        size = (size_or_tuple, size_or_tuple) if isinstance(size_or_tuple, int) else size_or_tuple
        return pygame.transform.scale(raw, size)
    except: return None

PHONETIC_IMAGES_SHORT = {}; PHONETIC_IMAGES_LONG = {}; PHONETIC_IMAGE_SIZE = 100 
for char, _, _ in ALPHABET_DATA:
    PHONETIC_IMAGES_SHORT[char] = load_img(os.path.join(SHORT_IMG_DIR, f's-{char.lower()}.webp'), PHONETIC_IMAGE_SIZE)
    PHONETIC_IMAGES_LONG[char] = load_img(os.path.join(LONG_IMG_DIR, f'L-{char.lower()}.webp'), PHONETIC_IMAGE_SIZE)

BIRD_SIZE = 200 
img_bird1 = load_img(os.path.join(OTHER_IMG_DIR, "bird_fly1.webp"), BIRD_SIZE)
img_bird2 = load_img(os.path.join(OTHER_IMG_DIR, "bird_fly2.webp"), BIRD_SIZE)
img_bird_sing1 = load_img(os.path.join(OTHER_IMG_DIR, "bird_sing1.webp"), BIRD_SIZE * 2)
img_bird_sing2 = load_img(os.path.join(OTHER_IMG_DIR, "bird_sing2.webp"), BIRD_SIZE * 2)

RABBIT_ICON_SIZE=210; FEEDBACK_IMG_SIZE=200; MOVEMENT_SPEED=0.1; EAT_THRESHOLD=5.0 
ANIMATION_DELAY=10; EAT_DURATION=30; CRY_DURATION=60; EARS_UP_ICON_SIZE=80 
STATE_STAND=0; STATE_MOVING_1=1; STATE_MOVING_2=2; STATE_EAT=3
STATE_MOVING_LEFT_1 = 4; STATE_MOVING_LEFT_2 = 5 
STATE_CRY = 6; STATE_JUMP = 7 
FEEDBACK_NEUTRAL="NEUTRAL"; FEEDBACK_CORRECT="CORRECT"; FEEDBACK_INCORRECT="INCORRECT"
FEEDBACK_DURATION_MISS=60; FEEDBACK_DURATION_CORRECT=30
CARROT_ICON_SIZE = RABBIT_ICON_SIZE // 2 

KEY_W=80; KEY_H=80
KEYBOARD_LAYOUT = [['q','w','e','r','t','y','u','i','o','p'],['a','s','d','f','g','h','j','k','l'],['z','x','c','v','b','n','m']]
KEYBOARD_START_X=(SCREEN_WIDTH - len(KEYBOARD_LAYOUT[0]) * KEY_W) // 2
KEYBOARD_START_Y=SCREEN_HEIGHT // 2 - 40 
HAND_Y=KEYBOARD_START_Y + KEY_H * 3 + 45; FINGER_SIZE=30
LEFT_HAND_BASE_X=SCREEN_WIDTH // 2 - 250
LEFT_HAND_POSITIONS = {'Pinky': (LEFT_HAND_BASE_X, HAND_Y), 'Ring': (LEFT_HAND_BASE_X + 60, HAND_Y - 20), 'Middle': (LEFT_HAND_BASE_X + 120, HAND_Y - 30), 'Index': (LEFT_HAND_BASE_X + 180, HAND_Y - 20)}
RIGHT_HAND_BASE_X=SCREEN_WIDTH // 2 + 250
RIGHT_HAND_POSITIONS = {'Index': (RIGHT_HAND_BASE_X - 180, HAND_Y - 20), 'Middle': (RIGHT_HAND_BASE_X - 120, HAND_Y - 30), 'Ring': (RIGHT_HAND_BASE_X - 60, HAND_Y - 20), 'Pinky': (RIGHT_HAND_BASE_X, HAND_Y)}
KEY_MAP = {
    'a': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Pinky'}, 's': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Ring'}, 'd': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Middle'}, 'f': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'}, 'g': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'},
    'h': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}, 'j': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}, 'k': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Middle'}, 'l': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Ring'}, 
    'q': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Pinky'}, 'w': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Ring'}, 'e': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Middle'}, 'r': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'}, 't': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'},
    'y': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}, 'u': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}, 'i': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Middle'}, 'o': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Ring'}, 'p': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Pinky'},
    'z': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Pinky'}, 'x': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Ring'}, 'c': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Middle'}, 'v': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'}, 'b': {'hand': 'LEFT', 'color': BLUE_LIGHT, 'finger': 'Index'},
    'n': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}, 'm': {'hand': 'RIGHT', 'color': RED_LIGHT, 'finger': 'Index'}
}

learned_letters = set(string.ascii_uppercase); grass_removed_letters = set()
current_quiz_letter = ""; eat_timer = 0; cry_timer = 0; jump_timer = 0; quiz_feedback_status = FEEDBACK_NEUTRAL 
feedback_timer = 0; is_finished = False; start_time = time.time()
abc_phonics_index = 0; transition_start_time = 0; quiz_awaiting_input = False 

BACKGROUND_IMAGES = {}
main_bg = load_img(os.path.join(BG_DIR, "bg.webp"), (SCREEN_WIDTH, SCREEN_HEIGHT))
title_bg = load_img(os.path.join(BG_DIR, "map.webp"), (SCREEN_WIDTH, SCREEN_HEIGHT))
BACKGROUND_IMAGES['main'] = main_bg if main_bg else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
BACKGROUND_IMAGES['title_screen'] = title_bg if title_bg else BACKGROUND_IMAGES['main']

img_carrot = load_img(os.path.join(RABBIT_DIR, "carrot.webp"), CARROT_ICON_SIZE) 
img_maru = load_img(os.path.join(OTHER_IMG_DIR, "ooo.webp"), FEEDBACK_IMG_SIZE)
img_batsu = load_img(os.path.join(OTHER_IMG_DIR, "xxx.webp"), FEEDBACK_IMG_SIZE)

img_rabbit_stand_menu = load_img(os.path.join(RABBIT_DIR, "stand.webp"), 600)
img_rabbit_hopping_menu = load_img(os.path.join(RABBIT_DIR, "hopping.webp"), 600)
img_rabbit_right_neck_menu = load_img(os.path.join(RABBIT_DIR, "right_neck.webp"), 600)
img_rabbit_left_neck_menu = load_img(os.path.join(RABBIT_DIR, "left_neck.webp"), 600)

RESULT_IMG_SIZE = 300
img_result_jump = load_img(os.path.join(RABBIT_DIR, "jump.webp"), RESULT_IMG_SIZE)
img_result_hopping = load_img(os.path.join(RABBIT_DIR, "hopping.webp"), RESULT_IMG_SIZE)
img_result_squat = load_img(os.path.join(RABBIT_DIR, "squat.webp"), RESULT_IMG_SIZE)
img_result_left_neck = load_img(os.path.join(RABBIT_DIR, "left_neck.webp"), RESULT_IMG_SIZE)
img_result_poor = load_img(os.path.join(RABBIT_DIR, "poor.webp"), RESULT_IMG_SIZE)
img_result_cry = load_img(os.path.join(RABBIT_DIR, "cry.webp"), RESULT_IMG_SIZE)

RABBIT_IMAGES = {} 
RABBIT_IMAGES[STATE_STAND] = load_img(os.path.join(RABBIT_DIR, "stand.webp"), RABBIT_ICON_SIZE)
RABBIT_IMAGES[STATE_MOVING_1] = load_img(os.path.join(RABBIT_DIR, "right1.webp"), RABBIT_ICON_SIZE)
RABBIT_IMAGES[STATE_MOVING_2] = load_img(os.path.join(RABBIT_DIR, "right2.webp"), RABBIT_ICON_SIZE)
RABBIT_IMAGES[STATE_EAT] = load_img(os.path.join(RABBIT_DIR, "eat.webp"), RABBIT_ICON_SIZE)
RABBIT_IMAGES[STATE_CRY] = load_img(os.path.join(RABBIT_DIR, "cry.webp"), RABBIT_ICON_SIZE)
RABBIT_IMAGES[STATE_JUMP] = load_img(os.path.join(RABBIT_DIR, "jump.webp"), RABBIT_ICON_SIZE) 
if RABBIT_IMAGES[STATE_MOVING_1]: RABBIT_IMAGES[STATE_MOVING_LEFT_1] = pygame.transform.flip(RABBIT_IMAGES[STATE_MOVING_1], True, False)
if RABBIT_IMAGES[STATE_MOVING_2]: RABBIT_IMAGES[STATE_MOVING_LEFT_2] = pygame.transform.flip(RABBIT_IMAGES[STATE_MOVING_2], True, False)

rabbit_pos_x, rabbit_pos_y = 0, 0
target_x, target_y = 0, 0; target_letter = "" 

# ====================================================================
# II. 描画・ユーティリティ関数
# ====================================================================

class AlphabetGrid:
    def __init__(self):
        self.surface = None
        self.last_mode = None
        self.last_removed = set()
        self.gw = SCREEN_WIDTH * 0.8
        self.gh = SCREEN_HEIGHT - (SCREEN_HEIGHT * 0.45) - 50

    def get_surface(self, mode, removed_set):
        if self.surface and self.last_mode == mode and self.last_removed == removed_set:
            return self.surface
        
        self.surface = pygame.Surface((self.gw, self.gh), pygame.SRCALPHA)
        self.last_mode = mode
        self.last_removed = removed_set.copy()
        
        images = PHONETIC_IMAGES_LONG if mode == MODE_RANDOM else PHONETIC_IMAGES_SHORT
        pygame.draw.rect(self.surface, BLACK, (0, 0, self.gw, self.gh), 2)
        
        cw, rh = self.gw / 9, self.gh / 3
        for i, (l, _, _) in enumerate(ALPHABET_DATA):
            if l not in learned_letters: continue
            r, c = i // 9, i % 9
            cx, cy = c * cw, r * rh
            pygame.draw.rect(self.surface, BLACK, (cx, cy, cw, rh), 1)
            txt = font_medium.render(l, True, BLACK)
            self.surface.blit(txt, txt.get_rect(center=(cx + cw/2, cy + rh*0.25)))
            img = images.get(l)
            if img: self.surface.blit(img, img.get_rect(center=(cx + cw/2, cy + rh*0.5)))
            if img_carrot and l not in removed_set:
                self.surface.blit(img_carrot, img_carrot.get_rect(center=(cx + cw/2, cy + rh*0.75)))
        return self.surface

grid_cache = AlphabetGrid()

class ScoreCache:
    def __init__(self):
        self.last_score = -1
        self.surface = None
        self.rect = None

    def get_score_render(self, score, right_pos, bottom_pos):
        if self.last_score == score and self.surface:
            return self.surface, self.rect
        self.last_score = score
        score_str = f"X {score}"
        txt_main = font_score.render(score_str, True, WHITE)
        txt_out = font_score.render(score_str, True, BLACK)
        w, h = txt_main.get_width() + 4, txt_main.get_height() + 4
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for dx, dy in [(0,0),(4,0),(0,4),(4,4)]:
            surf.blit(txt_out, (dx, dy))
        surf.blit(txt_main, (2, 2))
        self.surface = surf
        self.rect = surf.get_rect(right=right_pos, bottom=bottom_pos)
        return self.surface, self.rect

score_cache = ScoreCache()

def play_sound_sound_object(sound_obj, loops=0):
    if sound_obj:
        try: sound_obj.play(loops=loops)
        except: pass

def play_sound_file(word_name):
    base_name = word_name.lower()
    for ext in ['.ogg']:
        p = os.path.join(WORD_SOUND_DIR, base_name + ext)
        if os.path.exists(p):
            try:
                s = pygame.mixer.Sound(p)
                s.play()
                return
            except: pass

def get_grid_center_pos(letter):
    GY = SCREEN_HEIGHT * 0.45; GW, GH = SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - GY - 50
    try: i = next(idx for idx, d in enumerate(ALPHABET_DATA) if d[0] == letter)
    except: return None, None 
    r, c = i // 9, i % 9; cw, rh = GW / 9, GH / 3
    return SCREEN_WIDTH * 0.1 + c * cw + cw/2, GY + r * rh + rh * 0.75 - RABBIT_ICON_SIZE/4

def get_start_position():
    GY = SCREEN_HEIGHT * 0.45; GW, GH = SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - GY - 50
    r, c = 2, 9; cw, rh = GW / 9, GH / 3
    return SCREEN_WIDTH * 0.1 + c * cw + cw/2, GY + r * rh + rh * 0.75 - RABBIT_ICON_SIZE/4

def set_next_quiz_random(game_instance):
    global current_quiz_letter, quiz_feedback_status, quiz_awaiting_input
    quizzable = [l for l, _, _ in ALPHABET_DATA if l not in grass_removed_letters]
    if not quizzable:
        game_instance.state = STATE_TRANSITION; global transition_start_time; transition_start_time = pygame.time.get_ticks()
        play_sound_sound_object(CLEAR_SOUND) 
        return False 
    current_quiz_letter = random.choice(quizzable); quiz_feedback_status = FEEDBACK_NEUTRAL; quiz_awaiting_input = True 
    game_instance.problem_index += 1
    play_sound_sound_object(PHONIC_SOUNDS.get(f"LONG_{current_quiz_letter}")); return True

def set_next_quiz_abc_phonics(game_instance):
    global current_quiz_letter, quiz_feedback_status, quiz_awaiting_input
    if game_instance.problem_index >= len(game_instance.problems_to_play):
        game_instance.state = STATE_TRANSITION; global transition_start_time; transition_start_time = pygame.time.get_ticks()
        play_sound_sound_object(CLEAR_SOUND) 
        return False
    current_quiz_letter = game_instance.problems_to_play[game_instance.problem_index]
    quiz_feedback_status = FEEDBACK_NEUTRAL; quiz_awaiting_input = True 
    game_instance.problem_index += 1
    play_sound_sound_object(PHONIC_SOUNDS.get(current_quiz_letter)); return True

class FlowingProblem:
    def __init__(self, text): 
        self.text = text
        self.x = -100
        self.y = SCREEN_HEIGHT // 6
        self.speed = 1.0 
        self.is_active = True
    def move(self): 
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 100: self.is_active = False
    def draw_bird(self, screen, typed_txt, remaining_txt):
        is_first_image = (pygame.time.get_ticks() // 500) % 2 == 0
        img = img_bird1 if is_first_image else img_bird2
        if img:
            ts_surf = font_extra_large.render(typed_txt, True, WHITE)
            rs_surf = font_extra_large.render(remaining_txt, True, WHITE)
            tw = ts_surf.get_width() + rs_surf.get_width()
            bird_center_x = self.x + tw // 2
            bird_x = int(bird_center_x - BIRD_SIZE // 2)
            bird_y = int(self.y - BIRD_SIZE + 50) 
            screen.blit(img, (bird_x, bird_y))

def draw_keyboard(screen, next_char=None):
    for row_idx, row in enumerate(KEYBOARD_LAYOUT):
        for col_idx, char in enumerate(row):
            x = KEYBOARD_START_X + col_idx * KEY_W; y = KEYBOARD_START_Y + row_idx * KEY_H
            rect = pygame.Rect(x, y, KEY_W - 5, KEY_H - 5); key_info = KEY_MAP.get(char, None)
            color = YELLOW if next_char and char.upper() == next_char.upper() else (key_info['color'] if key_info else GRAY)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            txt = font_medium.render(char.upper(), True, BLACK); screen.blit(txt, txt.get_rect(center=rect.center))

def draw_hands(screen, next_char=None):
    next_key_info = KEY_MAP.get(next_char.lower() if next_char else '', {})
    f_num = {'Index': '2', 'Middle': '3', 'Ring': '4', 'Pinky': '5'}
    for hand, pos_dict in [('LEFT', LEFT_HAND_POSITIONS), ('RIGHT', RIGHT_HAND_POSITIONS)]:
        for f_name, pos in pos_dict.items():
            color = next_key_info.get('color') if next_key_info.get('hand') == hand and next_key_info.get('finger') == f_name else DARK_GRAY
            pygame.draw.circle(screen, color, pos, FINGER_SIZE)
            pygame.draw.circle(screen, WHITE, pos, FINGER_SIZE - 5) 
            txt = font_small.render(f_num.get(f_name, ''), True, BLACK); screen.blit(txt, txt.get_rect(center=pos))

def draw_button(screen, text, rect, color, border_color=BLACK, forced_press_color=False):
    mouse_pos = pygame.mouse.get_pos()
    is_pressed = pygame.mouse.get_pressed()[0]
    draw_color = color
    if forced_press_color or (rect.collidepoint(mouse_pos) and is_pressed):
        draw_color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))
    pygame.draw.rect(screen, draw_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=10) 
    f = font_medium if len(text) <= 4 else font_small
    if text == "もう一度聞く": f = font_replay_button
    elif text == "パス": f = font_pass_button
    t_color = WHITE if color != ORANGE else BLACK
    surf = f.render(text, True, t_color); screen.blit(surf, surf.get_rect(center=rect.center))

def draw_progress_button(screen, current, total):
    rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, 20, 160, 50)
    pygame.draw.rect(screen, GREEN, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    txt = font_small.render(f"{current} / {total}", True, WHITE)
    screen.blit(txt, txt.get_rect(center=rect.center))

def draw_result_screen(screen, results, game_instance): 
    screen.blit(BACKGROUND_IMAGES['main'], (0, 0)) 
    overlay = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 180)); screen.blit(overlay, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1))
    title_surf = font_extra_large.render("結果発表！", True, BLACK)
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50 + SCREEN_HEIGHT * 0.1)))
    data = [("正解キー数", f"{results['correct']} キー", BLUE), ("ミスキー数", f"{results['miss']} キー", RED), ("所要時間", f"{results['time']:.1f} 秒", BLACK), ("正確率", f"{results['accuracy']}%", BLACK)]
    y_offset = 150 + SCREEN_HEIGHT * 0.1
    for label, value, color in data:
        l_s = font_large.render(label, True, BLACK); v_s = font_large.render(value, True, color)
        screen.blit(l_s, l_s.get_rect(midright=(SCREEN_WIDTH // 2 - 20, y_offset)))
        screen.blit(v_s, v_s.get_rect(midleft=(SCREEN_WIDTH // 2 + 20, y_offset))); y_offset += 60
    acc = results['accuracy']; msg = ""; eval_img = None; res_sound = None 
    if acc == 100: msg = "Amazing!!!"; eval_img = img_result_jump; res_sound = RESULT_SOUNDS['amazing']
    elif 80 < acc < 100: msg = "Excellent!!"; eval_img = img_result_hopping; res_sound = RESULT_SOUNDS['excellent']
    elif 60 < acc <= 80: msg = "Very Good!"; eval_img = img_result_squat; res_sound = RESULT_SOUNDS['verygood']
    elif 30 < acc <= 60: msg = "good!"; eval_img = img_result_left_neck; res_sound = RESULT_SOUNDS['good']
    elif 0 < acc <= 30: msg = "Poor"; eval_img = img_result_poor; res_sound = RESULT_SOUNDS['poor']
    elif acc == 0: msg = "Oh! My God!"; eval_img = img_result_cry; res_sound = RESULT_SOUNDS['ohmygod']
    if res_sound and not game_instance.result_sound_played:
        play_sound_sound_object(res_sound); game_instance.result_sound_played = True
    if msg:
        msg_surf = font_large.render(msg, True, PURPLE)
        screen.blit(msg_surf, msg_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 50)))
    if eval_img: screen.blit(eval_img, eval_img.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)))
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + 130, 300, 70)
    draw_button(screen, "戻る", button_rect, GREEN); return button_rect

# ====================================================================
# III. ゲーム管理クラス
# ====================================================================

class Game:
    def __init__(self, mode=MODE_ABC): 
        self.reset()
        self.state = STATE_TITLE
        self.set_mode(mode)

    def reset(self):
        global grass_removed_letters, rabbit_state, quiz_awaiting_input, rabbit_pos_x, rabbit_pos_y, target_x, target_y, cry_timer, jump_timer
        self.typed_text = ""; self.current_problem = ""; self.total_correct_keys = 0; self.total_missed_keys = 0; self.pass_count = 0
        self.problem_index = 0; self.start_time_typing = 0; self.end_time_typing = 0; self.problems_to_play = []
        self.current_full_word = ""; self.word_clear_timer = 0; self.cleared_word_display = ""; self.word_image_cache = {} 
        self.current_word_image = None; self.current_word_image_rect = None; self.result_sound_played = False 
        self.abc_correct_timer = 0 
        grass_removed_letters = set(); start_time = time.time(); current_quiz_letter = "" 
        rabbit_state = STATE_STAND; rabbit_pos_x, rabbit_pos_y = get_start_position(); target_x, target_y = rabbit_pos_x, rabbit_pos_y
        quiz_awaiting_input = False; cry_timer = 0; jump_timer = 0
        self.phonics_correct_count = 0; self.phonics_miss_count = 0; self.phonics_duration = 0

    def set_mode(self, mode, count=None):
        self.current_mode = mode; self.problem_index = 0
        if mode in [MODE_WORD, MODE_WORD_TEST]:
            temp_list = list(WORD_LIST)
            random.shuffle(temp_list)
            if count is None or count == "全て": self.problems_to_play = temp_list
            else:
                try: num = int(count); self.problems_to_play = temp_list[:min(num, len(temp_list))]
                except: self.problems_to_play = temp_list
        elif mode == MODE_ABC_PHONICS: self.problems_to_play = random.sample(ALPHABET_LIST, len(ALPHABET_LIST))
        else: self.problems_to_play = ALPHABET_LIST

    def _load_next_problem(self):
        if self.current_mode not in [MODE_RANDOM, MODE_ABC_PHONICS]:
            if self.problem_index < len(self.problems_to_play):
                p = self.problems_to_play[self.problem_index]
                self.current_problem = p; self.current_full_word = p; self.typed_text = ""
                self.problem_index += 1; self.current_flowing_problem = FlowingProblem(p) 
                self.current_word_image = None; self.current_word_image_rect = None
                if self.current_mode == MODE_WORD_TEST:
                    img_path = os.path.join(WORDS_IMG_DIR, f"{p.lower()}.webp")
                    img = load_img(img_path, (750, 450)) 
                    if img:
                        self.current_word_image = img
                        self.current_word_image_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
                if self.current_mode == MODE_ABC: play_sound_sound_object(PHONIC_SOUNDS.get(p.upper()))
                if self.current_mode == MODE_LONG_VOWEL: play_sound_sound_object(PHONIC_SOUNDS.get(f"LONG_{p.upper()}"))
                if self.current_mode in [MODE_WORD, MODE_WORD_TEST]: play_sound_file(p.lower())
                if self.problem_index == 1: self.start_time_typing = pygame.time.get_ticks()
            else:
                self.end_time_typing = pygame.time.get_ticks()
                self.state = STATE_TRANSITION
                global transition_start_time
                transition_start_time = pygame.time.get_ticks() 
                play_sound_sound_object(CLEAR_SOUND) 

    def handle_key_input(self, char):
        global current_quiz_letter, quiz_feedback_status, feedback_timer, rabbit_state, target_x, target_y, target_letter, quiz_awaiting_input, jump_timer
        if self.state != STATE_GAME or rabbit_state == STATE_CRY or self.word_clear_timer > 0: return 
        p_letter = char.upper() 
        if self.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
            if not quiz_awaiting_input: return
            if current_quiz_letter and p_letter == current_quiz_letter:
                quiz_feedback_status = FEEDBACK_CORRECT; feedback_timer = FEEDBACK_DURATION_CORRECT; target_letter = p_letter 
                quiz_awaiting_input = False; self.phonics_correct_count += 1 
                nx, ny = get_grid_center_pos(p_letter)
                if nx is not None: target_x, target_y = nx, ny; rabbit_state = STATE_MOVING_1
            else:
                if quiz_feedback_status == FEEDBACK_NEUTRAL:
                    quiz_feedback_status = FEEDBACK_INCORRECT; feedback_timer = FEEDBACK_DURATION_MISS
                    self.phonics_miss_count += 1; play_sound_sound_object(LOW_BOING_SOUND)
        else:
            nc = self.get_next_char()
            if nc and char.lower() == nc.lower():
                play_sound_sound_object(HIT_SOUND); self.total_correct_keys += 1
                self.typed_text += self.current_problem[0]; self.current_problem = self.current_problem[1:]
                if not self.current_problem:
                    if self.current_mode in [MODE_WORD, MODE_WORD_TEST]:
                        play_sound_sound_object(CORRECT_WORD_SOUND)
                        self.cleared_word_display = self.current_full_word
                        self.word_clear_timer = 40; rabbit_state = STATE_JUMP; jump_timer = 40 
                    else: 
                        self.abc_correct_timer = 30
                        self.word_clear_timer = 30 
            else: play_sound_sound_object(MISS_SOUND); self.total_missed_keys += 1

    def skip_problem(self):
        global quiz_awaiting_input, grass_removed_letters, current_quiz_letter, rabbit_state, cry_timer
        if self.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS] and quiz_awaiting_input:
            play_sound_sound_object(SQUEAKY_TOY_SOUND); self.pass_count += 1; quiz_awaiting_input = False
            grass_removed_letters.add(current_quiz_letter); rabbit_state = STATE_CRY; cry_timer = CRY_DURATION

    def get_next_char(self):
        if self.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]: return current_quiz_letter
        return self.current_problem[0] if self.current_problem else None
    def get_typed_text(self): 
        return self.typed_text if self.current_mode in [MODE_WORD, MODE_WORD_TEST] else self.typed_text.lower()
    def get_remaining_text(self): 
        if self.current_mode == MODE_WORD: return self.current_problem
        if self.current_mode == MODE_WORD_TEST: return "?" * len(self.current_problem)
        return self.current_problem.lower()
    def calculate_results(self):
        if self.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
            t = max(1, self.phonics_duration); miss = self.phonics_miss_count + self.pass_count
            total = self.phonics_correct_count + miss
            acc = round((self.phonics_correct_count / total) * 100, 1) if total > 0 else 0
            return {"time": t, "accuracy": acc, "correct": self.phonics_correct_count, "miss": miss}
        else:
            t = max(1, ((self.end_time_typing or pygame.time.get_ticks()) - self.start_time_typing) / 1000)
            miss = self.total_missed_keys; total = self.total_correct_keys + miss
            acc = round((self.total_correct_keys / total) * 100, 1) if total > 0 else 0
            return {"time": t, "accuracy": acc, "correct": self.total_correct_keys, "miss": miss}

# ====================================================================
# IV. メインループ
# ====================================================================

async def main():
    global rabbit_state, rabbit_pos_x, rabbit_pos_y, target_x, target_y, target_letter, eat_timer, cry_timer, jump_timer, quiz_feedback_status, feedback_timer, current_quiz_letter, grass_removed_letters, start_time, transition_start_time, quiz_awaiting_input
    
    game = Game(); running = True; anim_frame = 0; result_btn_rect = None
    btn_w, btn_h = 240, 100; gap_x = 30; gap_y = 40
    start_x = (SCREEN_WIDTH - (btn_w * 3 + gap_x * 2)) // 2
    start_y = SCREEN_HEIGHT // 2 - 80
    mode_order_top = [MODE_ABC, MODE_LONG_VOWEL, MODE_WORD]
    mode_order_bottom = [MODE_ABC_PHONICS, MODE_RANDOM, MODE_WORD_TEST]
    mode_btns = {}
    btn_labels = {MODE_ABC: "短音", MODE_LONG_VOWEL: "長音", MODE_WORD: "単語", MODE_ABC_PHONICS: "短音テスト", MODE_RANDOM: "長音テスト", MODE_WORD_TEST: "単語テスト"}
    for i, m in enumerate(mode_order_top): mode_btns[m] = pygame.Rect(start_x + i*(btn_w+gap_x), start_y, btn_w, btn_h)
    for i, m in enumerate(mode_order_bottom): mode_btns[m] = pygame.Rect(start_x + i*(btn_w+gap_x), start_y + (btn_h+gap_y), btn_w, btn_h)
    
    title_click_timer = 0; selected_mode = None
    word_menu_options = ["全て", "10", "20", "30"]
    word_menu_labels = {"全て": "全て", "10": "１０こ", "20": "２０こ", "30": "３０こ"}
    wm_w, wm_h = 300, 80; wm_gap = 30; wm_start_y = (SCREEN_HEIGHT - (wm_h * 4 + wm_gap * 3)) // 2
    word_menu_btns = {opt: pygame.Rect(SCREEN_WIDTH // 2 - wm_w // 2, wm_start_y + i*(wm_h+wm_gap), wm_w, wm_h) for i, opt in enumerate(word_menu_options)}
    word_menu_click_timer = 0; selected_word_opt = None
    BACK_RECT = pygame.Rect(20, 20, 100, 50)
    REPLAY_DEFAULT_Y = SCREEN_HEIGHT * 0.45 - 60
    REPLAY_RECT = pygame.Rect(SCREEN_WIDTH // 2 - 120, REPLAY_DEFAULT_Y, 240, 50)
    GRID_RIGHT = SCREEN_WIDTH * 0.9; PASS_W = 120
    PASS_RECT = pygame.Rect(GRID_RIGHT - PASS_W, REPLAY_DEFAULT_Y, PASS_W, 50)
    BIG_RABBIT_SIZE = int(RABBIT_ICON_SIZE * 1.5)
    img_rabbit_stand_big = load_img(os.path.join(RABBIT_DIR, "stand.webp"), BIG_RABBIT_SIZE)
    img_rabbit_jump_big = load_img(os.path.join(RABBIT_DIR, "jump.webp"), BIG_RABBIT_SIZE)

    play_sound_sound_object(OPENING_SOUND)

    while running:
        anim_frame += 1; cur_ms = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            if e.type == pygame.KEYDOWN and game.state == STATE_GAME:
                if 'a' <= e.unicode <= 'z': game.handle_key_input(e.unicode)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if game.state == STATE_TITLE and title_click_timer == 0:
                    for m, r in mode_btns.items():
                        if r.collidepoint(e.pos):
                            play_sound_sound_object(CLICK_SOUND); OPENING_SOUND.stop()
                            selected_mode = m; title_click_timer = 20; break
                elif game.state == STATE_WORD_MENU and word_menu_click_timer == 0:
                    if BACK_RECT.collidepoint(e.pos): 
                        CHOICE_MUSIC.stop(); game.state = STATE_TITLE; play_sound_sound_object(OPENING_SOUND) 
                    for opt, r in word_menu_btns.items():
                        if r.collidepoint(e.pos):
                            play_sound_sound_object(DOORBELL_SOUND); selected_word_opt = opt; word_menu_click_timer = 20; break
                elif game.state == STATE_GAME:
                    if BACK_RECT.collidepoint(e.pos): 
                        game.reset(); game.state = STATE_TITLE; play_sound_sound_object(OPENING_SOUND) 
                    if REPLAY_RECT.collidepoint(e.pos):
                        if rabbit_state != STATE_CRY:
                            if game.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
                                play_sound_sound_object(PHONIC_SOUNDS.get(current_quiz_letter if game.current_mode == MODE_ABC_PHONICS else f"LONG_{current_quiz_letter}"))
                            elif game.current_mode in [MODE_WORD, MODE_WORD_TEST]:
                                if game.word_clear_timer <= 0: play_sound_file(game.current_full_word.lower())
                    if PASS_RECT.collidepoint(e.pos) and game.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
                        if rabbit_state not in (STATE_CRY, STATE_MOVING_1, STATE_MOVING_2, STATE_MOVING_LEFT_1, STATE_MOVING_LEFT_2, STATE_EAT):
                            game.skip_problem()
                elif game.state == STATE_RESULT and result_btn_rect and result_btn_rect.collidepoint(e.pos): 
                    game.state = STATE_TITLE; play_sound_sound_object(OPENING_SOUND) 

        if game.state == STATE_TITLE and title_click_timer > 0:
            title_click_timer -= 1
            if title_click_timer == 0:
                REPLAY_RECT.y = REPLAY_DEFAULT_Y
                m = selected_mode
                if m in [MODE_WORD, MODE_WORD_TEST]:
                    game.reset(); game.current_mode = m; game.state = STATE_WORD_MENU
                    play_sound_sound_object(CHOICE_MUSIC, loops=-1) 
                else:
                    game.reset(); game.set_mode(m); game.state = STATE_GAME; start_time = time.time()
                    if m == MODE_RANDOM: set_next_quiz_random(game)
                    elif m == MODE_ABC_PHONICS: set_next_quiz_abc_phonics(game)
                    else: game._load_next_problem()

        if game.state == STATE_WORD_MENU and word_menu_click_timer > 0:
            word_menu_click_timer -= 1
            if word_menu_click_timer == 0:
                CHOICE_MUSIC.stop(); game.set_mode(game.current_mode, selected_word_opt)
                game.state = STATE_GAME; start_time = time.time(); game._load_next_problem()

        if game.state == STATE_GAME:
            if game.word_clear_timer > 0:
                game.word_clear_timer -= 1
                if game.abc_correct_timer > 0:
                    game.abc_correct_timer -= 1
                if game.word_clear_timer <= 0: game._load_next_problem()
            if rabbit_state == STATE_JUMP:
                jump_timer -= 1
                if jump_timer <= 0: rabbit_state = STATE_STAND
            if game.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
                if not quiz_awaiting_input:
                    if rabbit_state == STATE_CRY:
                        cry_timer -= 1
                        if cry_timer <= 0:
                            rabbit_state = STATE_STAND
                            if game.current_mode == MODE_RANDOM: set_next_quiz_random(game)
                            else: set_next_quiz_abc_phonics(game)
                    dist = np.sqrt((target_x - rabbit_pos_x)**2 + (target_y - rabbit_pos_y)**2)
                    if rabbit_state in [STATE_MOVING_1, STATE_MOVING_2, STATE_MOVING_LEFT_1, STATE_MOVING_LEFT_2]:
                        if dist < EAT_THRESHOLD:
                            rabbit_pos_x, rabbit_pos_y = target_x, target_y
                            if target_letter and target_letter not in grass_removed_letters:
                                rabbit_state = STATE_EAT; eat_timer = EAT_DURATION; play_sound_sound_object(HIT_SOUND); grass_removed_letters.add(target_letter)
                            else: rabbit_state = STATE_STAND
                        else:
                            n1, n2 = (STATE_MOVING_1, STATE_MOVING_2) if target_x > rabbit_pos_x else (STATE_MOVING_LEFT_1, STATE_MOVING_LEFT_2)
                            rabbit_pos_x += (target_x - rabbit_pos_x) * MOVEMENT_SPEED; rabbit_pos_y += (target_y - rabbit_pos_y) * MOVEMENT_SPEED
                            if anim_frame % 10 == 0: rabbit_state = n2 if rabbit_state == n1 else n1
                    elif rabbit_state == STATE_EAT:
                        eat_timer -= 1
                        if eat_timer <= 0:
                            rabbit_state = STATE_STAND
                            if game.current_mode == MODE_RANDOM: set_next_quiz_random(game)
                            else: set_next_quiz_abc_phonics(game)
                if feedback_timer > 0: feedback_timer -= 1
                elif feedback_timer == 0 and quiz_feedback_status != FEEDBACK_NEUTRAL and rabbit_state != STATE_EAT:
                    quiz_feedback_status = FEEDBACK_NEUTRAL

        if game.state == STATE_TITLE:
            screen.blit(BACKGROUND_IMAGES['title_screen'], (0,0))
            title_text = "ABCD（あぶくど）タイピング"
            title_surf = font_menu_title.render(title_text, True, BLACK)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 30))
            text_outline = font_menu_title.render(title_text, True, WHITE)
            for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]: screen.blit(text_outline, title_rect.move(dx, dy))
            screen.blit(title_surf, title_rect)
            for m, r in mode_btns.items(): draw_button(screen, btn_labels[m], r, BLUE, forced_press_color=(selected_mode == m and title_click_timer > 0))
        elif game.state == STATE_WORD_MENU:
            screen.blit(BACKGROUND_IMAGES['main'], (0,0)); draw_button(screen, "戻る", BACK_RECT, DARK_GRAY)
            for opt, r in word_menu_btns.items(): draw_button(screen, word_menu_labels[opt], r, ORANGE, forced_press_color=(selected_word_opt == opt and word_menu_click_timer > 0))
            rabbit_rect = img_rabbit_stand_menu.get_rect(bottomleft=(20, SCREEN_HEIGHT - 20))
            if word_menu_click_timer > 0:
                t = 20 - word_menu_click_timer
                rabbit_rect.y -= int(250 * (4 * t * (20 - t) / (20 * 20)))
                menu_rabbit_img = img_rabbit_hopping_menu
            else:
                neck_cycle = (pygame.time.get_ticks() // 300) % 4
                menu_rabbit_img = img_rabbit_right_neck_menu if neck_cycle==1 else (img_rabbit_left_neck_menu if neck_cycle==3 else img_rabbit_stand_menu)
            if menu_rabbit_img: screen.blit(menu_rabbit_img, rabbit_rect)
        elif game.state == STATE_GAME:
            screen.blit(BACKGROUND_IMAGES['main'], (0,0))
            
            is_correct_acting = (game.word_clear_timer > 0) or \
                                (quiz_feedback_status == FEEDBACK_CORRECT and (feedback_timer > 0 or eat_timer > 0)) or \
                                (getattr(game, 'abc_correct_timer', 0) > 0)
            
            current_bird_sing_img = img_bird_sing2 if is_correct_acting else img_bird_sing1
            
            if current_bird_sing_img:
                bird_sing_pos = (-100, SCREEN_HEIGHT - 410) if game.current_mode in [MODE_ABC, MODE_LONG_VOWEL, MODE_WORD] else ((-30, SCREEN_HEIGHT - 410) if game.current_mode == MODE_WORD_TEST else (10, 50))
                screen.blit(current_bird_sing_img, bird_sing_pos)
            
            draw_progress_button(screen, game.problem_index, len(game.problems_to_play))
            draw_button(screen, "戻る", BACK_RECT, DARK_GRAY)
            if game.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS, MODE_WORD, MODE_WORD_TEST]: draw_button(screen, "もう一度聞く", REPLAY_RECT, ORANGE)
            if game.current_mode in [MODE_RANDOM, MODE_ABC_PHONICS]:
                draw_button(screen, "パス", PASS_RECT, RED)
                score_surf, score_pos = score_cache.get_score_render(game.phonics_correct_count, PASS_RECT.right - 10, PASS_RECT.top - 20)
                score_carrot_rect = img_carrot.get_rect(right=score_pos.left - 10, bottom=score_pos.bottom + 5)
                screen.blit(img_carrot, score_carrot_rect)
                screen.blit(score_surf, score_pos)
                grid_surf = grid_cache.get_surface(game.current_mode, grass_removed_letters)
                screen.blit(grid_surf, (SCREEN_WIDTH*0.1, SCREEN_HEIGHT * 0.45))
                if quiz_feedback_status != FEEDBACK_NEUTRAL:
                    fb = img_maru if quiz_feedback_status == FEEDBACK_CORRECT else img_batsu
                    if fb: screen.blit(fb, fb.get_rect(center=(600, 200)))
                curr_img = RABBIT_IMAGES.get(rabbit_state)
                if curr_img: screen.blit(curr_img, curr_img.get_rect(center=(int(rabbit_pos_x), int(rabbit_pos_y))))
            elif game.current_mode in [MODE_WORD, MODE_WORD_TEST]:
                if game.word_clear_timer > 0 and game.current_mode == MODE_WORD:
                    ts = font_extra_large.render(game.cleared_word_display, True, WHITE)
                    tw, th = ts.get_width(), ts.get_height()
                    pygame.draw.rect(screen, DARK_GREEN, (SCREEN_WIDTH//2 - tw//2 - 30, SCREEN_HEIGHT//6 - 10, tw + 60, th + 20))
                    pygame.draw.rect(screen, BROWN, (SCREEN_WIDTH//2 - tw//2 - 30, SCREEN_HEIGHT//6 - 10, tw + 60, th + 20), 5)
                    screen.blit(ts, (SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//6))
                else:
                    prob = game.current_flowing_problem
                    if prob:
                        prob.move(); t_txt, r_txt = game.get_typed_text(), game.get_remaining_text(); prob.draw_bird(screen, t_txt, r_txt)
                        ts_surf = font_extra_large.render(t_txt, True, WHITE); rs_surf = font_extra_large.render(r_txt, True, WHITE)
                        tw, th = ts_surf.get_width() + rs_surf.get_width(), ts_surf.get_height()
                        pygame.draw.rect(screen, DARK_GREEN, (prob.x - 30, prob.y - 10, tw + 60, th + 20))
                        pygame.draw.rect(screen, BROWN, (prob.x - 30, prob.y - 10, tw + 60, th + 20), 5)
                        screen.blit(ts_surf, (prob.x, prob.y)); screen.blit(rs_surf, (prob.x + ts_surf.get_width(), prob.y))
                        if not prob.is_active and game.current_problem != '' and game.word_clear_timer <= 0: 
                            game.total_missed_keys += len(game.current_problem); game._load_next_problem()
                rabbit_rect_game = img_rabbit_stand_big.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                if rabbit_state == STATE_JUMP:
                    t_game = 40 - jump_timer
                    rabbit_rect_game.y -= int(350 * (4 * t_game * (40 - t_game) / (40 * 40)))
                    current_rabbit_img = img_rabbit_jump_big
                else: current_rabbit_img = img_rabbit_stand_big
                if current_rabbit_img: screen.blit(current_rabbit_img, rabbit_rect_game)
                if game.current_mode == MODE_WORD_TEST:
                    if game.current_word_image:
                        screen.blit(game.current_word_image, game.current_word_image_rect)
                        REPLAY_RECT.y = game.current_word_image_rect.top - 50
                    else: REPLAY_RECT.y = 60
                else: draw_keyboard(screen, game.get_next_char()); draw_hands(screen, game.get_next_char())
            else:
                prob = game.current_flowing_problem
                if prob:
                    prob.move(); t_txt, r_txt = game.get_typed_text(), game.get_remaining_text(); prob.draw_bird(screen, t_txt, r_txt)
                    nx = game.get_next_char()
                    p_img = (PHONETIC_IMAGES_LONG if game.current_mode==MODE_LONG_VOWEL else PHONETIC_IMAGES_SHORT).get(nx)
                    if p_img: screen.blit(p_img, (550, 180))
                    ts_surf = font_extra_large.render(t_txt, True, WHITE); rs_surf = font_extra_large.render(r_txt, True, WHITE)
                    tw, th = ts_surf.get_width() + rs_surf.get_width(), ts_surf.get_height()
                    pygame.draw.rect(screen, DARK_GREEN, (prob.x - 30, prob.y - 10, tw + 60, th + 20))
                    pygame.draw.rect(screen, BROWN, (prob.x - 30, prob.y - 10, tw + 60, th + 20), 5)
                    screen.blit(ts_surf, (prob.x, prob.y)); screen.blit(rs_surf, (prob.x + ts_surf.get_width(), prob.y))
                    if not prob.is_active and game.current_problem != '' and game.word_clear_timer <= 0: 
                        game.total_missed_keys += len(game.current_problem); game._load_next_problem()
                draw_keyboard(screen, game.get_next_char()); draw_hands(screen, game.get_next_char())
        elif game.state == STATE_TRANSITION:
            screen.blit(BACKGROUND_IMAGES['title_screen'], (0,0))
            if cur_ms - transition_start_time >= TRANSITION_DURATION: 
                game.phonics_duration = (pygame.time.get_ticks() - start_time*1000)/1000 
                game.state = STATE_RESULT
            msg = font_extra_large.render("モードクリア！", True, WHITE); screen.blit(msg, msg.get_rect(center=(600, 400)))
        elif game.state == STATE_RESULT:
            result_btn_rect = draw_result_screen(screen, game.calculate_results(), game)
        
        pygame.display.flip()
        await asyncio.sleep(0) 
        clock.tick(60)

if __name__ == '__main__':
    asyncio.run(main())