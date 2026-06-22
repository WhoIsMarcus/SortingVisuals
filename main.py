import pygame

pygame.init()

# starting array to sort
arr = [
  43, 42, 92, 10, 66, 51, 2, 71, 16, 79,
  74, 11, 56, 57, 73, 46, 49, 93, 77, 38,
  31, 22, 33, 97, 81, 50, 84, 27, 88, 34,
  9, 48, 60, 64, 75, 45, 99, 53, 86, 13,
  37, 24, 40, 41, 19, 67, 62, 61, 8, 35,
  100, 47, 3, 52, 17, 39, 59, 69, 23, 63,
  25, 6, 7, 68, 83, 20, 80, 44, 91, 21,
  1, 96, 58, 94, 54, 90, 26, 72, 85, 78,
  65, 30, 28, 89, 98, 5, 55, 76, 12, 70,
  87, 14, 18, 29, 32, 36, 95, 4, 15, 82
]

# window size
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

SCALE = 4  # bar height scale
STATE = "MENU"  # current screen
auto = False  # autoplay toggle

# list of algorithms
algorithms = ["Bubble", "Selection", "Insertion", "Quick", "Merge"]

# target time for each algorithm
target_times = {
    "Bubble": 8.0,
    "Selection": 6.0,
    "Insertion": 5.0,
    "Quick": 2.5,
    "Merge": 3.5
}

selected_index = 0  # menu selection index

# sorting algorithms (each yields steps)

def bubble(a):
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            yield a, j  # show comparison
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                yield a, j  # show swap

def selection(a):
    n = len(a)
    for i in range(n):
        min_i = i
        for j in range(i + 1, n):
            if a[j] < a[min_i]:
                min_i = j
            yield a, j  # show scan
        a[i], a[min_i] = a[min_i], a[i]
        yield a, i  # show swap

def insertion(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            yield a, j  # show shift
            j -= 1
        a[j + 1] = key
        yield a, i  # show insert

def quick(a):
    stack = [(0, len(a) - 1)]
    while stack:
        l, r = stack.pop()
        if l >= r:
            continue
        pivot = a[r]
        i = l
        for j in range(l, r):
            yield a, j  # show scan
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                yield a, i  # show swap
                i += 1
        a[i], a[r] = a[r], a[i]
        yield a, i  # show pivot swap
        stack.append((l, i - 1))
        stack.append((i + 1, r))

def merge(a):
    w = 1
    n = len(a)
    while w < n:
        for i in range(0, n, 2 * w):
            a[i:i + 2 * w] = sorted(a[i:i + 2 * w])
            yield a, i  # show merge
        w *= 2

# counts how many steps a generator will yield
def count_steps(func, arr):
    temp = arr.copy()
    g = func(temp)
    c = 0
    for _ in g:
        c += 1
    return c

# color based on value
def color(v):
    t = v / 100
    return (int(t * 255), int(80 * (1 - t)), int(255 * (1 - t)))

# draw bars
def draw(arr, highlight):
    screen.fill((0, 0, 0))
    MARGIN = 20
    usable = WIDTH - 2 * MARGIN
    spacing = max(1, usable // (len(arr) * 10))
    bar_w = (usable - spacing * (len(arr) - 1)) / len(arr)
    total = len(arr) * bar_w + (len(arr) - 1) * spacing
    start = (WIDTH - total) / 2
    for i, v in enumerate(arr):
        h = min(v * SCALE, HEIGHT - 20)
        x = start + i * (bar_w + spacing)
        y = HEIGHT - h
        c = color(v)
        if i == highlight:
            c = (0, 255, 0)  # highlight bar
        pygame.draw.rect(screen, c, pygame.Rect(x, y, bar_w, h))

# draw menu screen
def menu():
    screen.fill((20, 20, 20))
    font = pygame.font.SysFont(None, 40)
    small = pygame.font.SysFont(None, 28)
    screen.blit(font.render("Pick Algorithm (1-5)", True, (255, 255, 255)), (270, 40))
    for i, name in enumerate(algorithms):
        t = f"{i+1}. {name}  |  speed: {target_times[name]:.1f}s"
        screen.blit(small.render(t, True, (200, 200, 200)), (250, 120 + i * 40))
    screen.blit(small.render("Use UP/DOWN to change speed BEFORE starting", True, (120, 120, 120)), (180, 380))

# main loop setup
running = True
gen = None
working = arr.copy()
highlight = None
current_algo = None
step_count = 1

# main loop
while running:
    clock.tick(60)  # limit FPS

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if STATE == "MENU":
                if e.key == pygame.K_UP:
                    target_times[algorithms[selected_index]] += 0.5
                if e.key == pygame.K_DOWN:
                    target_times[algorithms[selected_index]] = max(0.5, target_times[algorithms[selected_index]] - 0.5)

                # pick algorithm
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    selected_index = e.key - pygame.K_1
                    current_algo = algorithms[selected_index]
                    working = arr.copy()

                    # start generator + count steps
                    if current_algo == "Bubble":
                        gen = bubble(working)
                        step_count = count_steps(bubble, arr)
                    elif current_algo == "Selection":
                        gen = selection(working)
                        step_count = count_steps(selection, arr)
                    elif current_algo == "Insertion":
                        gen = insertion(working)
                        step_count = count_steps(insertion, arr)
                    elif current_algo == "Quick":
                        gen = quick(working)
                        step_count = count_steps(quick, arr)
                    elif current_algo == "Merge":
                        gen = merge(working)
                        step_count = count_steps(merge, arr)

                    STATE = "SORT"
                    auto = False
                    highlight = None

            elif STATE == "SORT":
                if e.key == pygame.K_SPACE:
                    try:
                        working, highlight = next(gen)  # manual step
                    except StopIteration:
                        pass

                if e.key == pygame.K_p:
                    auto = not auto  # toggle autoplay

                if e.key == pygame.K_ESCAPE:
                    STATE = "MENU"
                    gen = None
                    working = arr.copy()
                    highlight = None
                    auto = False

    # autoplay logic
    if STATE == "SORT" and auto and gen:
        try:
            t = target_times[current_algo]
            steps_per_frame = max(1, int((step_count / t) / 60))
            for _ in range(steps_per_frame):
                working, highlight = next(gen)
        except StopIteration:
            auto = False

    # draw screen
    if STATE == "MENU":
        menu()
    else:
        draw(working, highlight)
        font = pygame.font.SysFont(None, 26)
        screen.blit(font.render(
            f"{current_algo} | target: {target_times[current_algo]:.1f}s | auto: {auto}",
            True, (255, 255, 255)
        ), (10, 10))

    pygame.display.flip()

pygame.quit()
