import pygame, math, time, os, random


# pygame moduel을 import하고 초기화한다.
pygame.init()

# 창 정보와 관련된 변수를 정의한다.
w = 1600
h = w * (9 / 16)

# 창 정보를 저장할 변수를 생성한다. 모든 효과는 screen에 띄운다.
screen = pygame.display.set_mode((w, h))

# 시간을 측정하기 위해 instance를 생성한다.
clock = pygame.time.Clock()

# 변수를 정의한다.
main = True
ingame = True

# 키 누름을 감지하는 list를 정의한다.
keys = [0, 0, 0, 0]
keyset = [0, 0, 0, 0]

# frame을 구한다. 노트의 감속을 위해 필요하다.
maxframe = 60
fps = 0

# 노트 위치 계산을 위해 초시계를 만든다.
gst = time.time()
Time = time.time() - gst

# 노트와 관련된 정보를 생성한다.
ty = 0        # 노트의 y 좌표
tst = Time    # 노트가 생성되는 시간
# 복사본을 위한 list를 생성한다. lane이 4개이므로 4개 생성한다.
t1 = []
t2 = []
t3 = []
t4 = []

# 게임 화면에 띄울 문자열을 생성한다.
rate = 'PERFECT'

# font 경로를 설정한다.
Cpath = os.path.dirname(__file__)
Fpath = os.path.join(Cpath, 'font')
ingame_font_rate = pygame.font.Font(os.path.join(Fpath, 'retro_game_font.ttf'), int(w / 30))

# 가져온 font로 렌더링한다.
rate_text = ingame_font_rate.render(str(rate), False, (255, 255, 255))

# 노트를 생성하는 함수를 만든다.
def sum_note(n):
    if n == 1:
        ty = 0
        tst = Time + 2
        t1.append([ty, tst])
    elif n == 2:
        ty = 0
        tst = Time + 2
        t2.append([ty, tst])
    elif n == 3:
        ty = 0
        tst = Time + 2
        t3.append([ty, tst])
    elif n == 4:
        ty = 0
        tst = Time + 2
        t4.append([ty, tst])

# 노트의 속도를 조절하는 변수를 만든다.
speed = 1

# 노트 소환을 위한 변수를 만든다.
notesumt = 0
num1 = 0
num2 = 0

# 화면에 문자를 띄우기 위한 변수를 만든다.
combo = 0
combo_effect = 0
combo_effect2 = 0
miss_anim = 0
last_combo = 0
combo_time = Time + 1

spin = 0

# 점수를 판정하는 함수를 만든다.
rate_data = [0, 0, 0, 0]
def rating(n):
    # rate_data의 n번째 노트들의 정보를 가져와 판단한다.
    global combo, miss_anim, last_combo, combo_effect, combo_effect2, combo_time, rate
    print((h/12)*9, rate_data[0], speed*(h/900)*15)
    if abs((h/12)*9 - rate_data[n-1] < 950*speed*(h/900) and (h/12)*9 - rate_data[n-1] >= 200*speed*(h/900)):
        last_combo = combo
        miss_anim = 1
        combo = 0
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        rate = 'WORST'
    if abs((h/12)*9 - rate_data[n-1]) < 200*speed*(h/900) and abs((h/12)*9 - rate_data[n-1]) >= 100*speed*(h/900):
        last_combo = combo
        miss_anim = 1
        combo = 0
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        rate = 'BAD'
    if abs((h/12)*9 - rate_data[n-1]) < 100*speed*(h/900) and abs((h/12)*9 - rate_data[n-1]) >= 50*speed*(h/900):
        combo += 1
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        rate = 'GOOD'
    if abs((h/12)*9 - rate_data[n-1]) < 50*speed*(h/900) and abs((h/12)*9 - rate_data[n-1]) >= 15*speed*(h/900):
        combo += 1
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        rate = 'GREAT'
    if abs((h/12)*9 - rate_data[n-1]) < 15*speed*(h/900) and abs((h/12)*9 - rate_data[n-1]) >= 0*speed*(h/900):
        combo += 1
        combo_effect = 0.2
        combo_time = Time + 1
        combo_effect2 = 1.3
        rate = 'PERFECT'


##############################################################################################
##############################################################################################

while main:
    while ingame:

        if len(t1) > 0:
            rate_data[0] = t1[0][0]
        if len(t2) > 0:
            rate_data[1] = t2[0][0]
        if len(t3) > 0:
            rate_data[2] = t3[0][0]
        if len(t4) > 0:
            rate_data[3] = t4[0][0]


        
        # 생성되는 노트의 수와 노트가 생성되는 lane 번호를 설정하는 부분
        if Time > 0.5 * notesumt:
            notesumt += 1
            while num1 == num2:
                num1 = random.randint(1, 4)
            sum_note(num1)
            num2 = num1

        Time = time.time() - gst

        # combo 글씨 생성
        ingame_font_combo = pygame.font.Font(os.path.join(Fpath, 'retro_game_font.ttf'), int((w / 45) * combo_effect2))
        combo_text = ingame_font_combo.render(str(combo), False, (255, 255, 255))

        # 점수 글씨 생성
        rate_text = ingame_font_rate.render(str(rate), False, (255, 255, 255))
        rate_text = pygame.transform.scale(rate_text, (int(w / 110 * len(rate) * combo_effect2), int((w / 60 * combo_effect * combo_effect2))))

        # miss 글씨 생성
        ingame_font_miss = pygame.font.Font(os.path.join(Fpath, 'retro_game_font.ttf'), int((w / 45 * miss_anim)))
        miss_text = ingame_font_miss.render(str(last_combo), False, (255, 0, 0))


        fps = clock.get_fps()
        if fps == 0:
            fps = maxframe


        # 이벤트 감지 코드를 작성한다.
        for event in pygame.event.get():
            # 창을 나가는 동작을 감지한다.
            if event.type == pygame.QUIT:
                # 창을 지운다.
                pygame.quit()
            # 입력 키를 설정한다.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    keyset[0] = 1
                    if len(t1) > 0:
                        if t1[0][0] > h / 3:
                            rating(1)
                            del t1[0]
                    
                if event.key == pygame.K_f:
                    keyset[1] = 1
                    if len(t2) > 0:
                        if t2[0][0] > h / 3:
                            rating(2)
                            del t2[0]
                    
                if event.key == pygame.K_j:
                    keyset[2] = 1
                    if len(t3) > 0:
                        if t3[0][0] > h / 3:
                            rating(3)
                            del t3[0]
                    
                if event.key == pygame.K_k:
                    keyset[3] = 1
                    if len(t4) > 0:
                        if t4[0][0] > h / 3:
                            rating(4)
                            del t4[0]
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    keyset[0] = 0
                if event.key == pygame.K_f:
                    keyset[1] = 0
                if event.key == pygame.K_j:
                    keyset[2] = 0
                if event.key == pygame.K_k:
                    keyset[3] = 0       
    

# gear========================================================================================
        # 화면을 그린다. 단색으로 채운다.
        screen.fill((0, 0, 0))

        # 움직임에 감속을 넣어주는 코드를 작성한다.
        keys[0] += (keyset[0] - keys[0]) / (3 * (maxframe / fps))
        keys[1] += (keyset[1] - keys[1]) / (3 * (maxframe / fps))
        keys[2] += (keyset[2] - keys[2]) / (3 * (maxframe / fps))
        keys[3] += (keyset[3] - keys[3]) / (3 * (maxframe / fps))


# text=========================================================================================
        # 텍스트의 움직임을 결정한다.
        if Time > combo_time:
            combo_effect += (0 - combo_effect) / (7 * (maxframe / fps))
        if Time < combo_time:
            combo_effect += (1 - combo_effect) / (7 * (maxframe / fps))
        
        combo_effect2 += (2 - combo_effect2) / (7 * (maxframe / fps))

        miss_anim += (4 - miss_anim) / (14 * (maxframe / fps))



# gear==========================================================================================
        # gear background
        pygame.draw.rect(screen, (0, 0, 0), (w / 2 - w / 8, -int(w / 100), w / 4, h + int(w / 50)))

# key 효과===================================================================================
# key를 눌렀을 때 생기는 효과를 만든다.
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200 - ((200 / 7) * i), 200 - ((200 / 7) * i), 200 - ((200 / 7) * i)), (w / 2 - w / 8 + w / 32 - (w / 32) * keys[0], (h / 12) * 9 - (h / 30) * keys[0] * i, w / 16 * keys[0], (h / 35) / i))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200 - ((200 / 7) * i), 200 - ((200 / 7) * i), 200 - ((200 / 7) * i)), (w / 2 - w / 16 + w / 32 - (w / 32) * keys[1], (h / 12) * 9 - (h / 30) * keys[1] * i, w / 16 * keys[1], (h / 35) / i))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200 - ((200 / 7) * i), 200 - ((200 / 7) * i), 200 - ((200 / 7) * i)), (w / 2 + w / 32 - (w / 32) * keys[2], (h / 12) * 9 - (h / 30) * keys[2] * i, w / 16 * keys[2], (h / 35) / i))
        for i in range(7):
            i += 1
            pygame.draw.rect(screen, (200 - ((200 / 7) * i), 200 - ((200 / 7) * i), 200 - ((200 / 7) * i)), (w / 2 + w / 16 + w / 32 - (w / 32) * keys[3], (h / 12) * 9 - (h / 30) * keys[3] * i, w / 16 * keys[3], (h / 35) / i))


        # gear line
        pygame.draw.rect(screen, (255, 255, 255), [w / 2 - w / 8, -int(w / 100), w / 4, h + int(w / 50)], int(w / 100))



# note=========================================================================================
        # 노트를 만든다.
        for tile_data in t1:
            # 렉이 걸려도 노트는 일정한 속도로 내려오도록 하는 코드를 작성한다.
            # 판정선 위치 기준             현재 시간 - 노트 소환 시간
            #                             시간이 경과할수록 이 부분의 차가 커져 노트가 내려간다.
            tile_data[0] = (h / 12) * 9 + (Time - tile_data[1]) * 350 * speed * (h / 900)
            pygame.draw.rect(screen, (255, 255, 255), (w / 2 - w / 8, tile_data[0] - h / 100, w / 16, h / 50))
            # 놓친 노트는 없앤다.
            if tile_data[0] > h - (h / 9):
                # 미스 판정을 만든다. 놓치면 해당 노트를 삭제한다.
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                rate = 'MISS'
                t1.remove(tile_data)

        
        for tile_data in t2:
            tile_data[0] = (h / 12) * 9 + (Time - tile_data[1]) * 350 * speed * (h / 900)
            pygame.draw.rect(screen, (255, 255, 255), (w / 2 - w / 16, tile_data[0] - h / 100, w / 16, h / 50))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                rate = 'MISS'
                t2.remove(tile_data)
        
        for tile_data in t3:
            tile_data[0] = (h / 12) * 9 + (Time - tile_data[1]) * 350 * speed * (h / 900)
            pygame.draw.rect(screen, (255, 255, 255), (w / 2, tile_data[0] - h / 100, w / 16, h / 50))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                rate = 'MISS'
                t3.remove(tile_data)
        
        for tile_data in t4:
            tile_data[0] = (h / 12) * 9 + (Time - tile_data[1]) * 350 * speed * (h / 900)
            pygame.draw.rect(screen, (255, 255, 255), (w / 2 + w / 16, tile_data[0] - h / 100, w / 16, h / 50))
            if tile_data[0] > h - (h / 9):
                last_combo = combo
                miss_anim = 1
                combo = 0
                combo_effect = 0.2
                combo_time = Time + 1
                combo_effect2 = 1.3
                rate = 'MISS'
                t4.remove(tile_data)





# blinder=============================================================================================
        # 판정선을 그린다.
        pygame.draw.rect(screen, (0, 0, 0), (w / 2 - w / 8, (h / 12) * 9, w / 4, h / 2))
        pygame.draw.rect(screen, (255, 0, 255), (w / 2 - w / 8, (h / 12) * 9, w / 4, h / 2), int(h / 100))





# key==================================================================================================
# 배경 화면을 꾸민다.
        pygame.draw.rect(screen, (255 - 100 * keys[0],255 - 100 * keys[0], 255 - 100 * keys[0]), (w / 2 - w / 9, (h / 24) * 19 + (h / 48) * keys[0], w / 27, h / 8), int(h / 150))
        pygame.draw.rect(screen, (255 - 100 * keys[3],255 - 100 * keys[3], 255 - 100 * keys[3]), (w / 2 + w / 13.5, (h / 24) * 19 + (h / 48) * keys[3], w / 27, h / 8), int(h / 150))

        pygame.draw.circle(screen, (150, 150, 150), (w / 2, (h / 24) * 21), (w / 20), int(h / 200))
        pygame.draw.line(screen, (150, 150, 150), (w / 2 - math.sin(spin) * 25 * (w / 1600), (h / 24) * 21 - math.cos(spin) * 25 * (w / 1600)), (w / 2 + math.sin(spin) * 25 * (w / 1600), (h / 24) * 21 + math.cos(spin) * 25 * (w / 1600)), int(w / 400))
        spin += (speed / 20 * (maxframe / fps))


        pygame.draw.rect(screen, (255 - 100 * keys[1], 255 - 100 * keys[1], 255 - 100 * keys[1]), (w / 2 - w / 18, (h / 48) * 39 + (h / 48) * keys[1], w / 27, h / 8))
        pygame.draw.rect(screen, (0,0, 0), (w / 2 - w / 18, (h / 48) * 43 + (h / 48) * (keys[1] * 1.2), w / 27, h / 64), int(h / 150))
        pygame.draw.rect(screen, (50,50, 50), (w / 2 - w / 18, (h / 48) * 39 + (h / 48) * keys[1], w / 27, h / 8), int(h / 150))

        pygame.draw.rect(screen, (255 - 100 * keys[2], 255 - 100 * keys[2], 255 - 100 * keys[2]), (w / 2 + w / 58, (h / 48) * 39 + (h / 48) * keys[2], w / 27, h / 8))
        pygame.draw.rect(screen, (0,0, 0), (w / 2 + w / 58, (h / 48) * 43 + (h / 48) * (keys[2] * 1.2), w / 27, h / 64), int(h / 150))
        pygame.draw.rect(screen, (50,50, 50), (w / 2 + w / 58, (h / 48) * 39 + (h / 48) * keys[2], w / 27, h / 8), int(h / 150))



        # font를 화면에 띄운다.
        miss_text.set_alpha(255 - (255 / 4) * miss_anim)
        screen.blit(combo_text, (w / 2 - combo_text.get_width() / 2, (h / 12) * 4 - combo_text.get_height() / 2))
        screen.blit(rate_text, (w / 2 - rate_text.get_width() / 2, (h / 12) * 8 - rate_text.get_height() / 2))
        screen.blit(miss_text, (w / 2 - miss_text.get_width() / 2, (h / 12) * 8 - miss_text.get_height() / 2))
        

        # 화면을 업데이트하는 함수를 정의한다. 이 코드가 없으면 화면이 보이지 않는다.
        pygame.display.flip()

        # frame 제한 코드
        clock.tick(maxframe)
    main = False
    ingame = False