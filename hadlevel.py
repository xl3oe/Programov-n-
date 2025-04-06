import pygame
import random
import time
import mysql.connector
import bcrypt

# Inicializace pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600  # Rozlišení
CELL_SIZE = 40  # Velikost buňky
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("HAD")

# Načtení obrázku jablka
try:
    apple_img_path = 'jablko.png'
    apple_img = pygame.image.load(apple_img_path)
    apple_img = pygame.transform.scale(apple_img, (CELL_SIZE, CELL_SIZE))
    apple_img_loaded = True
    print(f"Obrázek jablka úspěšně načten z: {apple_img_path}")
except pygame.error as e:
    print(f"Nepodařilo se načíst obrázek jablka: {e}")
    print("Používám barevný tvar místo jablka")
    apple_img_loaded = False

# Moderní barevné schéma
BACKGROUND_COLOR = (25, 25, 35)  # Tmavší, elegantnější pozadí
WHITE = (240, 240, 240)  # Čistě bílá
BLACK = (10, 10, 10)  # Téměř černá
GREEN = (76, 209, 55)  # Svěží zelená
DARK_GREEN = (0, 158, 96)  # Tmavší zelená pro hlavu hada
RED = (255, 59, 48)  # Apple-style červená
GOLD = (255, 204, 0)  # Jasnější zlatá
SILVER = (174, 174, 178)  # Moderní stříbrná
BRONZE = (164, 84, 51)  # Teplejší bronzová
PURPLE = (138, 43, 226)  # Jasná fialová pro speciální ovoce
BUTTON_COLOR = (52, 199, 89)  # Zelená pro tlačítka
BUTTON_HOVER = (48, 176, 82)  # Tmavší zelená pro hover efekt
BORDER_COLOR = (255, 59, 48)  # Červená pro okraje
GRID_COLOR = (45, 45, 55)  # Jemná barva mřížky

# Fonty pro text
try:
    title_font = pygame.font.Font("freesansbold.ttf", 48)
    font = pygame.font.Font("freesansbold.ttf", 36)
    small_font = pygame.font.Font("freesansbold.ttf", 24)
    print("Fonty úspěšně načteny")
except:
    # Fallback na základní fonty
    title_font = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    print("Používám základní fonty")

# MySQL připojení
try:
    mydb = mysql.connector.connect(
        host="dbs.spskladno.cz",
        user="student7",
        password="spsnet",
        database="vyuka7"
    )
    mycursor = mydb.cursor(buffered=True)
    db_connected = True
except mysql.connector.Error as err:
    print(f"Chyba připojení k databázi: {err}")
    db_connected = False

# Globální proměnné
username_temp = ""
input_active = False
input_text_value = ""
input_prompt = ""
input_callback = None
error_message = ""
error_time = 0
button_cooldown = 0
current_screen = "main"  # může být "main", "login", "register", "game_mode", "game", "input", "leaderboard"
logged_in_user = None  # Proměnná pro sledování přihlášeného uživatele
fullscreen = False  # Proměnná pro sledování fullscreen stavu
is_password_field = False  # Proměnná pro sledování, zda je aktuální vstup heslo
new_password = ""  # Pro ukládání nového hesla při změně

# Vytvoření tabulky pro uživatele (pokud neexistuje)
def create_user_table():
    if db_connected:
        try:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS game_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL
                );
            """)
            
            # Vytvoření tabulky pro skóre
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS game_scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    game_mode VARCHAR(20) NOT NULL,
                    score INT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Tabulka pro ukládání nejvyššího dosaženého levelu
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS game_levels (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    max_level INT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            mydb.commit()
            print("Tabulky v databázi byly vytvořeny nebo již existují")
        except mysql.connector.Error as err:
            print(f"Chyba při vytváření tabulky: {err}")

# Funkce pro vykreslení tlačítek
# Funkce pro vykreslení tlačítek - moderní design
# Funkce pro vykreslení tlačítek - moderní design s ošetřením hodnot barev
# Funkce pro vykreslení tlačítek - upravená pro správnou velikost textu a umístění
# Funkce pro vykreslení tlačítek - modernizovaná s konzistentním stínováním a fonty
# Komplexně přepracovaná funkce pro vykreslení tlačítek - bez stínů, s kontrolou šířky textu
def draw_button(text, x, y, width, height, action=None, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
    global button_cooldown, screen
    
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    # Zjistíme, jestli je myš nad tlačítkem
    hover = x + width > mouse_pos[0] > x and y + height > mouse_pos[1] > y
    
    # Vykreslení tlačítka s efektem hover a zaoblením
    button_rect = pygame.Rect(x, y, width, height)
    
    if hover:
        pygame.draw.rect(screen, hover_color, button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
    
    # Okraj tlačítka - jednoduchý, bez stínování
    border_color = (50, 50, 50)
    pygame.draw.rect(screen, border_color, button_rect, 2, border_radius=10)
    
    # Testovací render textu, abychom zjistili, zda se vejde
    test_text = font.render(text, True, WHITE)
    text_width = test_text.get_width()
    
    # Pokud je text širší než tlačítko, použijeme menší font
    if text_width > width - 20:
        # Začneme s fontem o velikosti 30 a snižujeme, dokud se text nevejde
        font_size = 30
        while font_size > 12 and text_width > width - 20:
            font_size -= 2
            smaller_font = pygame.font.Font("freesansbold.ttf", font_size)
            test_text = smaller_font.render(text, True, WHITE)
            text_width = test_text.get_width()
        
        button_text = smaller_font.render(text, True, WHITE)
    else:
        button_text = test_text
    
    # Finální rozměry textu
    text_width = button_text.get_width()
    text_height = button_text.get_height()
    
    # Vycentrování textu v tlačítku
    text_x = x + (width - text_width) // 2
    text_y = y + (height - text_height) // 2
    
    # Vykreslení textu
    screen.blit(button_text, (text_x, text_y))
    
    # Cooldown pro tlačítka
    current_time = pygame.time.get_ticks()
    if hover and click[0] == 1 and current_time - button_cooldown > 300:
        button_cooldown = current_time
        return True
    return False

# Přidejte tyto globální proměnné na začátek souboru, kde jsou ostatní globální proměnné
stars = []  # Seznam hvězd v pozadí
STAR_COUNT = 50  # Počet hvězd

# Funkce pro inicializaci hvězd - volejte ji před hlavní smyčkou
def initialize_stars():
    global stars
    stars = []
    for _ in range(STAR_COUNT):
        # Každá hvězda má souřadnice x, y, velikost a rychlost
        star = {
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT),
            "size": random.randint(1, 3),
            "speed": random.uniform(0.3, 1.0)  # Rychlost pohybu
        }
        stars.append(star)

# Funkce pro aktualizaci pozic hvězd - volejte ji v každém snímku
def update_stars():
    global stars
    for star in stars:
        # Pohyb hvězdy zleva doprava
        star["x"] += star["speed"]
        # Když hvězda dosáhne pravého okraje, vrátí se na levý
        if star["x"] > WIDTH:
            star["x"] = 0
            star["y"] = random.randint(0, HEIGHT)

# Funkce pro vykreslení hvězd - použijte ji místo náhodného vykreslování
def draw_stars():
    for star in stars:
        # Vykreslení hvězdy jako kroužku
        pygame.draw.circle(screen, (255, 255, 255), (int(star["x"]), int(star["y"])), star["size"])

# Funkce pro zobrazení informací o přihlášeném uživateli - vylepšený design
# Funkce pro zobrazení informací o přihlášeném uživateli - vylepšený design s tlačítkem "Změnit heslo"
# Funkce pro zobrazení informací o přihlášeném uživateli - nový design s oddělenými tlačítky
# Funkce pro zobrazení informací o přihlášeném uživateli - nový design s oddělenými tlačítky
def draw_login_info():
    global logged_in_user, current_screen
    
    if logged_in_user:
        # Tlačítko pro odhlášení - vlevo nahoře
        if draw_button("Odhlásit", 10, 10, 100, 30, color=(255, 59, 48), hover_color=(220, 30, 30)):
            logout()
            
        # Tlačítko pro nastavení - vpravo nahoře
        settings_button_x = WIDTH - 110
        if draw_button("Nastavení", settings_button_x, 10, 100, 30, color=(52, 120, 246), hover_color=(30, 90, 220)):
            # Přepnutí na novou obrazovku nastavení
            current_screen = "settings"
            
        # Zobrazení jména uživatele uprostřed nahoře
        user_label = small_font.render("Uživatel:", True, (180, 180, 190))
        user_text = small_font.render(f"{logged_in_user}", True, WHITE)
        
        # Pozice textu uživatele - uprostřed nahoře
        user_label_x = WIDTH // 2 - (user_label.get_width() + user_text.get_width() + 10) // 2
        screen.blit(user_label, (user_label_x, 15))
        screen.blit(user_text, (user_label_x + user_label.get_width() + 10, 15))

# Funkce pro odhlášení uživatele
def logout():
    global logged_in_user, current_screen
    logged_in_user = None
    current_screen = "main"
    print("Uživatel byl odhlášen")

# Funkce pro zobrazení hlavní obrazovky
# Funkce pro zobrazení hlavní obrazovky - moderní design
def draw_main_screen():
    # Pozadí s gradientem
    for y in range(HEIGHT):
        # Vytvořit plynulý přechod od tmavší k lehce světlejší barvě
        color_value = 25 + (y / HEIGHT) * 15
        pygame.draw.line(screen, (int(color_value), int(color_value), int(color_value + 10)), 
                        (0, y), (WIDTH, y))
    
    # Aktualizace a vykreslení hvězd v pozadí
    update_stars()
    draw_stars()
    
    # Logo hry
    title_shadow = title_font.render("HAD", True, (0, 0, 0))
    title_text = title_font.render("HAD", True, GREEN)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = HEIGHT // 4 - 50
    
    # Stínový efekt
    screen.blit(title_shadow, (title_x + 2, title_y + 2))
    screen.blit(title_text, (title_x, title_y))
    
    # Dekorativní podtržení titulku
    pygame.draw.line(screen, GREEN, 
                    (title_x, title_y + title_text.get_height() + 5),
                    (title_x + title_text.get_width(), title_y + title_text.get_height() + 5), 3)
    
    # Zobrazení informací o přihlášeném uživateli
    draw_login_info()
    
    # Kontejner pro tlačítka - vizuální seskupení
    buttons_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 300)
    pygame.draw.rect(screen, (35, 35, 45), buttons_rect, border_radius=15)
    pygame.draw.rect(screen, (60, 60, 70), buttons_rect, 2, border_radius=15)
    
    # Tlačítka pro login, registraci, a hraní
    button_y_start = HEIGHT // 2 - 80
    button_spacing = 60
    
    if not logged_in_user:  # Tlačítka Login a Register zobrazíme pouze pokud není nikdo přihlášen
        if draw_button("Přihlášení", WIDTH // 2 - 100, button_y_start, 200, 50):
            start_input("Zadej uživatelské jméno:", login_step1)
        
        if draw_button("Registrace", WIDTH // 2 - 100, button_y_start + button_spacing, 200, 50):
            start_input("Zadej uživatelské jméno:", register_step1)
        
        button_y = button_y_start + button_spacing * 2
    else:
        button_y = button_y_start
    
    # Tlačítko Play Game je vždy dostupné - výraznější
    if draw_button("Hrát Hru", WIDTH // 2 - 100, button_y, 200, 50, 
                 color=(76, 209, 55), hover_color=(66, 179, 45)):
        global current_screen
        current_screen = "game_mode"
    
    # Tlačítko pro žebříček
    if draw_button("Žebříček", WIDTH // 2 - 100, button_y + button_spacing, 200, 50, 
                 color=(255, 149, 0), hover_color=(215, 129, 0)):
        load_leaderboard()
        current_screen = "leaderboard"

    # Dolní lišta s dalšími ovládacími prvky
    footer_rect = pygame.Rect(0, HEIGHT - 80, WIDTH, 80)
    pygame.draw.rect(screen, (35, 35, 45), footer_rect)
    pygame.draw.line(screen, (60, 60, 70), (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 2)
    
    # Tlačítko pro přepnutí fullscreen
    # Tlačítko pro přepnutí fullscreen - širší pro celý text
    if draw_button("Fullscreen", WIDTH // 4 - 100, HEIGHT - 65, 200, 40, 
                color=(90, 90, 100), hover_color=(70, 70, 80)):
        toggle_fullscreen()
        
    # Tlačítko pro ukončení hry
    if draw_button("Ukončit", WIDTH * 3 // 4 - 80, HEIGHT - 65, 160, 40, 
                 color=(255, 59, 48), hover_color=(220, 30, 30)):
        pygame.quit()
        exit()

# Funkce pro zobrazení obrazovky s výběrem herního módu
# Funkce pro zobrazení obrazovky s výběrem herního módu - moderní design
# Funkce pro zobrazení obrazovky s výběrem herního módu - upravený design


# Funkce pro zobrazení obrazovky nastavení uživatele
# Funkce pro zobrazení obrazovky nastavení uživatele - s možností změny nicku
# Nahradit současnou funkci draw_settings_screen tímto čistějším kódem
def draw_settings_screen():
    global current_screen
    
    # Pozadí s gradientem
    for y in range(HEIGHT):
        color_value = 25 + (y / HEIGHT) * 15
        pygame.draw.line(screen, (int(color_value), int(color_value), int(color_value + 10)), 
                        (0, y), (WIDTH, y))
    
    # Titulek stránky
    title_text = title_font.render("Nastavení uživatele", True, WHITE)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = 40
    
    # Pozadí pro titulek
    title_bg = pygame.Rect(title_x - 20, title_y - 10, 
                          title_text.get_width() + 40, title_text.get_height() + 20)
    pygame.draw.rect(screen, (40, 40, 50), title_bg, border_radius=10)
    pygame.draw.rect(screen, (52, 120, 246), title_bg, 2, border_radius=10)
    
    screen.blit(title_text, (title_x, title_y))
    
    # Hlavní kontejner pro nastavení
    settings_width, settings_height = 500, 300
    settings_x = WIDTH // 2 - settings_width // 2
    settings_y = title_y + title_text.get_height() + 40
    
    settings_box = pygame.Rect(settings_x, settings_y, settings_width, settings_height)
    pygame.draw.rect(screen, (35, 35, 45), settings_box, border_radius=15)
    pygame.draw.rect(screen, (60, 60, 70), settings_box, 2, border_radius=15)
    
    # Informace o uživateli
    user_text = font.render(f"Uživatel: {logged_in_user}", True, WHITE)
    screen.blit(user_text, (settings_x + 30, settings_y + 30))
    
    # Tlačítko pro změnu hesla
    change_pass_y = settings_y + 100
    if draw_button("Změnit heslo", settings_x + settings_width//2 - 100, change_pass_y, 200, 50,
                 color=(52, 120, 246), hover_color=(30, 90, 220)):
        start_input("Zadejte staré heslo:", change_password_step1, is_password=True)
    
    # Tlačítko zpět
    if draw_button("Zpět", WIDTH // 2 - 100, HEIGHT - 80, 200, 50,
                 color=(90, 90, 100), hover_color=(70, 70, 80)):
        current_screen = "main"

# Funkce pro změnu přezdívky uživatele
def change_nickname(new_nickname):
    global logged_in_user, current_screen, error_message, error_time
    
    # Kontrola, zda uživatel zadal platnou přezdívku
    if not new_nickname or len(new_nickname) < 3:
        error_message = "Přezdívka musí mít alespoň 3 znaky."
        error_time = pygame.time.get_ticks()
        current_screen = "settings"
        return
    
    if db_connected:
        try:
            # Kontrola, zda nová přezdívka není již obsazena
            check_sql = "SELECT username FROM game_users WHERE username = %s AND username != %s"
            mycursor.execute(check_sql, (new_nickname, logged_in_user))
            exists = mycursor.fetchone()
            
            if exists:
                error_message = "Tato přezdívka je již obsazena."
                error_time = pygame.time.get_ticks()
                current_screen = "settings"
                return
            
            # Aktualizace přezdívky v databázi
            sql = "UPDATE game_users SET username = %s WHERE username = %s"
            mycursor.execute(sql, (new_nickname, logged_in_user))
            
            # Aktualizace přezdívky v tabulkách skóre a levelů
            sql_scores = "UPDATE game_scores SET username = %s WHERE username = %s"
            mycursor.execute(sql_scores, (new_nickname, logged_in_user))
            
            sql_levels = "UPDATE game_levels SET username = %s WHERE username = %s"
            mycursor.execute(sql_levels, (new_nickname, logged_in_user))
            
            mydb.commit()
            
            # Aktualizace přihlášeného uživatele
            old_username = logged_in_user
            logged_in_user = new_nickname
            
            error_message = f"Přezdívka úspěšně změněna z {old_username} na {new_nickname}!"
            error_time = pygame.time.get_ticks()
            current_screen = "settings"
            
        except mysql.connector.Error as err:
            print(f"Chyba při změně přezdívky: {err}")
            error_message = f"Chyba při změně přezdívky: {err}"
            error_time = pygame.time.get_ticks()
            current_screen = "settings"
    else:
        error_message = "Databáze není dostupná."
        error_time = pygame.time.get_ticks()
        current_screen = "settings"

def draw_game_mode_screen():
    global current_screen, screen
    
    # Jednoduché černé pozadí - méně rušivé
    screen.fill(BACKGROUND_COLOR)
    
    # Zobrazení informací o přihlášeném uživateli
    draw_login_info()
    
    # Titulek pro výběr módu - upravená velikost a pozice
    title_text = title_font.render("Vyberte mód hry", True, WHITE)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = HEIGHT // 4 - 60
    
    # Přidáme obdélník kolem titulku - jasné ohraničení
    title_bg = pygame.Rect(title_x - 20, title_y - 10, 
                          title_text.get_width() + 40, title_text.get_height() + 20)
    pygame.draw.rect(screen, (35, 35, 45), title_bg, border_radius=10)
    pygame.draw.rect(screen, (76, 209, 55), title_bg, 2, border_radius=10)
    
    screen.blit(title_text, (title_x, title_y))
    
    # Kontejner pro tlačítka s jasně definovanou velikostí
    box_width, box_height = 400, 300  # Menší box pro lepší umístění tlačítek
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    
    mode_box = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (35, 35, 45), mode_box, border_radius=15)
    pygame.draw.rect(screen, (60, 60, 70), mode_box, 2, border_radius=15)
    
    # Ikona hada (zjednodušená) pro klasický mód
    snake_y = box_y + 80
    for i in range(3):
        snake_segment = pygame.Rect(box_x + 50 + i*15, snake_y - 5, 15, 15)
        pygame.draw.rect(screen, GREEN, snake_segment, border_radius=5)
    
    # Tlačítko klasického módu - větší a s dostatkem prostoru pro text
    if draw_button("Klasický Had", box_x + box_width//2 - 100, snake_y - 10, 200, 50, 
                  color=GREEN, hover_color=(0, 180, 0)):
        start_game("classic")
    
    # Ikona úrovní (jednoduché schody) pro levelový mód
    level_y = snake_y + 80
    for i in range(3):
        level_step = pygame.Rect(box_x + 50 + i*15, level_y + 15 - i*10, 15, 10 + i*10)
        pygame.draw.rect(screen, PURPLE, level_step, border_radius=3)
    
    # Tlačítko levelového módu - větší a s dostatkem prostoru pro text
    if logged_in_user:
        if draw_button("Had na levely", box_x + box_width//2 - 100, level_y, 200, 50,
                    color=PURPLE, hover_color=(118, 23, 206)):
            start_game("levels")
    else:
        # Pokud uživatel není přihlášen, zobrazíme neaktivní tlačítko s upozorněním
        button_text = "Pro hraní se přihlašte"
        button_rect = pygame.Rect(box_x + box_width//2 - 100, level_y, 200, 50)
        pygame.draw.rect(screen, (80, 80, 90), button_rect, border_radius=10)
        
        text_surface = small_font.render(button_text, True, WHITE)
        text_x = button_rect.centerx - text_surface.get_width() // 2
        text_y = button_rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    # Tlačítko zpět v dolní části kontejneru - menší a úhledné
    if draw_button("Zpět", box_x + box_width//2 - 60, box_y + box_height - 50, 120, 40,
                  color=(90, 90, 100), hover_color=(70, 70, 80)):
        current_screen = "main"

# Funkce pro zpracování vstupu
def start_input(prompt, callback, is_password=False):
    global input_active, input_text_value, input_prompt, input_callback, current_screen, is_password_field
    input_active = True
    input_text_value = ""
    input_prompt = prompt
    input_callback = callback
    is_password_field = is_password
    current_screen = "input"

# Vylepšená input obrazovka s moderním designem
def draw_input_screen():
    global input_text_value, input_callback, current_screen
    
    # Pozadí s lehkým gradientem
    for y in range(HEIGHT):
        color_value = 25 + (y / HEIGHT) * 15
        pygame.draw.line(screen, (int(color_value), int(color_value), int(color_value + 10)), 
                        (0, y), (WIDTH, y))
    
    # Zobrazení informací o přihlášeném uživateli
    draw_login_info()
    
    # Moderní dialog box
    dialog_width, dialog_height = 500, 250
    dialog_x = WIDTH // 2 - dialog_width // 2
    dialog_y = HEIGHT // 2 - dialog_height // 2
    
    dialog = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (35, 35, 45), dialog, border_radius=15)
    pygame.draw.rect(screen, (76, 209, 55), dialog, 2, border_radius=15)
    
    # Záhlaví dialogu
    header = pygame.Rect(dialog_x, dialog_y, dialog_width, 50)
    pygame.draw.rect(screen, (52, 199, 89), header, border_top_left_radius=15, border_top_right_radius=15)
    
    # Text záhlaví
    header_text = font.render("Zadejte údaje", True, WHITE)
    screen.blit(header_text, (dialog_x + dialog_width//2 - header_text.get_width()//2, dialog_y + 10))
    
    # Prompt text
    prompt_text = font.render(input_prompt, True, WHITE)
    screen.blit(prompt_text, (dialog_x + dialog_width//2 - prompt_text.get_width()//2, dialog_y + 80))
    
    # Vykreslení vstupního boxu
    input_box = pygame.Rect(dialog_x + 50, dialog_y + 120, dialog_width - 100, 40)
    pygame.draw.rect(screen, (25, 25, 35), input_box, border_radius=5)
    pygame.draw.rect(screen, (120, 120, 130), input_box, 2, border_radius=5)
    
    # Pro hesla zobrazíme místo textu hvězdičky
    if is_password_field:
        display_text = '*' * len(input_text_value)
    else:
        display_text = input_text_value
        
    input_text_surface = font.render(display_text, True, WHITE)
    
    # Ořez textu, pokud je příliš dlouhý
    text_rect = input_box.copy()
    text_rect.left += 10
    text_rect.width -= 20
    screen.blit(input_text_surface, (text_rect.left, text_rect.top + 5), 
               (0, 0, text_rect.width, text_rect.height))
    
    # Blikající kurzor při aktivním vstupu
    if pygame.time.get_ticks() % 1000 < 500:
        cursor_x = text_rect.left + input_text_surface.get_width()
        if cursor_x < text_rect.right:
            pygame.draw.line(screen, WHITE, 
                            (cursor_x, text_rect.top + 5), 
                            (cursor_x, text_rect.bottom - 5), 2)
    
    # Tlačítka OK a Zrušit
    if draw_button("OK", dialog_x + dialog_width//4 - 60, dialog_y + dialog_height - 60, 120, 40,
                 color=(52, 199, 89), hover_color=(42, 189, 79)):
        # Kontrola, zda vstupní pole není prázdné
        if not input_text_value:
            global error_message, error_time
            error_message = "Vyplňte prosím pole"
            error_time = pygame.time.get_ticks()
        elif input_callback:
            temp_callback = input_callback
            input_active = False
            input_callback = None
            temp_callback(input_text_value)
    
    if draw_button("Zrušit", dialog_x + 3*dialog_width//4 - 60, dialog_y + dialog_height - 60, 120, 40,
                 color=(255, 59, 48), hover_color=(235, 39, 28)):
        input_active = False
        input_callback = None
        current_screen = "main"
    
    # Informace o klávesových zkratkách - POSUNUTÉ DOLŮ mimo dialog box
    info_text = small_font.render("Enter = OK, Esc = Zrušit", True, (180, 180, 190))
    screen.blit(info_text, (dialog_x + dialog_width//2 - info_text.get_width()//2, 
                          dialog_y + dialog_height + 15))  # Změněno na +15 místo -15

# Funkce pro kroky přihlášení (beze změn v logice)
def login_step1(username):
    global username_temp
    username_temp = username
    start_input("Zadej heslo:", login_step2, is_password=True)

def login_step2(password):
    global current_screen, error_message, error_time, logged_in_user
    
    if db_connected:
        try:
            sql = "SELECT password FROM game_users WHERE username = %s"
            mycursor.execute(sql, (username_temp,))
            result = mycursor.fetchone()

            if result:
                stored_password = result[0]
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    print("Přihlášení bylo úspěšné!")
                    logged_in_user = username_temp
                    current_screen = "game_mode"
                else:
                    error_message = "Nesprávné uživatelské jméno nebo heslo."
                    error_time = pygame.time.get_ticks()
                    current_screen = "main"
            else:
                error_message = "Uživatel neexistuje."
                error_time = pygame.time.get_ticks()
                current_screen = "main"
        except mysql.connector.Error as err:
            print(f"Chyba při přihlášení: {err}")
            error_message = f"Chyba při přihlášení: {err}"
            error_time = pygame.time.get_ticks()
            current_screen = "main"
    else:
        error_message = "Databáze není dostupná."
        error_time = pygame.time.get_ticks()
        current_screen = "main"

# Funkce pro kroky registrace (beze změn v logice)
def register_step1(username):
    global username_temp
    username_temp = username
    start_input("Zadej heslo:", register_step2, is_password=True)

def register_step2(password):
    global current_screen, error_message, error_time
    
    if db_connected:
        try:
            check_sql = "SELECT username FROM game_users WHERE username = %s"
            mycursor.execute(check_sql, (username_temp,))
            exists = mycursor.fetchone()
            
            if exists:
                error_message = "Uživatel již existuje. Zvolte jiné jméno."
                error_time = pygame.time.get_ticks()
                current_screen = "main"
                return
                
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            sql = "INSERT INTO game_users (username, password) VALUES (%s, %s)"
            val = (username_temp, hashed_password)
            mycursor.execute(sql, val)
            mydb.commit()
            print("Uživatel byl úspěšně zaregistrován!")
            error_message = "Registrace úspěšná! Nyní se můžete přihlásit."
            error_time = pygame.time.get_ticks()
            current_screen = "main"
        except mysql.connector.Error as err:
            print(f"Chyba při registraci: {err}")
            error_message = f"Chyba při registraci: {err}"
            error_time = pygame.time.get_ticks()
            current_screen = "main"
    else:
        error_message = "Databáze není dostupná."
        error_time = pygame.time.get_ticks()
        current_screen = "main"

# Kroky pro změnu hesla (beze změn v logice)
def change_password_step1(old_password):
    global logged_in_user
    if db_connected:
        try:
            sql = "SELECT password FROM game_users WHERE username = %s"
            mycursor.execute(sql, (logged_in_user,))
            result = mycursor.fetchone()

            if result:
                stored_password = result[0]
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')
                
                if bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
                    start_input("Zadej nové heslo:", change_password_step2, is_password=True)
                else:
                    global error_message, error_time
                    error_message = "Staré heslo je nesprávné."
                    error_time = pygame.time.get_ticks()
                    current_screen = "main"
                    return
            else:
                error_message = "Uživatel neexistuje."
                error_time = pygame.time.get_ticks()
                current_screen = "main"
        except mysql.connector.Error as err:
            print(f"Chyba při změně hesla: {err}")
            error_message = f"Chyba při změně hesla: {err}"
            error_time = pygame.time.get_ticks()
            current_screen = "main"

def change_password_step2(new_password_input):
    global new_password
    new_password = new_password_input
    start_input("Potvrďte nové heslo:", change_password_step3, is_password=True)

def change_password_step3(confirm_password):
    global logged_in_user, current_screen, input_text_value, error_message, error_time
    if new_password == confirm_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        if db_connected:
            try:
                # Aktualizace hesla v databázi
                sql = "UPDATE game_users SET password = %s WHERE username = %s"
                mycursor.execute(sql, (hashed_password, logged_in_user))
                mydb.commit()
                print("Heslo bylo úspěšně změněno!")
                current_screen = "main"
                error_message = "Heslo úspěšně změněno!"
                error_time = pygame.time.get_ticks()
            except mysql.connector.Error as err:
                print(f"Chyba při aktualizaci hesla: {err}")
                error_message = f"Chyba při aktualizaci hesla: {err}"
                error_time = pygame.time.get_ticks()
    else:
        error_message = "Hesla se neshodují."
        error_time = pygame.time.get_ticks()
        current_screen = "main"

# Funkce pro změnu jména uživatele
def change_username(new_username):
    global logged_in_user, current_screen, error_message, error_time
    
    # Kontrola, zda uživatel zadal platné jméno - stačí 1 znak
    if not new_username or len(new_username) < 1:
        error_message = "Uživatelské jméno nemůže být prázdné."
        error_time = pygame.time.get_ticks()
        current_screen = "settings"
        return
    
    if db_connected:
        try:
            # Kontrola, zda nové jméno není již obsazeno
            check_sql = "SELECT username FROM game_users WHERE username = %s AND username != %s"
            mycursor.execute(check_sql, (new_username, logged_in_user))
            exists = mycursor.fetchone()
            
            if exists:
                error_message = "Toto uživatelské jméno je již obsazeno."
                error_time = pygame.time.get_ticks()
                current_screen = "settings"
                return
            
            # Aktualizace jména v databázi
            sql = "UPDATE game_users SET username = %s WHERE username = %s"
            mycursor.execute(sql, (new_username, logged_in_user))
            
            # Aktualizace jména v tabulkách skóre a levelů
            sql_scores = "UPDATE game_scores SET username = %s WHERE username = %s"
            mycursor.execute(sql_scores, (new_username, logged_in_user))
            
            sql_levels = "UPDATE game_levels SET username = %s WHERE username = %s"
            mycursor.execute(sql_levels, (new_username, logged_in_user))
            
            mydb.commit()
            
            # Aktualizace přihlášeného uživatele
            old_username = logged_in_user
            logged_in_user = new_username
            
            error_message = f"Uživatelské jméno úspěšně změněno z {old_username} na {new_username}!"
            error_time = pygame.time.get_ticks()
            current_screen = "settings"
            
        except mysql.connector.Error as err:
            print(f"Chyba při změně jména: {err}")
            error_message = f"Chyba při změně jména: {err}"
            error_time = pygame.time.get_ticks()
            current_screen = "settings"
    else:
        error_message = "Databáze není dostupná."
        error_time = pygame.time.get_ticks()
        current_screen = "settings"

# Modernizovaná funkce pro zobrazení chybové zprávy
# Modernizovaná funkce pro zobrazení chybové zprávy
def draw_error_message():
    if pygame.time.get_ticks() - error_time < 3000:  # Zobrazení zprávy na 3 sekundy
        # Příprava textu
        error_text = font.render(error_message, True, WHITE)
        
        # Zjištění typu zprávy (chyba/úspěch) podle obsahu
        if "úspěšně" in error_message or "úspěšná" in error_message or "úspěšně změněno" in error_message:
            bg_color = (52, 199, 89)  # Zelená pro úspěch
        else:
            bg_color = (255, 59, 48)  # Červená pro chybu
        
        # Kompaktnější design zprávy - menší obdélník ve spodní části obrazovky
        message_width = error_text.get_width() + 40
        message_height = 50
        message_x = WIDTH // 2 - message_width // 2
        message_y = HEIGHT - 100  # Posunuto výš
        
        message_bg = pygame.Rect(message_x, message_y, message_width, message_height)
        
        # Zaoblený obdélník s průhledností
        s = pygame.Surface((message_width, message_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (bg_color[0], bg_color[1], bg_color[2], 220), 
                       (0, 0, message_width, message_height), border_radius=10)
        screen.blit(s, (message_x, message_y))
        
        # Tenký okraj
        pygame.draw.rect(screen, (255, 255, 255, 180), message_bg, 1, border_radius=10)
        
        # Vykreslení textu na střed
        screen.blit(error_text, (message_x + 20, message_y + message_height//2 - error_text.get_height()//2))

# Funkce pro uložení skóre do databáze (beze změny v logice)
def save_score(username, game_mode, score):
    if not db_connected or not username:
        return False
    
    try:
        # Nejprve zjistíme, jestli uživatel už má vyšší skóre v této hře
        check_sql = "SELECT MAX(score) FROM game_scores WHERE username = %s AND game_mode = %s"
        mycursor.execute(check_sql, (username, game_mode))
        result = mycursor.fetchone()
        
        # Uložíme skóre, pouze pokud je vyšší než dosavadní nebo uživatel ještě nemá žádné
        current_high_score = result[0] if result and result[0] is not None else 0
        
        if score > current_high_score:
            sql = "INSERT INTO game_scores (username, game_mode, score) VALUES (%s, %s, %s)"
            val = (username, game_mode, score)
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"Skóre {score} uloženo pro uživatele {username} v módu {game_mode}")
            return True
        else:
            print(f"Skóre {score} nebylo uloženo, protože není vyšší než dosavadní ({current_high_score})")
            return False
    
    except mysql.connector.Error as err:
        print(f"Chyba při ukládání skóre: {err}")
        return False
    
    
def draw_settings_screen():
    global current_screen
    
    # Pozadí s gradientem
    for y in range(HEIGHT):
        color_value = 25 + (y / HEIGHT) * 15
        pygame.draw.line(screen, (int(color_value), int(color_value), int(color_value + 10)), 
                        (0, y), (WIDTH, y))
    
    # Titulek stránky
    title_text = title_font.render("Nastavení uživatele", True, WHITE)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = 40
    
    # Pozadí pro titulek
    title_bg = pygame.Rect(title_x - 20, title_y - 10, 
                          title_text.get_width() + 40, title_text.get_height() + 20)
    pygame.draw.rect(screen, (40, 40, 50), title_bg, border_radius=10)
    pygame.draw.rect(screen, (52, 120, 246), title_bg, 2, border_radius=10)
    
    screen.blit(title_text, (title_x, title_y))
    
    # Hlavní kontejner pro nastavení
    settings_width, settings_height = 500, 350  # Zvětšíme výšku pro další tlačítko
    settings_x = WIDTH // 2 - settings_width // 2
    settings_y = title_y + title_text.get_height() + 40
    
    settings_box = pygame.Rect(settings_x, settings_y, settings_width, settings_height)
    pygame.draw.rect(screen, (35, 35, 45), settings_box, border_radius=15)
    pygame.draw.rect(screen, (60, 60, 70), settings_box, 2, border_radius=15)
    
    # Informace o uživateli
    user_text = font.render(f"Uživatel: {logged_in_user}", True, WHITE)
    screen.blit(user_text, (settings_x + 30, settings_y + 30))
    
    # Tlačítko pro změnu hesla
    change_pass_y = settings_y + 100
    if draw_button("Změnit heslo", settings_x + settings_width//2 - 100, change_pass_y, 200, 50,
                 color=(52, 120, 246), hover_color=(30, 90, 220)):
        start_input("Zadejte staré heslo:", change_password_step1, is_password=True)
    
    # Tlačítko pro změnu jména - umístíme ho pod tlačítko pro změnu hesla
    change_username_y = change_pass_y + 70
    if draw_button("Změnit jméno", settings_x + settings_width//2 - 100, change_username_y, 200, 50,
                 color=(52, 199, 89), hover_color=(42, 179, 79)):
        start_input("Zadejte nové uživatelské jméno:", change_username, is_password=False)
    
    # Tlačítko zpět - umístíme ho mimo settings_box, aby bylo viditelně oddělené
    back_button_x = WIDTH // 2 - 100
    back_button_y = HEIGHT - 80
    
    # Přidáme explicitní kontrolu na kliknutí na tlačítko
    back_clicked = draw_button("Zpět", back_button_x, back_button_y, 200, 50,
                             color=(90, 90, 100), hover_color=(70, 70, 80))
    
    # Pokud bylo kliknuto na tlačítko zpět, nastavíme obrazovku na hlavní
    if back_clicked:
        print("Tlačítko zpět bylo stisknuto - přepínám na hlavní obrazovku")
        current_screen = "main"
        return  # Okamžitě opustíme funkci

# Funkce pro uložení nejvyššího dosaženého levelu (beze změny v logice)
def save_level(username, level):
    if not db_connected or not username:
        return False
    
    try:
        # Zjistíme, jestli uživatel už má uložen nějaký level
        check_sql = "SELECT MAX(max_level) FROM game_levels WHERE username = %s"
        mycursor.execute(check_sql, (username,))
        result = mycursor.fetchone()
        
        # Uložíme level, pouze pokud je vyšší než dosavadní nebo uživatel ještě nemá žádný
        current_max_level = result[0] if result and result[0] is not None else 0
        
        if level > current_max_level:
            sql = "INSERT INTO game_levels (username, max_level) VALUES (%s, %s)"
            val = (username, level)
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"Level {level} uložen pro uživatele {username}")
            return True
        else:
            print(f"Level {level} nebyl uložen, protože není vyšší než dosavadní ({current_max_level})")
            return False
    
    except mysql.connector.Error as err:
        print(f"Chyba při ukládání levelu: {err}")
        return False

# Funkce pro načtení nejvyššího dosaženého levelu (beze změny v logice)
def get_highest_level(username):
    if not db_connected or not username:
        return 1
    
    try:
        sql = "SELECT MAX(max_level) FROM game_levels WHERE username = %s"
        mycursor.execute(sql, (username,))
        result = mycursor.fetchone()
        
        if result and result[0] is not None:
            return result[0]
        else:
            return 1
    except mysql.connector.Error as err:
        print(f"Chyba při načítání nejvyššího levelu: {err}")
        return 1

# Funkce pro načtení nejlepších skóre (beze změny v logice)
def load_leaderboard():
    global leaderboard_data
    leaderboard_data = {"classic": [], "levels": []}
    
    if not db_connected:
        return
    
    try:
        # Získání nejlepších 5 skóre pro klasický herní mód
        sql = """
            SELECT username, MAX(score) as high_score 
            FROM game_scores 
            WHERE game_mode = %s 
            GROUP BY username 
            ORDER BY high_score DESC 
            LIMIT 5
        """
        mycursor.execute(sql, ("classic",))
        leaderboard_data["classic"] = mycursor.fetchall()
        
        # Získání nejlepších 5 hráčů podle nejvyššího dosaženého levelu
        sql_levels = """
            SELECT username, MAX(max_level) as highest_level
            FROM game_levels
            GROUP BY username
            ORDER BY highest_level DESC
            LIMIT 5
        """
        mycursor.execute(sql_levels)
        leaderboard_data["levels"] = mycursor.fetchall()
            
    except mysql.connector.Error as err:
        print(f"Chyba při načítání žebříčku: {err}")

# Funkce pro zobrazení žebříčku - moderní design
# Funkce pro zobrazení žebříčku - vylepšená pro lepší využití prostoru
# Funkce pro zobrazení žebříčku - vylepšená s fixním tipem
# Funkce pro zobrazení žebříčku - vrácená do čistého designu
def draw_leaderboard_screen():
    # Pozadí s gradientem
    for y in range(HEIGHT):
        color_value = 25 + (y / HEIGHT) * 15
        color_blue = 35 + (y / HEIGHT) * 20
        pygame.draw.line(screen, (int(color_value), int(color_value), int(color_blue)), 
                        (0, y), (WIDTH, y))
    
    # Zobrazení informací o přihlášeném uživateli
    draw_login_info()
    
    # Titulek žebříčku s dekorativními prvky
    title_text = title_font.render("Žebříček nejlepších hráčů", True, GOLD)
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = 30
    
    # Pozadí pro titulek
    title_bg = pygame.Rect(title_x - 20, title_y - 10, 
                          title_text.get_width() + 40, title_text.get_height() + 20)
    pygame.draw.rect(screen, (40, 40, 50), title_bg, border_radius=10)
    pygame.draw.rect(screen, GOLD, title_bg, 2, border_radius=10)
    
    screen.blit(title_text, (title_x, title_y))
    
    # Vytvoření boxů pro každý herní mód
    modes = ["classic", "levels"]
    mode_names = {"classic": "Klasický mód", "levels": "Levelový mód"}
    mode_colors = {"classic": GREEN, "levels": PURPLE}
    
    for i, mode in enumerate(modes):
        # Kontejner pro žebříček módu
        box_width, box_height = WIDTH // 2 - 50, HEIGHT - 200
        box_x = 25 + i * (WIDTH // 2)
        box_y = 100
        
        mode_box = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (35, 35, 45), mode_box, border_radius=15)
        pygame.draw.rect(screen, mode_colors[mode], mode_box, 2, border_radius=15)
        
        # Nadpis módu
        mode_title = font.render(mode_names[mode], True, mode_colors[mode])
        mode_title_x = box_x + box_width // 2 - mode_title.get_width() // 2
        screen.blit(mode_title, (mode_title_x, box_y + 20))
        
        # Dekorativní linie pod nadpisem
        pygame.draw.line(screen, mode_colors[mode], 
                        (box_x + 20, box_y + 60), 
                        (box_x + box_width - 20, box_y + 60), 2)
        
        # Vykreslení záhlaví tabulky
        if mode == "classic":
            header_text = small_font.render("Hráč                   Skóre", True, WHITE)
        else:
            header_text = small_font.render("Hráč                   Level", True, WHITE)
        
        screen.blit(header_text, (box_x + 30, box_y + 80))
        
        # Vykreslení položek žebříčku
        for j, (username, score) in enumerate(leaderboard_data[mode]):
            entry_y = box_y + 120 + j * 50
            
            # Barevné pozadí pro položky
            if j % 2 == 0:
                entry_bg = pygame.Rect(box_x + 20, entry_y - 5, box_width - 40, 40)
                pygame.draw.rect(screen, (45, 45, 55), entry_bg, border_radius=5)
            
            # Barvy pro medailové pozice
            if j == 0:
                color = GOLD
                medal = "1"  
            elif j == 1:
                color = SILVER
                medal = "2"
            elif j == 2:
                color = BRONZE
                medal = "3"
            else:
                color = WHITE
                medal = f"{j+1}."
            
            # Zobrazení umístění, jména a skóre
            rank_text = font.render(f"{medal} {username}", True, color)
            
            # Pro levelový mód zobrazíme "Level" místo "Skóre"
            if mode == "levels":
                score_text = font.render(f"Level {score}", True, color)
            else:
                score_text = font.render(f"{score}", True, color)
            
            screen.blit(rank_text, (box_x + 30, entry_y))
            # Zarovnání skóre doprava
            score_x = box_x + box_width - 30 - score_text.get_width()
            screen.blit(score_text, (score_x, entry_y))
    
    # Tlačítko zpět s efektem
    back_button_x = WIDTH // 2 - 100
    back_button_y = HEIGHT - 80
    
    if draw_button("Zpět do menu", back_button_x, back_button_y, 200, 50,
                 color=(90, 90, 100), hover_color=(70, 70, 80)):
        global current_screen
        current_screen = "main"

    # Funkce pro výpočet různých parametrů pro jednotlivé levely (beze změny v logice)
# Úprava parametrů pro level 6
def get_level_parameters(level):
    # Základní nastavení pro level 1
    params = {
        "game_speed": 8,            # Rychlost hry
        "special_fruit_chance": 0,  # Šance na speciální ovoce (0-100)
        "obstacles": [],            # Seznam překážek (x, y) - VŽDY PRÁZDNÝ
        "fruits_to_win": 5,         # Počet ovoce potřebný k postupu do dalšího levelu
        "walls": True,              # Stěny jsou vždy smrtící
        "special_fruit_points": 3,  # Kolik bodů přidá speciální ovoce
        "moving_obstacles": False,  # Nemáme žádné překážky
        "shrinking_fruits": False,  # Zda ovoce zmizí po určitém čase
        "shrink_time": 0,           # Čas v sekundách, po kterém ovoce zmizí
        "maze_mode": False,         # Není žádný mód bludiště
        "maze_walls": []            # Nemáme žádné zdi pro bludiště
    }
    
    # Úprava parametrů podle levelu - pouze rychlost a počet ovoce
    if level >= 2:
        params["game_speed"] = 9
        params["fruits_to_win"] = 7
    
    if level >= 3:
        params["special_fruit_chance"] = 15
        params["fruits_to_win"] = 10
    
    if level >= 4:
        params["game_speed"] = 10
        params["special_fruit_chance"] = 20
        params["shrinking_fruits"] = True
        params["shrink_time"] = 5
    
    if level >= 5:
        params["fruits_to_win"] = 12
    
    if level >= 6:
        # OPRAVA: udržujeme rychlost na 10 až do levelu 10
        params["game_speed"] = 10
        params["special_fruit_chance"] = 25
    
    if level >= 7:
        # OPRAVA: zachováme rychlost 10, zvýšíme jen obtížnost jinými způsoby
        params["fruits_to_win"] = 15
        params["shrink_time"] = 5  # Méně času na sebrání mizejícího ovoce
    
    if level >= 8:
        # OPRAVA: zachováme rychlost 10, zvýšíme jen obtížnost jinými způsoby
        params["special_fruit_chance"] = 30
        params["shrink_time"] = 4.5
    
    if level >= 9:
        # OPRAVA: zachováme rychlost 10, zvýšíme jen obtížnost jinými způsoby
        params["fruits_to_win"] = 20
        params["shrink_time"] = 5
    
    if level >= 10:
        # OPRAVA: mírně zvýšíme rychlost, ale zůstaneme pod hranicí neovladatelnosti
        params["game_speed"] = 10.5
        params["special_fruit_chance"] = 40
        params["shrink_time"] = 4.5
        params["fruits_to_win"] = 25
    
    return params

# Funkce pro spuštění hry s moderním designem
# Funkce pro spuštění hry s moderním designem - upravená pro lepší využití prostoru ve fullscreenu
# Funkce pro spuštění hry s moderním designem - s fixním počtem buněk
# Funkce pro spuštění hry s moderním designem - opravená
# Funkce pro spuštění hry s moderním designem - s většími buňkami
def start_game(mode):
    global current_screen, error_message, error_time, WIDTH, HEIGHT
    current_screen = "game"
    
    # Pro levelový mód načteme nejvyšší dosažený level
    current_level = 1
    if mode == "levels" and logged_in_user:
        current_level = get_highest_level(logged_in_user)
    
    # Získáme parametry pro daný level
    level_params = {}
    if mode == "levels":
        level_params = get_level_parameters(current_level)
        game_speed = level_params["game_speed"]
    else:
        # Pro klasický mód vždy normální obtížnost
        game_speed = 8
    
    print(f"Spouštím hru v módu: {mode}, rychlost: {game_speed}")
    
    # Velikost buňky je vždy CELL_SIZE
    used_cell_size = CELL_SIZE
    
    # Dynamicky určujeme počet buněk podle velikosti obrazovky
    # Použijeme 80% dostupné šířky a 70% dostupné výšky
    # Fixní počet buněk bez ohledu na velikost obrazovky
    grid_cells_width = 15
    grid_cells_height = 10
    
    
    # Skutečné rozměry herní plochy
    game_width = grid_cells_width * CELL_SIZE
    game_height = grid_cells_height * CELL_SIZE
        
    # Centrování herní plochy
    game_area_x = (WIDTH - game_width) // 2
    game_area_y = (HEIGHT - game_height) // 2
    
    # OPRAVA: Ujistěte se, že herní plocha nebude mimo obrazovku
    # Kontrola X souřadnice
    if game_area_x < 0:
        game_area_x = 0
    elif game_area_x + game_width > WIDTH:
        game_area_x = max(0, WIDTH - game_width)
    
    # Kontrola Y souřadnice
    if game_area_y < 0:
        game_area_y = 0
    elif game_area_y + game_height > HEIGHT:
        game_area_y = max(0, HEIGHT - game_height)
    
    # Počáteční pozice hada musí být vždy uvnitř herní plochy
    # Kontrolujeme, aby had nezačínal příliš blízko okraje
    safe_margin = 3  # Minimální vzdálenost od okraje v buňkách
    start_cell_x = safe_margin
    start_cell_y = grid_cells_height // 2
    
    # OPRAVA: Ujistíme se, že počáteční pozice je vždy uvnitř herní plochy
    if start_cell_x >= grid_cells_width:
        start_cell_x = grid_cells_width // 4
    if start_cell_y >= grid_cells_height:
        start_cell_y = grid_cells_height // 2
    
    # Absolutní pozice hlavy hada
    start_x = game_area_x + start_cell_x * used_cell_size
    start_y = game_area_y + start_cell_y * used_cell_size
    
    # Počáteční pozice hada musí být vždy uvnitř herní plochy
    # Kontrolujeme, aby had nezačínal příliš blízko okraje
    safe_margin = 3  # Minimální vzdálenost od okraje v buňkách
    start_cell_x = safe_margin
    start_cell_y = grid_cells_height // 2
    
    # Absolutní pozice hlavy hada
    start_x = game_area_x + start_cell_x * used_cell_size
    start_y = game_area_y + start_cell_y * used_cell_size
    
    # Vytvoření těla hada - hlava a dva segmenty doprava
    snake = [(start_x, start_y), (start_x - used_cell_size, start_y), (start_x - 2 * used_cell_size, start_y)]
    
    # Počáteční pozice ovoce v herní ploše - vždy s odstupem od hada
    fruit_margin = 1  # Okraj v buňkách od hranice herní plochy
    
    # Ujistíme se, že ovoce nevznikne na hadovi
    valid_position = False
    while not valid_position:
        fruit_cell_x = random.randrange(fruit_margin, grid_cells_width - fruit_margin)
        fruit_cell_y = random.randrange(fruit_margin, grid_cells_height - fruit_margin)
        
        # Absolutní pozice ovoce
        fruit_x = game_area_x + fruit_cell_x * used_cell_size
        fruit_y = game_area_y + fruit_cell_y * used_cell_size
        fruit_candidate = (fruit_x, fruit_y)
        
        # Kontrola, zda ovoce není na hadovi
        if fruit_candidate not in snake:
            valid_position = True
            fruit = fruit_candidate
    
    # Uložení rozměrů herní plochy pro pozdější použití
    game_area = (game_area_x, game_area_y, game_width, game_height)
    
    snake_direction = (used_cell_size, 0)  # Počáteční směr: vpravo
    score = 0
    fruits_eaten = 0  # Pro levelový mód: počítání sebraných ovoce
    level_complete = False  # Pro levelový mód: indikátor dokončení levelu
    game_over = False
    special_fruit = None  # Pro levelový mód: speciální ovoce
    obstacles = []  # PŘEKÁŽKY JSOU VŽDY PRÁZDNÉ
    
    # Proměnné pro mizející ovoce
    fruit_spawn_time = pygame.time.get_ticks()  # Čas, kdy bylo ovoce vytvořeno
    
    # Důležité - definujeme proměnnou pro aktuální velikost buňky
    current_cell_size = used_cell_size
    
    # Definice proměnné progress_bar_width, kterou později používáme
    progress_bar_width = 150
    
    # Inicializace hodin
    clock = pygame.time.Clock()

    # Proměnná pro ukládání čekajících směrů pohybu (pro omezení rychlých změn směru)
    pending_direction = None
    last_move_time = pygame.time.get_ticks()
    
    # Nastavení zpoždění mezi změnami směru
    move_delay = 100  # Normální zpoždění
    
    # Efekt po startu hry - animace odpočtu
    show_countdown = True
    countdown_start = pygame.time.get_ticks()
    countdown_interval = 500  # Prodloužení intervalu na 1 sekundu
    countdown_size = 200  # Fixní základní velikost
    current_countdown_number = 3  # Aktuální číslo odpočtu

    while show_countdown and current_screen == "game":
        current_time = pygame.time.get_ticks()
        # Vypočítáme, které číslo má být zobrazeno
        countdown_time = (current_time - countdown_start) // countdown_interval
        
        if countdown_time >= 3:
            show_countdown = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                show_countdown = False
                game_over = True
                current_screen = "main"

        # Vykreslení pozadí s gradientem
        for y in range(HEIGHT):
            color_value_g = int(25 + (y / HEIGHT) * 10)
            color_value_b = int(35 + (y / HEIGHT) * 5)
            pygame.draw.line(screen, (25, color_value_g, color_value_b), 
                            (0, y), (WIDTH, y))
        
        # Zobrazení informací o přihlášeném uživateli během hry
        if logged_in_user:
            user_text = small_font.render(f"Hráč: {logged_in_user}", True, WHITE)
            screen.blit(user_text, (10, 10))
        
        # Zobrazení herního módu a levelu
        if mode == "levels":
            mode_text = small_font.render(f"Levelový mód - Level {current_level}", True, WHITE)
        else:
            mode_text = small_font.render("Klasický mód", True, WHITE)
        screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 10))
        
        # Vykreslení herní plochy s okrajem
        game_x, game_y, game_width, game_height = game_area
        border_width = 3
        
        # Pozadí herní plochy (mírně větší pro okraj)
        pygame.draw.rect(screen, (30, 30, 40), 
                    (game_x - border_width, game_y - border_width, 
                        game_width + 2*border_width, game_height + 2*border_width),
                    border_radius=10)
        
        # Vnitřní část herní plochy
        pygame.draw.rect(screen, (20, 20, 30), 
                    (game_x, game_y, game_width, game_height),
                    border_radius=8)
        
        # Odpočet se zvětšováním
        countdown_number = 3 - countdown_time
        if countdown_number > 0:
            # Použití fixní velikosti bez pulzování
            countdown_font = pygame.font.Font(None, countdown_size)
            countdown_text = countdown_font.render(str(countdown_number), True, WHITE)
            screen.blit(countdown_text, 
                    (WIDTH // 2 - countdown_text.get_width() // 2, 
                        HEIGHT // 2 - countdown_text.get_height() // 2))
        else:
            start_text = title_font.render("START!", True, GREEN)
            screen.blit(start_text, 
                    (WIDTH // 2 - start_text.get_width() // 2, 
                        HEIGHT // 2 - start_text.get_height() // 2))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Hlavní herní smyčka
    while not game_over and current_screen == "game":
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # OPRAVA: Okamžitá změna směru při stisknutí klávesy
                # Testujeme, zda nový směr vede ke srážce s vlastním tělem
                if event.key == pygame.K_UP and snake_direction != (0, CELL_SIZE):
                    new_direction = (0, -CELL_SIZE)
                    next_head = (snake[0][0] + new_direction[0], snake[0][1] + new_direction[1])
                    # Kontrola kolize s vlastním tělem (kromě posledního segmentu)
                    if next_head not in snake[:-1]:
                        snake_direction = new_direction
                        print("Klávesa NAHORU stisknuta - směr změněn")
                elif event.key == pygame.K_DOWN and snake_direction != (0, -CELL_SIZE):
                    new_direction = (0, CELL_SIZE)
                    next_head = (snake[0][0] + new_direction[0], snake[0][1] + new_direction[1])
                    if next_head not in snake[:-1]:
                        snake_direction = new_direction
                        print("Klávesa DOLŮ stisknuta - směr změněn")
                elif event.key == pygame.K_LEFT and snake_direction != (CELL_SIZE, 0):
                    new_direction = (-CELL_SIZE, 0)
                    next_head = (snake[0][0] + new_direction[0], snake[0][1] + new_direction[1])
                    if next_head not in snake[:-1]:
                        snake_direction = new_direction
                        print("Klávesa VLEVO stisknuta - směr změněn")
                elif event.key == pygame.K_RIGHT and snake_direction != (-CELL_SIZE, 0):
                    new_direction = (CELL_SIZE, 0)
                    next_head = (snake[0][0] + new_direction[0], snake[0][1] + new_direction[1])
                    if next_head not in snake[:-1]:
                        snake_direction = new_direction
                        print("Klávesa VPRAVO stisknuta - směr změněn")
                elif event.key == pygame.K_ESCAPE:
                    game_over = True
                    current_screen = "main"
                    print("Klávesa ESC stisknuta - ukončení hry")
                elif event.key == pygame.K_f:  # Přidáno pro rychlé přepnutí fullscreen během hry
                    toggle_fullscreen()
                    print("Klávesa F stisknuta - přepnutí fullscreen")
                    # Pokud jsme změnili režim, musíme hru restartovat
                    game_over = True
                    current_screen = "game_mode"
                    
        # Změníme směr pouze jednou za jeden tah, až když je had připraven na pohyb
        if pending_direction and (current_time - last_move_time) >= move_delay:
            # Kontrola, jestli by nový směr nevedl k okamžité srážce
            temp_head = (snake[0][0] + pending_direction[0], snake[0][1] + pending_direction[1])
            
            # Kontrola kolize s vlastním krkem - pouze pokud had má alespoň 2 segmenty
            if len(snake) < 2 or temp_head != snake[1]:
                snake_direction = pending_direction
                print(f"Směr změněn na: {snake_direction}")  # Diagnostický výpis
            else:
                print(f"Ignoruji změnu směru - vedla by ke kolizi s krkem")
    
            pending_direction = None
                
        # PŘIDÁNA KONTROLA KOLIZE S TĚLEM HADA
        next_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])
        
        # Kontrola kolize s tělem hada (kromě posledního segmentu, který se v dalším kroku posune)
        if next_head in snake[:-1]:
            game_over = True
            continue

        snake_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])
        snake = [snake_head] + snake[:-1]
        last_move_time = current_time

        # Získání rozměrů herní plochy
        game_x, game_y, game_width, game_height = game_area
        
        # Kontrola sebrání ovoce
        if snake_head == fruit:
            score += 1
            fruits_eaten += 1  # Přidáme počítadlo pro levelový mód
            snake.append(snake[-1])
            
            # Generování nového ovoce v rámci herní plochy s bezpečnostním okrajem
            margin = 1  # Okraj v buňkách od hranice
            grid_width = game_width // CELL_SIZE
            grid_height = game_height // CELL_SIZE
            
            # Ujistíme se, že ovoce nevznikne na hadovi
            valid_position = False
            while not valid_position:
                fruit_x = game_x + random.randrange(margin, grid_width - margin) * CELL_SIZE
                fruit_y = game_y + random.randrange(margin, grid_height - margin) * CELL_SIZE
                fruit_candidate = (fruit_x, fruit_y)
                
                # Kontrola, zda ovoce není na hadovi
                if fruit_candidate not in snake:
                    valid_position = True
                    fruit = fruit_candidate
                    fruit_spawn_time = pygame.time.get_ticks()  # Reset časovače ovoce
            
            # Pro levelový mód - kontrola dokončení levelu a speciální ovoce
            if mode == "levels":
                # Kontrola, zda bylo sebráno dostatek ovoce pro dokončení levelu
                if fruits_eaten >= level_params.get("fruits_to_win", 5):
                    level_complete = True
                    game_over = True
                
                # Vygenerování speciálního ovoce s určitou šancí
                special_fruit_chance = level_params.get("special_fruit_chance", 0)
                if random.randint(1, 100) <= special_fruit_chance and special_fruit is None:
                    # Generování speciálního ovoce na jiném místě než běžné ovoce
                    valid_position = False
                    while not valid_position:
                        special_x = game_x + random.randrange(margin, grid_width - margin) * CELL_SIZE
                        special_y = game_y + random.randrange(margin, grid_height - margin) * CELL_SIZE
                        special_candidate = (special_x, special_y)
                        
                        if (special_candidate != fruit and 
                            special_candidate not in snake):
                            valid_position = True
                            special_fruit = special_candidate
        
        # Kontrola sebrání speciálního ovoce (pouze pro levelový mód)
        if mode == "levels" and special_fruit and snake_head == special_fruit:
            # Přidání bodů za speciální ovoce
            score += level_params.get("special_fruit_points", 3)
            snake.append(snake[-1])  # Zvětšíme hada o 1
            snake.append(snake[-1])  # Zvětšíme hada o 2
            special_fruit = None  # Odstraníme speciální ovoce
        
        # Kontrola kolize s hranicemi herní plochy - VŽDY KONČÍ HRU
        if (snake_head[0] < game_x or 
            snake_head[0] >= game_x + game_width or 
            snake_head[1] < game_y or 
            snake_head[1] >= game_y + game_height):
            print(f"KOLIZE SE ZDÍ: {snake_head} je mimo herní oblast!")
            game_over = True
            continue  # Přeskočíme zbytek cyklu

        # Zpracování mizejícího ovoce
        if mode == "levels" and level_params.get("shrinking_fruits", False):
            shrink_time = level_params.get("shrink_time", 5) * 1000  # Převod na milisekundy
            current_time = pygame.time.get_ticks()
            
            # Pokud uplynul čas pro zmizení ovoce
            if current_time - fruit_spawn_time >= shrink_time:
                print("Čas pro sebrání ovoce vypršel - konec hry!")
                game_over = True  # Konec hry, když hráč nestihne sebrat ovoce včas
                continue  # Přeskočíme zbytek cyklu a necháme hru skončit

        # Vykreslení pozadí s mírným gradientem
        for y in range(HEIGHT):
            color_value_g = int(25 + (y / HEIGHT) * 10)
            color_value_b = int(35 + (y / HEIGHT) * 5)
            pygame.draw.line(screen, (25, color_value_g, color_value_b), 
                            (0, y), (WIDTH, y))
        
        # Zobrazení herního rozhraní - vrchní panel s informacemi
        # V části kódu, kde se vykresluje herní rozhraní - vrchní panel s informacemi
        info_panel = pygame.Rect(0, 0, WIDTH, 50)
        pygame.draw.rect(screen, (30, 30, 40), info_panel)
        pygame.draw.line(screen, (60, 60, 70), (0, 50), (WIDTH, 50), 2)

        # Zobrazení informací o přihlášeném uživateli během hry - posunuté více doleva
        if logged_in_user:
            user_text = small_font.render(f"Hráč: {logged_in_user}", True, WHITE)
            screen.blit(user_text, (10, 15))

        # Zobrazení skóre - výrazné, posunuté více doprava
        score_text = font.render(f"Skóre: {score}", True, WHITE)
        score_x = WIDTH - score_text.get_width() - 20
        screen.blit(score_text, (score_x, 10))

        # Zobrazení aktuálního levelu (pouze pro levelový mód) - pozice mezi hráčem a progress barem
        if mode == "levels":
            level_text = small_font.render(f"Level: {current_level}", True, WHITE)
            level_x = user_text.get_width() + 30  # Pozice hned za textem o hráči
            screen.blit(level_text, (level_x, 15))
            
            # Zobrazení počtu posbíraných ovoce / počet potřebný k dokončení - posunuté
            progress_text = small_font.render(f"Postup: {fruits_eaten}/{level_params.get('fruits_to_win', 5)}", True, WHITE)
            progress_x = level_x + level_text.get_width() + 30  # Pozice za textem o levelu
            screen.blit(progress_text, (progress_x, 15))
            
            # Grafický ukazatel postupu - posunutý hned za text o postupu
            progress_bar_width = 150
            progress_bar_height = 10
            progress_bar_x = progress_x + progress_text.get_width() + 10
            progress_bar_y = 20
            
            # Pozadí ukazatele
            pygame.draw.rect(screen, (40, 40, 50), 
                        (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 
                        border_radius=5)
            
            # Naplnění ukazatele podle postupu
            if level_params.get("fruits_to_win", 5) > 0:
                fill_width = int((fruits_eaten / level_params.get("fruits_to_win", 5)) * progress_bar_width)
                if fill_width > 0:
                    pygame.draw.rect(screen, GREEN, 
                                (progress_bar_x, progress_bar_y, fill_width, progress_bar_height), 
                                border_radius=5)
            
            # Naplnění ukazatele podle postupu
            if level_params.get("fruits_to_win", 5) > 0:
                fill_width = int((fruits_eaten / level_params.get("fruits_to_win", 5)) * progress_bar_width)
                if fill_width > 0:
                    pygame.draw.rect(screen, GREEN, 
                                   (progress_bar_x, progress_bar_y, fill_width, progress_bar_height), 
                                   border_radius=5)
        
        # Vykreslení herní plochy s okrajem
        # Pozadí herní plochy
        border_width = 3  # Šířka okraje
        
        # Pozadí s okrajem
        pygame.draw.rect(screen, (30, 30, 40), 
                       (game_x - border_width, game_y - border_width, 
                        game_width + 2*border_width, game_height + 2*border_width), 
                       border_radius=10)
        
        # Vnitřní část herní plochy
        pygame.draw.rect(screen, (20, 20, 30), 
                       (game_x, game_y, game_width, game_height), 
                       border_radius=8)
        
        # Okraj - kreslíme okraj MIMO herní plochu
        border_color = BORDER_COLOR
        if mode == "levels":
            # Změníme barvu okraje podle levelu
            if current_level % 3 == 0:
                border_color = GOLD
            elif current_level % 3 == 1:
                border_color = GREEN
            elif current_level % 3 == 2:
                border_color = PURPLE
        
        pygame.draw.rect(screen, border_color, 
                       (game_x - border_width, game_y - border_width, 
                        game_width + 2*border_width, game_height + 2*border_width), 
                        border_width, border_radius=10)
        
        # Vykreslení mřížky v herní ploše (ve všech režimech)
        grid_color = GRID_COLOR  # Jemná barva pro mřížku
        # Vertikální čáry
        for x in range(game_x, game_x + game_width + 1, CELL_SIZE):
            pygame.draw.line(screen, grid_color, (x, game_y), (x, game_y + game_height))
        # Horizontální čáry
        for y in range(game_y, game_y + game_height + 1, CELL_SIZE):
            pygame.draw.line(screen, grid_color, (game_x, y), (game_x + game_width, y))
        
        # Vykreslení hada - s modernějším vzhledem
        # V části kódu, kde se vykresluje had:
        for i, segment in enumerate(snake):
            # Pro vizuální efekt - had bude mít mírný gradient od hlavy k ocasu
            if i == 0:  # Hlava
                segment_color = DARK_GREEN
            else:
                # Postupné ztmavení směrem k ocasu
                green_value = max(0, int(GREEN[1] - (i * 5)))
                segment_color = (GREEN[0], green_value, GREEN[2])
            
            # Zaoblené segmenty hada pro lepší vzhled - použijeme current_cell_size
            pygame.draw.rect(screen, segment_color, 
                        (segment[0], segment[1], current_cell_size, current_cell_size), 
                        border_radius=5)
            
            # Přidáme vnitřní zvýraznění pro 3D efekt
            pygame.draw.rect(screen, (segment_color[0]+20, segment_color[1]+20, segment_color[2]+20), 
                        (segment[0]+3, segment[1]+3, current_cell_size-6, current_cell_size-6), 
                        border_radius=3)

        # A pro ovoce:
        if apple_img_loaded:
            # Upravíme velikost obrázku jablka podle aktuální velikosti buňky
            scaled_apple_img = pygame.transform.scale(apple_img, (current_cell_size, current_cell_size))
            screen.blit(scaled_apple_img, (fruit[0], fruit[1]))
        else:
            # Modernější vzhled ovoce - s gradientem a světelnými efekty
            pygame.draw.rect(screen, RED, (fruit[0], fruit[1], current_cell_size, current_cell_size), border_radius=10)
            # Světelný odlesk - malý bílý kruh v levém horním rohu
            pygame.draw.circle(screen, (255, 255, 255, 128), 
                            (fruit[0] + current_cell_size//4, fruit[1] + current_cell_size//4), 
                            current_cell_size//6)
        
        # Speciální efekt pro hlavu hada - oči
        head_x, head_y = snake[0]
        # Určení pozice očí podle směru pohybu
        eye_size = 4
        eye_offset = CELL_SIZE // 4
        
        if snake_direction == (CELL_SIZE, 0):  # Doprava
            left_eye = (head_x + CELL_SIZE - eye_offset, head_y + eye_offset)
            right_eye = (head_x + CELL_SIZE - eye_offset, head_y + CELL_SIZE - eye_offset)
        elif snake_direction == (-CELL_SIZE, 0):  # Doleva
            left_eye = (head_x + eye_offset, head_y + eye_offset)
            right_eye = (head_x + eye_offset, head_y + CELL_SIZE - eye_offset)
        elif snake_direction == (0, -CELL_SIZE):  # Nahoru
            left_eye = (head_x + eye_offset, head_y + eye_offset)
            right_eye = (head_x + CELL_SIZE - eye_offset, head_y + eye_offset)
        else:  # Dolů
            left_eye = (head_x + eye_offset, head_y + CELL_SIZE - eye_offset)
            right_eye = (head_x + CELL_SIZE - eye_offset, head_y + CELL_SIZE - eye_offset)
        
        pygame.draw.circle(screen, WHITE, left_eye, eye_size)
        pygame.draw.circle(screen, WHITE, right_eye, eye_size)
            
        # Vizualizace časovače pro mizející ovoce
        if mode == "levels" and level_params.get("shrinking_fruits", False):
            shrink_time = level_params.get("shrink_time", 5) * 1000  # Převod na milisekundy
            current_time = pygame.time.get_ticks()
            time_left = max(0, shrink_time - (current_time - fruit_spawn_time))
            
            # Kruhový odpočet kolem ovoce
            progress = time_left / shrink_time
            if progress > 0:
                # Vykreslení kruhu kolem ovoce
                timer_radius = int(CELL_SIZE * 0.8)  # O něco větší než ovoce
                timer_x = fruit[0] + CELL_SIZE // 2
                timer_y = fruit[1] + CELL_SIZE // 2
                
                # Kruhový timer
                pygame.draw.arc(screen, WHITE, 
                              (timer_x - timer_radius, timer_y - timer_radius, 
                               timer_radius*2, timer_radius*2), 
                              0, progress * 2 * 3.14159, 3)
        
        # Vykreslení speciálního ovoce (pouze pro levelový mód)
        if mode == "levels" and special_fruit:
            # Speciální ovoce s výrazným efektem
            pygame.draw.rect(screen, PURPLE, 
                        (special_fruit[0], special_fruit[1], CELL_SIZE, CELL_SIZE), 
                        border_radius=10)
            
            # Pulzující efekt - střídání velikosti rámečku
            pulse = int(5 + 3 * abs(math.sin(current_time / 200)))
            
            # Ošetření hodnot barev proti přetečení
            lighter_purple = (
                min(255, PURPLE[0] + 50),
                min(255, PURPLE[1] + 50),
                min(255, PURPLE[2] + 50)
            )
            
            pygame.draw.rect(screen, lighter_purple, 
                        (special_fruit[0] + pulse, special_fruit[1] + pulse, 
                            CELL_SIZE - 2*pulse, CELL_SIZE - 2*pulse), 
                        border_radius=max(1, pulse-2))
        
        pygame.display.flip()
        
        # Nastavení rychlosti hry
        if mode == "classic":
            # Pro klasický mód používáme pevnou základní rychlost
            current_speed = game_speed + min(score // 15, 3)
        else:
            # Pro levelový mód používáme rychlost zadanou v parametrech levelu
            current_speed = game_speed
            
        clock.tick(current_speed)  # Aplikace rychlosti

    # Po ukončení hry
    if game_over and current_screen == "game":
        # Pro levelový mód - postup do dalšího levelu pokud byl dokončen
        if mode == "levels" and level_complete and logged_in_user:
            next_level = current_level + 1
            level_saved = save_level(logged_in_user, next_level)
            
            if level_saved:
                level_message = f"Level {current_level} dokončen! Postupujete do levelu {next_level}."
            else:
                level_message = f"Level {current_level} dokončen!"
        else:
            level_message = ""
        
        # Uložení skóre do databáze pokud je uživatel přihlášen
        if logged_in_user:
            score_saved = save_score(logged_in_user, mode, score)
            if score_saved:
                save_message = "Nové nejvyšší skóre uloženo!"
            else:
                save_message = "Skóre zaznamenáno."
        else:
            save_message = "Pro uložení skóre se přihlaste."
        
        # Zobrazíme obrazovku konce hry s tlačítky
        show_game_over = True
        
        # Přidání efektu přechodu
        fade_alpha = 0
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        
        while fade_alpha < 180:  # Postupné ztmavení (ne úplně černá)
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            fade_alpha += 5
            pygame.time.delay(20)
        
        while show_game_over:
            # Pozadí s tmavším gradientem
            for y in range(HEIGHT):
                color_value = 15 + (y / HEIGHT) * 10
                pygame.draw.line(screen, (int(color_value), int(color_value), int(color_value + 5)), 
                                (0, y), (WIDTH, y))
            
            # Vytvoření karty pro konec hry
            card_width, card_height = 500, 400
            card_x = WIDTH // 2 - card_width // 2
            card_y = HEIGHT // 2 - card_height // 2
            
            card = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, (35, 35, 45), card, border_radius=15)
            
            # Záhlaví karty s odlišnou barvou podle výsledku
            header_height = 60
            header = pygame.Rect(card_x, card_y, card_width, header_height)
            
            if level_complete and mode == "levels":
                header_color = GREEN
                header_text = "LEVEL DOKONČEN!"
            else:
                header_color = RED
                header_text = "KONEC HRY"
            
            pygame.draw.rect(screen, header_color, header, 
                           border_top_left_radius=15, border_top_right_radius=15)
            
            # Text záhlaví
            header_font = pygame.font.Font(None, 48)
            header_surface = header_font.render(header_text, True, WHITE)
            screen.blit(header_surface, 
                       (card_x + card_width//2 - header_surface.get_width()//2, 
                        card_y + header_height//2 - header_surface.get_height()//2))
            
            # Obsah karty
            content_y = card_y + header_height + 20

            # Dosažené skóre - zvýrazněné
            final_score_text = font.render(f"Dosažené skóre: {score}", True, WHITE)
            screen.blit(final_score_text, 
                    (card_x + card_width//2 - final_score_text.get_width()//2, content_y))

            # Informace o uložení skóre
            if level_complete and mode == "levels":
                save_color = GREEN
            else:
                save_color = WHITE
                
            save_text = small_font.render(save_message, True, save_color)
            screen.blit(save_text, 
                    (card_x + card_width//2 - save_text.get_width()//2, content_y + 40))

            # Zobrazení zprávy o postupu do dalšího levelu
            if level_message:
                level_y = content_y + 80
                
                # Rozdělíme zprávu na dvě části, pokud je příliš dlouhá
                if len(level_message) > 30:
                    # Najděme vhodné místo pro zalomení textu
                    split_point = level_message.find("! ")
                    if split_point == -1:  # Pokud nenajdeme "! ", hledáme mezeru kolem středu
                        mid_point = len(level_message) // 2
                        split_point = level_message.rfind(" ", 0, mid_point)
                    
                    if split_point != -1:
                        first_line = level_message[:split_point+1]  # Včetně znaku na split_point
                        second_line = level_message[split_point+1:]
                        
                        # Vykreslení obou řádků
                        level_text1 = font.render(first_line, True, GOLD)
                        level_text2 = font.render(second_line, True, GOLD)
                        
                        screen.blit(level_text1, 
                                (card_x + card_width//2 - level_text1.get_width()//2, level_y))
                        screen.blit(level_text2, 
                                (card_x + card_width//2 - level_text2.get_width()//2, level_y + 40))
                        
                        buttons_y = level_y + 100  # Posuneme tlačítka níže
                    else:
                        # Pokud nelze vhodně rozdělit, zmenšíme text
                        smaller_font = pygame.font.Font("freesansbold.ttf", 30)
                        level_text = smaller_font.render(level_message, True, GOLD)
                        screen.blit(level_text, 
                                (card_x + card_width//2 - level_text.get_width()//2, level_y))
                        buttons_y = level_y + 60
                else:
                    # Pro kratší zprávy použijeme normální vykreslení
                    level_text = font.render(level_message, True, GOLD)
                    screen.blit(level_text, 
                            (card_x + card_width//2 - level_text.get_width()//2, level_y))
                    buttons_y = level_y + 60
            else:
                buttons_y = content_y + 100
            
            # Tlačítka pro další akce
            button_width = 200
            button_spacing = 30
            
            # Různá tlačítka podle herního módu
            if mode == "levels" and level_complete:
    # Pro dokončený level nabídneme postup do dalšího
                next_button_x = card_x + card_width//2 - button_width - button_spacing//2
                next_button_y = buttons_y
                
                if draw_button("Další level", next_button_x, next_button_y, button_width, 50,
                            color=GREEN, hover_color=(0, 180, 0)):
                    show_game_over = False
                    start_game("levels")  # Spustíme hru v levelovém módu
                    return
                    
                menu_button_x = card_x + card_width//2 + button_spacing//2
                
                if draw_button("Zpět do menu", menu_button_x, next_button_y, button_width, 50,
                            color=(90, 90, 100), hover_color=(70, 70, 80)):
                    show_game_over = False
                    current_screen = "game_mode"
            else:
                # Pro klasický mód nebo nedokončený level
                if draw_button("Hrát znovu", card_x + card_width//2 - button_width - button_spacing//2, 
                            buttons_y, button_width, 50,
                            color=GREEN, hover_color=(0, 180, 0)):
                    show_game_over = False
                    start_game(mode)  # Restartujeme stejný herní mód
                    return
                
                if draw_button("Zpět do menu", card_x + card_width//2 + button_spacing//2, 
                            buttons_y, button_width, 50,
                            color=(90, 90, 100), hover_color=(70, 70, 80)):
                    show_game_over = False
                    current_screen = "game_mode"

            # Tlačítko pro zobrazení žebříčku - umístěno doprostřed karty, pod hlavními tlačítky
            # OPRAVENO: snížení velikosti tlačítka a centrování uvnitř karty
            # Tlačítko pro zobrazení žebříčku - umístěno doprostřed karty, pod hlavními tlačítky
            leaderboard_button_y = buttons_y + 70
            leaderboard_button_width = card_width - 40  # Šířka tlačítka přes celou kartu s odsazením

            if draw_button("Zobrazit žebříček", 
                        card_x + 20,  # Zarovnání doleva s odsazením 
                        leaderboard_button_y, 
                        leaderboard_button_width, 50,
                        color=(52, 152, 219), hover_color=(41, 128, 185)):
                show_game_over = False
                load_leaderboard()
                current_screen = "leaderboard"
            
            # Zpracování událostí
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    show_game_over = False
                    current_screen = "main"
            
            pygame.display.flip()
            clock.tick(60)

            # Funkce pro přepnutí fullscreen
# Funkce pro přepnutí fullscreen
def toggle_fullscreen():
    global fullscreen, WIDTH, HEIGHT, screen, current_screen, CELL_SIZE
    fullscreen = not fullscreen
    
    if fullscreen:
        temp_surf = screen.copy()  # Uložíme aktuální obsah obrazovky
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()  # Aktualizace rozměrů
        CELL_SIZE *= 2  # Zvětšíme velikost buňky na dvojnásobek
        screen.blit(pygame.transform.scale(temp_surf, (WIDTH, HEIGHT)), (0, 0))  # Obnovíme obsah obrazovky se změněnou velikostí
        
        # Přeinicializujeme hvězdy pro novou velikost obrazovky
        initialize_stars()
    else:
        temp_surf = screen.copy()  # Uložíme aktuální obsah obrazovky
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        WIDTH, HEIGHT = 800, 600  # Vrátíme zpět výchozí rozměry
        CELL_SIZE = 40  # Vrátíme velikost buňky na původní hodnotu
        screen.blit(pygame.transform.scale(temp_surf, (WIDTH, HEIGHT)), (0, 0))  # Obnovíme obsah obrazovky se změněnou velikostí
        
        # Přeinicializujeme hvězdy pro novou velikost obrazovky
        initialize_stars()
        
    print(f"Fullscreen: {fullscreen}, Rozměry: {WIDTH}x{HEIGHT}, Velikost buňky: {CELL_SIZE}")
    
    # Pokud jsme ve hře, restartujeme ji při změně režimu
    if current_screen == "game":
        current_screen = "game_mode"

# Hlavní herní smyčka
# Hlavní herní smyčka
# Upravená hlavní herní smyčka, která zajistí kontinuální vykreslování
def main_loop():
    global input_text_value, input_active, current_screen, error_message, error_time, input_callback, WIDTH, HEIGHT, screen
    
    # Inicializace hvězd
    initialize_stars()
    
    clock = pygame.time.Clock()
    running = True
    
    # Přidáme animaci načítání
    loading_alpha = 255
    loading_surface = pygame.Surface((WIDTH, HEIGHT))
    loading_surface.fill((25, 25, 35))
    
    # Logo při spuštění
    logo_text = title_font.render("HAD", True, GREEN)
    loading_surface.blit(logo_text, 
                       (WIDTH // 2 - logo_text.get_width() // 2, HEIGHT // 2 - logo_text.get_height() // 2))
    
    # Podpis
    author_text = small_font.render("© Vikyho projekt na programování", True, WHITE)
    loading_surface.blit(author_text, 
                       (WIDTH // 2 - author_text.get_width() // 2, HEIGHT // 2 + 50))
    
    # Zobrazení úvodní obrazovky
    screen.blit(loading_surface, (0, 0))
    pygame.display.flip()
    pygame.time.delay(1500)  # Krátké čekání pro efekt
    
    # Postupné zmizení úvodní obrazovky
    while loading_alpha > 0:
        loading_surface.set_alpha(loading_alpha)
        
        # Začínáme kreslit hlavní obrazovku pod načítací
        draw_main_screen()
        
        # Navrch přidáme postupně mizející načítací obrazovku
        screen.blit(loading_surface, (0, 0))
        pygame.display.flip()
        
        loading_alpha -= 5
        pygame.time.delay(20)
    
    while running:
        # Zpracování událostí
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Reagování na změnu velikosti okna
            if event.type == pygame.VIDEORESIZE and not fullscreen:
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                print(f"Okno změněno na: {WIDTH}x{HEIGHT}")
            
            # Zpracování vstupu pokud je aktivní vstupní obrazovka
            if input_active and current_screen == "input":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        temp_callback = input_callback  # Uložíme referenci před resetováním
                        input_active = False
                        input_callback = None
                        if temp_callback:  # Zkontrolujeme, že callback existuje
                            temp_callback(input_text_value)
                    elif event.key == pygame.K_BACKSPACE:
                        input_text_value = input_text_value[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False
                        input_callback = None
                        current_screen = "main"
                    else:
                        input_text_value += event.unicode
            
            # Klávesová zkratka pro fullscreen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
        
        # Vykreslení obrazovky podle aktuálního stavu
        if current_screen == "main":
            draw_main_screen()
        elif current_screen == "game_mode":
            draw_game_mode_screen()
        elif current_screen == "input":
            draw_input_screen()
        elif current_screen == "leaderboard":
            draw_leaderboard_screen()
        elif current_screen == "settings":
            draw_settings_screen()
        
        # Zobrazení chybové zprávy pokud existuje
        if error_message:
            draw_error_message()
            # Reset chybové zprávy po určitém čase
            if pygame.time.get_ticks() - error_time > 3000:
                error_message = ""
        
        # Vždy aktualizujeme hvězdy a překreslíme celou obrazovku, bez ohledu na vstup
        update_stars()
        
        pygame.display.flip()  # Překreslení celé obrazovky
        clock.tick(60)  # Omezení na 60 FPS - zajistí plynulost
    
    pygame.quit()

# Globální proměnná pro uchování dat žebříčku
leaderboard_data = {"classic": [], "levels": []}

# Spuštění aplikace
if __name__ == "__main__":
    # Pokus o import modulu math pro pokročilejší efekty
    try:
        import math
    except ImportError:
        # Definujeme zjednodušenou náhradu funkce sin
        class math:
            @staticmethod
            def sin(x):
                return 0  # Zjednodušená implementace pro případ chybějícího modulu
    
    create_user_table()
    main_loop()
