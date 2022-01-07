import pygame as pg
import sys, random, math


EPSILON = sys.float_info.epsilon
SCREENRECT = pg.Rect(0, 0, 640, 360)


class Hit(object):

    def __init__(self):
        self.pos = pg.math.Vector2()
        self.delta = pg.math.Vector2()
        self.normal = pg.math.Vector2()
        self.time = 1


class Sweep(object):

    def __init__(self):
        self.hit = None
        self.pos = pg.math.Vector2()
        self.time = 1


def clamp(n, lower, upper):
    return min(max(n, lower), upper)


def sign(n):
    return -1 if n < 0 else 1


def randomOnscreenVector2(w=0, h=0):
    return pg.math.Vector2(random.randint(0 + w/2, SCREENRECT.width - w/2),
                           random.randint(0 + h/2, SCREENRECT.height- h/2))


def segmentCollision(pos, delta, rectangle, paddingX=0, paddingY=0):
    scaleX = 1.0 / delta.x if delta.x != 0 else 1
    scaleY = 1.0 / delta.y if delta.y != 0 else 1
    signX = sign(scaleX)
    signY = sign(scaleY)
    rPositionX, rPositionY = rectangle.center
    rWidth, rHeight = rectangle.size
    nearTimeX = (rPositionX - signX*(rWidth/2 + paddingX) - pos.x) * scaleX
    nearTimeY = (rPositionY - signY*(rHeight/2 + paddingY) - pos.y) * scaleY
    farTimeX = (rPositionX + signX*(rWidth/2 + paddingX) - pos.x) * scaleX
    farTimeY = (rPositionY + signY*(rHeight/2 + paddingY) - pos.y) * scaleY

    if nearTimeX > farTimeY or nearTimeY > farTimeX:
        return False

    nearTime = nearTimeX if nearTimeX > nearTimeY else nearTimeY
    farTime = farTimeX if farTimeX < farTimeY else farTimeY

    if nearTime >= 1 or farTime <= 0:
        return False

    hit = Hit()
    hit.time = clamp(nearTime, 0, 1)

    if nearTimeX > nearTimeY:
        hit.normal.x = -signX
        hit.normal.y = 0
    else:
        hit.normal.x = 0
        hit.normal.y = -signY

    hit.delta.x = (1.0-hit.time) * -delta.x
    hit.delta.y = (1.0-hit.time) * -delta.y
    hit.pos.x = pos.x + delta.x*hit.time
    hit.pos.y = pos.y + delta.y*hit.time

    return hit


def sweepCollision(rect1, rect2, delta):

    sweep = Sweep()

    r1Position = pg.math.Vector2(rect1.center)
    r1Width, r1Height = rect1.size
    r2Position = pg.math.Vector2(rect2.center)
    r2Width, r2Height = rect2.size

    if delta.length() == 0:
        if rect2.colliderect(rect1):
            sweep.hit = Hit()
            sweep.hit.pos = r1Position
            sweep.pos = r1Position.x - r1Width
            sweep.time = sweep.hit.time
            return sweep

    sweep.hit = segmentCollision(r1Position, delta, rect2, r1Width / 2,
                                 r1Height / 2)

    if sweep.hit:
        sweep.time = clamp(sweep.hit.time, 0, 1)
        sweep.pos.x = math.ceil(r1Position.x + delta.x*sweep.time)
        sweep.pos.y = math.ceil(r1Position.y + delta.y*sweep.time)
        direction = delta.normalize()
        sweep.hit.pos.x = clamp(sweep.hit.pos.x + direction.x*(r1Width/2),
                                r2Position.x - r2Width/2,
                                r2Position.x + r2Width/2)
        sweep.hit.pos.y = clamp(sweep.hit.pos.y + direction.y*(r1Height/2),
                                r2Position.y - r2Height/2,
                                r2Position.y + r2Height/2)
    else:
        sweep.pos.x = r1Position.x + delta.x
        sweep.pos.y = r2Position.y + delta.y

    return sweep


def sweepGroup(rect1, delta, rectGroup):
    nearest = Sweep()
    nearest.time = 1
    nearest.pos.x = rect1.centerx + delta.x
    nearest.pos.y = rect1.centery + delta.y
    for r in rectGroup:
        sweep = sweepCollision(rect1, r, delta)
        if sweep.time < nearest.time and sweep.hit:
            nearest = sweep
    return nearest


def main():

    # Initialise PyGame, display and clock. Set initial value for DeltaTime
    pg.init()
    screen = pg.display.set_mode(SCREENRECT.size)
    pg.display.set_caption('Sweep Collision Test')
    clock = pg.time.Clock()
    dt = 0

    # Initialise background surface
    background = pg.Surface(SCREENRECT.size)
    background = background.convert()
    background.fill((80, 80, 80))

    # Rect object representing the "player"
    player = pg.Rect(100, 100, 30, 30)

    # Construct list of Rect obejects representing the colliders ensuring no
    # overlapping rects.
    colliderRectCount = 8

    colliderRects = []

    while len(colliderRects) < colliderRectCount:
        rTemp = pg.Rect(randomOnscreenVector2(30, 30), (30, 30))
        if rTemp.collidelist(colliderRects) == -1 \
        and not rTemp.colliderect(player):
            colliderRects.append(rTemp)

    # Start loop
    running = True
    while running:

        events = pg.event.get()
        screen.blit(background, (0, 0))

        # Get mouse position
        mPos = pg.mouse.get_pos()

        # Set player movement delta
        playerDelta = mPos - pg.math.Vector2(player.center)

        pg.draw.rect(screen, (255, 40, 40), player, 1)
        pg.draw.line(screen, (40, 40, 255), pg.math.Vector2(player.center),
                     pg.math.Vector2(player.center) + playerDelta)

        for r in colliderRects:
            pg.draw.rect(screen, (40, 255, 40), r, 1)

        sweep = sweepGroup(player, playerDelta, colliderRects)

        pg.draw.circle(screen, (255, 255, 40), sweep.pos, 3)
        if sweep.hit:
            pg.draw.circle(screen, (40, 255, 255), sweep.hit.pos, 3)

        for event in events:
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    player.center = sweep.pos

        pg.display.flip()
        dt = clock.tick(60)

if __name__ == '__main__':
    main()
    pg.quit()
