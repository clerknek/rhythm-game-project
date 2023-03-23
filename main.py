import pygame, cv2, time, os, random, librosa, sys, math
import mediapipe as mp

# version 정보
__version__ = '2.0.4'

# pygame moduel을 import하고 초기화한다.
pygame.init()

# 창 정보와 관련된 변수를 정의한다.
w = 1000
h = w * (9 / 16)

# 코드 최적화를 위해 나누기 변수를 정의한다.
a1 = h / 12
a2 = w / 45
a3 = 4 / 10
a4 = 8 / 10
a5 = h / 900
a6 = w * (1 / 2)
a7 = w / 32
a8 = h / 30
a9 = h / 35
a10 = h / 50
a11 = h / 24
a12 = h / 100
a13 = w / 20
a14 = w / 30
a15 = h / 2
a16 = int(w / 14)
a17 = int(h / 20)
a18 = int(h / 10)

# lane 좌표를 설정한다.
width1 = w*(1/2) - w*a3
width2 = w*(1/2) - w*(2/10)
width3 = w*(1/2)
width4 = w*(1/2) + w*(2/10)
width5 = w*(1/2) + w*a3

# 색깔과 관련된 변수를 정의한다.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

# screen instance를 생성한다.
screen = pygame.display.set_mode((w, h))

# 게임 내에서 시간을 측정하기 위해 instance를 생성한다.
clock = pygame.time.Clock()

# hand detection을 위해 cam을 딴다.
# cam = cv2.VideoCapture(1) # mac User.
cam = cv2.VideoCapture(0) # Window User.

# hand detection instance를 생성한다.
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence = 0.3)

# frame을 설정한다.
maxframe = 60
fps = 0

# path ==========================================================================================
# current 경로를 설정한다.
Cpath = os.path.dirname(__file__)
# font 경로를 설정한다.
Fpath = os.path.join(Cpath, 'font')
# music 경로를 설정한다.
Mpath = os.path.join(Cpath, 'music')
# image 경로를 설정한다.
Ipath = os.path.join(Cpath, 'image')
# ===============================================================================================

# font ==========================================================================================
# 시작할 때 게임 화면에 띄울 문자열을 생성한다.
font_file = os.path.join(Fpath, 'retro_game_font.ttf')
ingame_font_rate = pygame.font.Font(font_file, int(a14))
rate = 'START'
# 가져온 font로 렌더링한다.
rate_text = ingame_font_rate.render(str(rate), False, WHITE)
# ===============================================================================================

# image =========================================================================================
# outro에서 띄울 image path를 설정한다.
quit_path = os.path.join(Ipath, 'quit.png')
restart_path = os.path.join(Ipath, 'restart.png')
# ===============================================================================================

# note가 떨어지는 속도를 설정한다.
speed = 1

# lane이 4개이므로 note와 관련되 정보를 담을 list 4개를 생성한다.
# [ty, tst]가 하나의 element로 들어간다.
t1, t2, t3, t4 = [], [], [], []

# spark 효과를 담을 list를 정의한다.
sparks = []

# 키 누름을 감지하는 list를 정의한다.
lanes = [0, 0, 0, 0]
laneset = [0, 0, 0, 0]

# effect를 주기 위한 변수를 정의한다.
combo = 0
combo_effect = 0
combo_effect2 = 0
miss_anim = 0
last_combo = 0

# outro ========================================================================================
# outro에서 점수 계산을 위한 변수를 정의한다.
excellent_cnt = 0     # 10 점
perfect_cnt = 0       # 5 점
bad_cnt = 0           # 3 점
miss_cnt = 0          # 0 점
# ===============================================================================================

# life ==========================================================================================
# 게임을 종료시키기 위한 변수와 life image를 load한다.
l = int(w / 25)
life_cnt = 5
life_img_path = os.path.join(Ipath, 'heart.png')
life_img = pygame.image.load(life_img_path)
life_img = pygame.transform.scale(life_img, (l, l))
# ===============================================================================================

# song ==========================================================================================
# 노래 file을 불러온다.
song_file = os.path.join(Mpath, 'short_canon.wav')

# beat를 생성한다.
audio, _ = librosa.load(song_file)
sampling_rate = 44100
tempo, beats = librosa.beat.beat_track(y = audio, sr = sampling_rate)

# beat가 찍혀야 하는 시간을 담고 있는 list를 생성한다.
beat_times = librosa.frames_to_time(beats)
beat_times = list(beat_times)
beat_times = beat_times[5:]

# pygame에 노래 file을 불러온다.
pygame.mixer.music.load(song_file)
# ===============================================================================================

# function ======================================================================================
# Spark VFX class를 선언한다.
class Spark():
    def __init__(self, loc, angle, speed, color, scale = 1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def point_towards(self, angle, rate):
        rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sing = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]


    # 중력과 마찰 기능을 추가한다.
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])
        # 더 현실적이 되고 싶다면, 여기서 속도를 조절해야 한다.

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]

        # 각도와 관련된 많은 옵션들을 가지고 놀 수 있습니다.
        self.point_towards(math.pi / 2, 0.02)
        self.velocity_adjust(0.975, 0.2, 8, dt)
        # self.angle += 0.1

        self.speed -= 0.1

        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, offset=[0, 0]):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.speed * self.scale, self.loc[1] + math.sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)

# note를 생성하는 함수를 정의한다.
def generate_notes():
    '''
    각 lane에 생성되는 note를 생성하는 함수이다. note의 정보를 [ty, tst]로 입력한다.
        - ty는 note의 위치이고 tst는 note가 생성되어야 하는 시간이다.
    [parameter]
        None
    [return]
        None
    '''
    global beat_times, t1, t2, t3, t4

    idx = 0
    while True:
        # idx가 beat_times의 끝에 도달하면 종료한다.
        if idx == len(beat_times):
                break
        
        # note를 생성할 lane을 random하게 추출한다.
        lane = random.randint(1, 4)

        if lane == 1:
            ty = 0
            tst = beat_times[idx]
            t1.append([ty, tst])
            idx += 1
            continue
        elif lane == 2:
            ty = 0
            tst = beat_times[idx]
            t2.append([ty, tst])
            idx += 1
            continue
        elif lane == 3:
            ty = 0
            tst = beat_times[idx]
            t3.append([ty, tst])
            idx += 1
            continue
        elif lane == 4:
            ty = 0
            tst = beat_times[idx]
            t4.append([ty, tst])
            idx += 1
            continue
    
# note가 한 번에 여러 개 떨어지도록 하는 함수를 정의한다.
def simultaneous_notes():
    '''
    note가 한 번에 여러 개 떨어지도록 만드는 함수이다. 한 번에 떨어지는 note 개수의 기본값은 2이다.
    [parameter]
        None
    [return]
        None
    '''
    global beat_times, t1, t2, t3, t4

    # 전체 beat의 수를 정의한다.
    total_beat = len(beat_times)

    # 1부터 total_beat // 2까지의 정수 중 하나를 random하게 추출해 sample 수로 설정한다.
    sample = random.randint(total_beat // 4, total_beat // 2)

    sample_beat_times = random.sample(beat_times, sample)

    idx = 0
    while True:
        if idx == len(sample_beat_times):
            break

        lane = random.randint(1, 4)

        if lane == 1:
            ty = 0
            tst = sample_beat_times[idx]
            t1.append([ty, tst])
            idx += 1
            continue
        elif lane == 2:
            ty = 0
            tst = sample_beat_times[idx]
            t2.append([ty, tst])
            idx += 1
            continue
        elif lane == 3:
            ty = 0
            tst = sample_beat_times[idx]
            t3.append([ty, tst])
            idx += 1
            continue
        elif lane == 4:
            ty = 0
            tst = sample_beat_times[idx]
            t4.append([ty, tst])
            idx += 1
            continue
    t1 = list(set([tuple(item) for item in t1]))
    t1 = list(list(item) for item in t1)

    t2 = list(set([tuple(item) for item in t2]))
    t2 = list(list(item) for item in t2)

    t3 = list(set([tuple(item) for item in t3]))
    t3 = list(list(item) for item in t3)

    t4 = list(set([tuple(item) for item in t4]))
    t4 = list(list(item) for item in t4)

    t1.sort()
    t2.sort()
    t3.sort()
    t4.sort()

# 점수를 판정하는 함수를 만든다.
rate_data = [0, 0, 0, 0]
def rating(n):
    '''
    각 lane에 combo와 'BAD', 'PERFECT', 'EXCELLENT' 문자를 띄우는 함수이다.
    [parameter]
        n: int - lane 번호를 설정한다.
    [return]
        None
    '''
    global gst, Time, combo, miss_anim, last_combo, combo_effect, combo_effect2, combo_time, rate, bad_cnt, perfect_cnt, excellent_cnt
    
    # rate_data의 n번째 note들의 정보를 가져와 판단한다.
    if abs(a1*9 - rate_data[n-1] < 950*speed*(h/900)) and abs(a1*9 - rate_data[n-1] >= 200*speed*(h/900)):
        last_combo = combo
        miss_anim = 1
        combo = 0
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        bad_cnt += 1
        rate = 'BAD'
    elif abs(a1*9 - rate_data[n-1]) < 200*speed*(h/900) and abs(a1*9 - rate_data[n-1]) >= 100*speed*(h/900):
        combo += 1
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        perfect_cnt += 1
        rate = 'PERFECT'
    elif abs(a1*9 - rate_data[n-1]) < 100*speed*(h/900) and abs(a1*9 - rate_data[n-1]) >= 0*speed*(h/900):
        combo += 1
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        excellent_cnt += 1
        rate = 'EXCELLENT'
# ===============================================================================================

# 각 lane에 note를 생성한다.
generate_notes()
simultaneous_notes()

# game function =================================================================================
# game을 실행하는 메인 함수를 정의한다. ===========================================================
def game():
    global gst, Time, combo, miss_anim, last_combo, combo_effect, combo_effect2, combo_time, rate, speed, t1, t2, t3, t4, miss_cnt, life_cnt
    
    # 시간 측정을 위해 게임이 플레이 되는 시간을 구하고 combo_time을 다시 계산한다.
    gst = time.time()
    Time = time.time() - gst
    combo_time = Time + 1
    
    # 노래 file을 재생한다.
    pygame.mixer.music.play()
    
    main = True
    while main:
        # 이벤트 감지 코드를 작성한다.
        for event in pygame.event.get():
            # 창을 나가는 동작을 감지한다.
            if event.type == pygame.QUIT:
                # 창을 지운다.
                main = False

        # 웹캠 이미지를 읽어온다.
        _, img = cam.read()
        # 좌우 반전 
        image = cv2.flip(img, 1)
        results = hands.process(image)

        if len(t1) > 0:
            rate_data[0] = t1[0][0]
        if len(t2) > 0:
            rate_data[1] = t2[0][0]
        if len(t3) > 0:
            rate_data[2] = t3[0][0]
        if len(t4) > 0:
            rate_data[3] = t4[0][0]

        # 게임이 시작되고 나서부터의 시간을 측정한다.
        Time = time.time() - gst

        # combo 글씨 생성
        ingame_font_combo = pygame.font.Font(font_file, int((a2) * combo_effect2))
        combo_text = ingame_font_combo.render(str(combo), False, WHITE)

        # 점수 글씨 생성
        rate_text = ingame_font_rate.render(str(rate), False, WHITE)
        rate_text = pygame.transform.scale(rate_text, (int(w / 110 * len(rate) * combo_effect2), int((w * (1 / 60) * combo_effect * combo_effect2))))

        # miss 글씨 생성
        ingame_font_miss = pygame.font.Font(font_file, int((a2 * miss_anim)))
        miss_text = ingame_font_miss.render(str(last_combo), False, (255, 0, 0))

        fps = clock.get_fps()
        if fps == 0:
            fps = maxframe   

    # gear ========================================================================================
        # 화면을 그린다. 단색으로 채운다.
        screen.fill(BLACK)

        # effect가 생기는 정도를 결정한다. effect가 생기고 사라지는 속도를 조절하고 싶으면 1을 바꾼다.
        # 숫자를 크게 하면 effect가 천천히 생기고 천천히 사라진다.
        lanes[0] += (laneset[0] - lanes[0]) / (1 * (maxframe / fps))
        lanes[1] += (laneset[1] - lanes[1]) / (1 * (maxframe / fps))
        lanes[2] += (laneset[2] - lanes[2]) / (1 * (maxframe / fps))
        lanes[3] += (laneset[3] - lanes[3]) / (1 * (maxframe / fps))

    # effect =======================================================================================
        # effect의 움직임을 결정한다.
        if Time > combo_time:
            combo_effect += (0 - combo_effect) / (1 * (maxframe / fps))
        if Time < combo_time:
            combo_effect += (1 - combo_effect) / (1 * (maxframe / fps))

        combo_effect2 += (2 - combo_effect2) / (1 * (maxframe / fps))

        miss_anim += (4 - miss_anim) / (14 * (maxframe / fps))

    # effect ===================================================================================
        # gear background
        pygame.draw.rect(screen, BLACK, (w*(1/2) - w*a3, -int(w/100), w*a4, h + int(w * (1 / 50))))

        # lane를 눌렀을 때 lane에 생기는 effect를 만든다.
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200-((200*(1/7))*i), 200-((200*(1/7))*i), 200-((200*(1/7))*i)), (w*(1/2) - w*a3 + w/32 - a7 * lanes[0], a1*9 - a8 * lanes[0] * i, w*(2/10) * lanes[0], a9 * (1 / i)))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200-((200*(1/7))*i), 200-((200*(1/7))*i), 200-((200*(1/7))*i)), (w*(1/2) - w*(2/10) + w/32 - a7 * lanes[1], a1*9 - a8 * lanes[1] * i, w*(2/10) * lanes[1], a9 * (1 / i)))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200-((200*(1/7))*i), 200-((200*(1/7))*i), 200-((200*(1/7))*i)), (w*(1/2)            + w/32 - a7 * lanes[2], a1*9 - a8 * lanes[2] * i, w*(2/10) * lanes[2], a9 * (1 / i)))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200-((200*(1/7))*i), 200-((200*(1/7))*i), 200-((200*(1/7))*i)), (w*(1/2) + w*(2/10) + w/32 - a7 * lanes[3], a1*9 - a8 * lanes[3] * i, w*(2/10) * lanes[3], a9 * (1 / i)))

        # gear line
        pygame.draw.rect(screen, WHITE, (w*(1/2) - w*a3, -int(w * (1/100)), w*a4, h + int(w * (1/50))), int(w * (1/200)))

    # note =========================================================================================
        # note를 만든다.
        for tile_data in t1:
            # 렉이 걸려도 노트는 일정한 속도로 내려오도록 하는 코드를 작성한다.
            # 판정선 위치 기준             현재 시간 - 노트 소환 시간
            #                             시간이 경과할수록 이 부분의 차가 커져 노트가 내려간다.
            tile_data[0] = a1 * 9 + (Time - tile_data[1]) * speed * 350 * (a5)
            pygame.draw.rect(screen, WHITE, (w*(1/2) - w*a3, tile_data[0] - a12, w*(2/10), a10))
            # 놓친 노트는 없앤다.

            if tile_data[0] > h - (h / 9):
                # 미스 판정을 만든다. 놓치면 해당 노트를 삭제한다.
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                miss_cnt += 1
                life_cnt -= 1
                rate = 'MISS'
                t1.remove(tile_data)

        for tile_data in t2:
            tile_data[0] = a1 * 9 + (Time - tile_data[1]) * 350 * speed * (a5)
            pygame.draw.rect(screen, WHITE, (w*(1/2) - w*(2/10), tile_data[0] - a12, w*(2/10), a10))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                miss_cnt += 1
                life_cnt -= 1
                rate = 'MISS'
                t2.remove(tile_data)

        for tile_data in t3:
            tile_data[0] = a1 * 9 + (Time - tile_data[1]) * 350 * speed * (a5)
            pygame.draw.rect(screen, WHITE, (w*(1/2), tile_data[0] - a12, w*(2/10), a10))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                miss_cnt += 1
                life_cnt -= 1
                rate = 'MISS'
                t3.remove(tile_data)

        for tile_data in t4:
            tile_data[0] = a1 * 9 + (Time - tile_data[1]) * 350 * speed * (a5)
            pygame.draw.rect(screen, WHITE, (w*(1/2) + w*(2/10), tile_data[0] - a12, w*(2/10), a10))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                miss_cnt += 1
                life_cnt -= 1
                rate = 'MISS'
                t4.remove(tile_data)

    # blinder =============================================================================================
        # 판정선을 그린다.
        pygame.draw.rect(screen, BLACK, (w*(1/2) - w*a3, a1 * 9, w*a4, h * (1/2)))
        pygame.draw.rect(screen, WHITE, (w*(1/2) - w*a3, a1 * 9, w*a4, h * (1/2)), int(a12))

    # background ==========================================================================================
        # 배경 화면에 생성될 버튼을 만든다.
        pygame.draw.circle(screen, (255 - 100 * lanes[0], 255 - 100 * lanes[0], 255 - 100 * lanes[0]), (w*(1/2) - w*(3/10), (a11) * 21 + a10 * lanes[0]), (a13), int(a12))
        pygame.draw.circle(screen, (255 - 100 * lanes[0], 255 - 100 * lanes[0], 255 - 100 * lanes[0]), (w*(1/2) - w*(3/10), (a11) * 21 + a10 * lanes[0]), (a14))

        pygame.draw.circle(screen, (255 - 100 * lanes[1], 255 - 100 * lanes[1], 255 - 100 * lanes[1]), (w*(1/2) - w*(1/10), (a11) * 21 + a10 * lanes[1]), (a13), int(a12))
        pygame.draw.circle(screen, (255 - 100 * lanes[1], 255 - 100 * lanes[1], 255 - 100 * lanes[1]), (w*(1/2) - w*(1/10), (a11) * 21 + a10 * lanes[1]), (a14))

        pygame.draw.circle(screen, (255 - 100 * lanes[2], 255 - 100 * lanes[2], 255 - 100 * lanes[2]), (w*(1/2) + w*(1/10), (a11) * 21 + a10 * lanes[2]), (a13), int(a12))
        pygame.draw.circle(screen, (255 - 100 * lanes[2], 255 - 100 * lanes[2], 255 - 100 * lanes[2]), (w*(1/2) + w*(1/10), (a11) * 21 + a10 * lanes[2]), (a14))

        pygame.draw.circle(screen, (255 - 100 * lanes[3], 255 - 100 * lanes[3], 255 - 100 * lanes[3]), (w*(1/2) + w*(3/10), (a11) * 21 + a10 * lanes[3]), (a13), int(a12))
        pygame.draw.circle(screen, (255 - 100 * lanes[3], 255 - 100 * lanes[3], 255 - 100 * lanes[3]), (w*(1/2) + w*(3/10), (a11) * 21 + a10 * lanes[3]), (a14))

        # 글씨를 화면에 띄운다.
        miss_text.set_alpha(255 - (255 / 4) * miss_anim)
        screen.blit(combo_text, (w*(1/2) - combo_text.get_width() * (1/2), a1 * 4 - combo_text.get_height() * (1/2)))
        screen.blit(rate_text, (w*(1/2) - rate_text.get_width() * (1/2), a1 * 8 - rate_text.get_height() * (1/2)))
        screen.blit(miss_text, (w*(1/2) - miss_text.get_width() * (1/2), a1 * 8 - miss_text.get_height() * (1/2)))

        # 남은 life의 개수를 이용해 life 문구를 띄운다.
        if life_cnt == 5:
            for i in range(life_cnt):
                screen.blit(life_img, (w - a16, a17 + a18*i))
        elif life_cnt == 4:
            for i in range(life_cnt):
                screen.blit(life_img, (w - a16, a17 + a18*i))
        elif life_cnt == 3:
            for i in range(life_cnt):
                screen.blit(life_img, (w - a16, a17 + a18*i))
        elif life_cnt == 2:
            for i in range(life_cnt):
                screen.blit(life_img, (w - a16, a17 + a18*i))
        elif life_cnt == 1:
            for i in range(life_cnt):
                screen.blit(life_img, (w - a16, a17 + a18*i))
        # 남은 life가 0이 되면 게임 오버 창으로 넘어간다. 노래를 종료하고 각 lane의 note를 초기화한다.
        else:
            main = False
            pygame.mixer.music.stop()
            t1, t2, t3, t4 = [], [], [], []
            game_over()

    # hand dtection =======================================================================================
        # hand detection과 hand tracking을 구현한다.
        grab_TF = [2, 2] # left, right
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                palm_x, palm_y = hand_landmarks.landmark[9].x*w, hand_landmarks.landmark[9].y*h
                _, finger_y = hand_landmarks.landmark[12].x*w, hand_landmarks.landmark[12].y*h

                if grab_TF[0] == 2:
                    if finger_y > palm_y:
                        grab_TF[0] = True
                        if width1 <= palm_x and palm_x <= width2:
                            laneset[0] = 1
                        if width2 <= palm_x and palm_x <= width3:
                            laneset[1] = 1
                        if width3 <= palm_x and palm_x <= width4:
                            laneset[2] = 1
                        if width4 <= palm_x and palm_x <= width5:
                            laneset[3] = 1
                    else:
                        grab_TF[0] = False
                elif grab_TF[1] == 2:
                    if finger_y > palm_y:
                        grab_TF[1] = True
                        if width1 <= palm_x and palm_x <= width2:
                            laneset[0] = 1
                        if width2 <= palm_x and palm_x <= width3:
                            laneset[1] = 1
                        if width3 <= palm_x and palm_x <= width4:
                            laneset[2] = 1
                        if width4 <= palm_x and palm_x <= width5:
                            laneset[3] = 1
                    else:
                        grab_TF[1] = False

                pygame.draw.circle(screen, GREEN, (int(palm_x), int(palm_y)), 15)
                if grab_TF[0] == True or grab_TF[1] == True:
                    # lane 1
                    if laneset[0] == 1:
                        if len(t1) > 0:
                            if t1[0][0] > a15:
                                rating(1)
                                del t1[0]

                    # lane 2
                    if laneset[1] == 1:
                        if len(t2) > 0:
                            if t2[0][0] > a15:
                                rating(2)
                                del t2[0]

                    # lane 3
                    if laneset[2] == 1:
                        if len(t3) > 0:
                            if t3[0][0] > a15:
                                rating(3)
                                del t3[0]

                    # lane 4
                    if laneset[3] == 1:
                        if len(t4) > 0:
                            if t4[0][0] > a15:
                                rating(4)
                                del t4[0]
                else:
                    laneset[0], laneset[1], laneset[2], laneset[3] = 0, 0, 0, 0
        else:
            laneset[0], laneset[1], laneset[2], laneset[3] = 0, 0, 0, 0
    
    # outro ===================================================================================
        if not pygame.mixer.music.get_busy():
            main = False
            end_game()

    # update ===================================================================================
        # 화면을 업데이트한다. 이 코드가 없으면 화면이 보이지 않는다.
        pygame.display.flip()

        # frame 제한 코드
        clock.tick(maxframe)
    cam.release()
# ========================================================================================

# 게임의 intro를 만드는 함수를 정의한다. ===================================================
def start_game():

    # intro 화면에 띄울 문구를 작성한다.
    intro_font_name = pygame.font.Font(font_file, 80)
    intro_font_start = pygame.font.Font(font_file, 50)
    intro_font_info = pygame.font.Font(font_file, 30)

    game_name_txt_render_1 = intro_font_name.render('ZAM ZAM', True, WHITE)
    game_name_txt_render_2 = intro_font_name.render('CIRCULATION', True, WHITE)
    start_box_txt_render = intro_font_start.render('START GAME', True, WHITE)
    info_txt_render = intro_font_info.render("CLICK THE BUTTON TO START", True, WHITE)
    start_box = pygame.Rect(w // 2 - 195, h // 2 + 50, 393, 70)
    
    # intro 실행.
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro = False
                pygame.quit()
                sys.exit()

        # 웹캠 이미지를 읽어온다.
        _, img = cam.read()
        # 좌우 반전 
        image = cv2.flip(img, 1)
        results = hands.process(image)

        # intro 화면을 띄운다.
        screen.fill(BLACK) 
        screen.blit(game_name_txt_render_1, (300, 70))
        screen.blit(game_name_txt_render_2, (170, 150))
        screen.blit(start_box_txt_render, (start_box.x + 10, start_box.y +5))
        screen.blit(info_txt_render, (230, 470))
        pygame.draw.rect(screen, WHITE, start_box, 4)

        # Spark VFX 효과를 일으킨다.
        for i, spark in sorted(enumerate(sparks), reverse=True):
            spark.move(1)
            spark.draw(screen)
            if not spark.alive:
                sparks.pop(i)

        # hand detection과 hand tracking을 구현한다.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                palm_x, palm_y = hand_landmarks.landmark[9].x*w, hand_landmarks.landmark[9].y*h
                _, finger_y = hand_landmarks.landmark[12].x*w, hand_landmarks.landmark[12].y*h

                pygame.draw.circle(screen, GREEN, (int(palm_x), int(palm_y)), 10)

                if finger_y > palm_y:

                    # 주먹을 쥐었을때 spark가 일어난다.
                    for i in range(10):
                        sparks.append(Spark([int(palm_x), int(palm_y)], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))

                    # 게임을 시작한다.
                    if start_box.collidepoint(int(palm_x), int(palm_y)):
                        game()
                         
        pygame.display.flip()
        clock.tick(maxframe)
    cam.release()
# ========================================================================================

# 게임의 outro를 만드는 함수를 정의한다. ===================================================
def end_game():
    global gst, Time, excellent_cnt, perfect_cnt, bad_cnt, miss_cnt, rate, combo, combo_effect, combo_effect2, miss_anim, last_combo, life_cnt

    # outro에서 사용할 font의 크기 및 위치를 변수로 정의한다.
    o1 = w / 25
    o2 = w / 35
    o3 = w / 30
    o4 = h * (1/10)

    # outro에서 띄울 총점을 계산한다.
    total_point = (excellent_cnt * 10) + (perfect_cnt * 5) + (bad_cnt * 3)

    # outro 화면에 띄울 문구를 작성한다.
    ingame_font_end = pygame.font.Font(font_file, int(o1))
    ingame_font_point = pygame.font.Font(font_file, int(o2))
    ingame_font_total = pygame.font.Font(font_file, int(o3))

    end_txt = 'Games Has Ended'
    excellent_txt = 'EXCELLENT : '
    perfect_txt = 'PERFECT : '
    bad_txt = 'BAD : '
    miss_txt = 'MISS : '
    total_txt = 'TOTAL POINT : '

    # 각 문자열에 개수를 추가한다.
    excellent_txt += str(excellent_cnt)
    perfect_txt += str(perfect_cnt)
    bad_txt += str(bad_cnt)
    miss_txt += str(miss_cnt)
    total_txt += str(total_point)

    # 각 문자열을 렌더링한다.
    end_txt_render = ingame_font_end.render(end_txt, False, WHITE)
    excellent_txt_render = ingame_font_point.render(excellent_txt, False, WHITE)
    perfect_txt_render = ingame_font_point.render(perfect_txt, False, WHITE)
    bad_txt_render = ingame_font_point.render(bad_txt, False, WHITE)
    miss_txt_render = ingame_font_point.render(miss_txt, False, WHITE)
    total_txt_render = ingame_font_total.render(total_txt, False, WHITE)

    # 버튼 이미지를 불러온다.
    quit_img = pygame.image.load(quit_path)
    restart_img = pygame.image.load(restart_path)

    # 이미지 사이즈를 지정한다.
    quit_img = pygame.transform.scale(quit_img, (100, 100))
    restart_img = pygame.transform.scale(restart_img, (100, 100))

    quit_button_box = pygame.Rect(w // 2 + 220, h // 2 - 55,  100, 100)
    restart_button_box = pygame.Rect(w // 2 - 330, h // 2 - 55,  100, 100)

    # outro를 실행한다.
    outro = True
    while outro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                outro = False
                pygame.quit()
                sys.exit()
        
        # 웹캠 이미지를 읽어온다.
        _, img = cam.read()
        # 좌우 반전 
        image = cv2.flip(img, 1)
        results = hands.process(image)
        
        # outro 화면을 띄운다.
        screen.fill(BLACK)
        screen.blit(end_txt_render, (w*(1/2) - end_txt_render.get_width() * (1/2), o4))
        screen.blit(excellent_txt_render, (w*(1/2) - excellent_txt_render.get_width() * (1/2), 3 * o4))
        screen.blit(perfect_txt_render, (w*(1/2) - perfect_txt_render.get_width() * (1/2), 4 * o4))
        screen.blit(bad_txt_render, (w*(1/2) - bad_txt_render.get_width() * (1/2), 5 * o4))
        screen.blit(miss_txt_render, (w*(1/2) - miss_txt_render.get_width() * (1/2), 6 * o4))
        screen.blit(total_txt_render, (w*(1/2) - total_txt_render.get_width() * (1/2), 8 * o4))
        screen.blit(quit_img, (w*(1/2) + 220,  4 * o4))
        screen.blit(restart_img, (w*(1/2) - 330,  4 * o4))
        pygame.draw.rect(screen, BLACK, quit_button_box, 2)
        pygame.draw.rect(screen, BLACK, restart_button_box, 2)

        # Spark VFX 효과를 일으킨다.
        for i, spark in sorted(enumerate(sparks), reverse=True):
            spark.move(1)
            spark.draw(screen)
            if not spark.alive:
                sparks.pop(i)

        # hand detection과 hand tracking을 구현한다
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                palm_x, palm_y = hand_landmarks.landmark[9].x*w, hand_landmarks.landmark[9].y*h
                _, finger_y = hand_landmarks.landmark[12].x*w, hand_landmarks.landmark[12].y*h

                pygame.draw.circle(screen, GREEN, (int(palm_x), int(palm_y)), 10)
                if finger_y > palm_y:

                    # 주먹을 쥐었을때 spark가 일어난다.
                    for i in range(10):
                        sparks.append(Spark([int(palm_x), int(palm_y)], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))

                    # 게임을 나간다.
                    if quit_button_box.collidepoint(int(palm_x), int(palm_y)):
                        outro = False
                        pygame.quit()
                        sys.exit()

                    # 초기화를 시키고 게임을 다시 시작한다.
                    if restart_button_box.collidepoint(int(palm_x), int(palm_y)):
                        outro = False
                        rate = 'START'
                        excellent_cnt = 0     
                        perfect_cnt = 0       
                        bad_cnt = 0           
                        miss_cnt = 0 
                        combo = 0
                        combo_effect = 0
                        combo_effect2 = 0
                        miss_anim = 0
                        last_combo = 0
                        life_cnt = 5
                        generate_notes()
                        simultaneous_notes()      
                        game()

        pygame.display.flip()
# ========================================================================================

# 게임이 종료되었을 때 뜨는 창을 만드는 함수를 정의한다. =====================================
def game_over():
    global gst, Time, excellent_cnt, perfect_cnt, bad_cnt, miss_cnt, rate, combo, combo_effect, combo_effect2, miss_anim, last_combo, life_cnt

    o1 = 1 / 2
    o2 = h / 10

    # 게임 오버되었을 때 창에 띄울 문자를 생성한다.
    ingame_font_over = pygame.font.Font(font_file, int(w / 20))
    over_txt = 'Game Over'
    over_txt_render = ingame_font_over.render(over_txt, False, WHITE)

    # 버튼 이미지를 불러온다.
    quit_img = pygame.image.load(quit_path)
    restart_img = pygame.image.load(restart_path)

    # 이미지 사이즈를 지정한다.
    quit_img = pygame.transform.scale(quit_img, (100, 100))
    restart_img = pygame.transform.scale(restart_img, (100, 100))
    quit_button_box = pygame.Rect(w // 2 + 220, h // 2 - 55,  100, 100)
    restart_button_box = pygame.Rect(w // 2 - 330, h // 2 - 55,  100, 100)

    # 게임이 종료되었을 때 실행되는 창을 띄운다.
    over = True
    while over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over = False
                pygame.quit()
                sys.exit()
        
        # 웹캠 이미지를 읽어온다.
        _, img = cam.read()
        # 좌우 반전 
        image = cv2.flip(img, 1)
        results = hands.process(image)

        # game over 화면을 띄운다.
        screen.fill(BLACK)
        screen.blit(over_txt_render, (w*o1 - over_txt_render.get_width() * o1, 3 * o2))
        screen.blit(quit_img, (w*o1 + 220,  4 * o2))
        screen.blit(restart_img, (w*o1 - 330,  4 * o2))
        pygame.draw.rect(screen, BLACK, quit_button_box, 2)
        pygame.draw.rect(screen, BLACK, restart_button_box, 2)

        # Spark VFX 효과를 일으킨다.
        for i, spark in sorted(enumerate(sparks), reverse=True):
            spark.move(1)
            spark.draw(screen)
            if not spark.alive:
                sparks.pop(i)

        # hand detection과 hand tracking을 구현한다
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                palm_x, palm_y = hand_landmarks.landmark[9].x*w, hand_landmarks.landmark[9].y*h
                _, finger_y = hand_landmarks.landmark[12].x*w, hand_landmarks.landmark[12].y*h

                pygame.draw.circle(screen, GREEN, (int(palm_x), int(palm_y)), 10)
                if finger_y > palm_y:

                    # 주먹을 쥐었을때 spark가 일어난다.
                    for i in range(10):
                        sparks.append(Spark([int(palm_x), int(palm_y)], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))


                    # 게임을 나간다.
                    if quit_button_box.collidepoint(int(palm_x), int(palm_y)):
                        over = False
                        pygame.quit()
                        sys.exit()

                    # 초기화를 시키고 게임을 다시 시작한다.
                    if restart_button_box.collidepoint(int(palm_x), int(palm_y)):
                        over = False
                        rate = 'START'
                        excellent_cnt = 0     
                        perfect_cnt = 0       
                        bad_cnt = 0           
                        miss_cnt = 0 
                        combo = 0
                        combo_effect = 0
                        combo_effect2 = 0
                        miss_anim = 0
                        last_combo = 0
                        life_cnt = 5
                        generate_notes()
                        simultaneous_notes()  
                        game()

        pygame.display.flip()
# ========================================================================================



# 게임을 시작한다.
start_game()