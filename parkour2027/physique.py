###############################################################
###############################################################
## Ressources en ligne:                                      ##
##                                                           ##
## 1) Underactuated Robotics, notamment le chapitre 4 :      ##
## "Simple Models of Walking and Running"                    ##
###############################################################
###############################################################

import pygame
import numpy as np
from scipy.integrate import solve_ivp

###############################################################
###############################################################
##             Resolution equa diff Mouvement                ##
###############################################################
###############################################################

# Parametres
m, mh, a, b, g = 5.0, 10.0, 0.5, 0.5, 9.81
l = a + b


def M_mat(q):
    m_tot = mh + 2 * m
    return np.array([[m_tot, 0.0, -m * b * np.cos(q[2]), -m * b * np.cos(q[3])],
                     [0.0, m_tot, -m * b * np.sin(q[2]), -m * b * np.sin(q[3])],
                     [-m * b * np.cos(q[2]), -m * b * np.sin(q[2]), m * b**2, 0.0],
                     [-m * b * np.cos(q[3]), -m * b * np.sin(q[3]), 0.0, m * b**2]])


def C_mat(q, dq):
    return np.array([[0.0, 0.0, m * b * np.sin(q[2]) * dq[2], m * b * np.sin(q[3]) * dq[3]],
                     [0.0, 0.0, -m * b * np.cos(q[2]) * dq[2], -m * b * np.cos(q[3]) * dq[3]],
                     [0.0, 0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0, 0.0]])


def tau_g(q):
    # le poids seul : pas de pied au sol, pas de couple
    return np.array([0.0,
                     (mh + 2 * m) * g,
                     -m * b * g * np.sin(q[2]),
                     -m * b * g * np.sin(q[3])])


def equa_diff(t, x):
    """
    On a :
    sol = (X, Y, θst, θsw, dX, dY, dθst, dθsw) = (q, dq)
    et on résout l'équation du mouvement
    M(q) * ddq + C(q,dq) * dq = 𝜏g(q)
    """
    q, dq = x[:4], x[4:]
    ddq = np.linalg.solve(M_mat(q), tau_g(q) - C_mat(q, dq) @ dq)

    return np.concatenate([dq, ddq])




# pygame setup
pygame.init()
LARGEUR, HAUTEUR = 800, 600
screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
clock = pygame.time.Clock()
running = True
color = "dark grey"


#circle setup
start_position_circle = pygame.Vector2(LARGEUR/2, HAUTEUR/2)
radius = 5

#Bar constants
bar_mass = m
bar_length_metre= l
meter_into_px = 100
bar_length_px = bar_length_metre * meter_into_px

#first bar setup
start_position_bar1 = pygame.Vector2(LARGEUR/2,HAUTEUR/2)

angle_bar1=np.pi/4
end_position_bar1 = start_position_bar1 + pygame.Vector2(bar_length_px*np.cos(angle_bar1),bar_length_px*np.sin(angle_bar1))
vector_bar1 = end_position_bar1 - start_position_bar1

#second bar setup
start_position_bar2 = start_position_bar1

angle_bar2=np.pi*3/4
end_position_bar2 = start_position_bar2 + pygame.Vector2(bar_length_px*np.cos(angle_bar2),bar_length_px*np.sin(angle_bar2))
vector_bar2 = end_position_bar2 - start_position_bar2

# ground
HAUTEUR_GROUND = HAUTEUR * 3/4

ground = pygame.Rect(0, HAUTEUR_GROUND, LARGEUR, HAUTEUR-HAUTEUR_GROUND)
color_ground = pygame.Color(50,50,50)

#################################
####  equations du mouvement ####
#################################


#Conditions initiales
dX0, dY0 = 0.0, -10.0
dtheta_st0, dtheta_sw0 = 1.0, 0.0

# sol = (X, Y, θst, θsw, dX, dY, dθst, dθsw)   (X, Y = hanche en mètres)
sol0 = np.array([start_position_bar1.x / meter_into_px, start_position_bar1.y / meter_into_px,
              angle_bar1 - np.pi/2, angle_bar2 - np.pi/2,
              dX0, dY0, dtheta_st0, dtheta_sw0])


# Temps de simulation
t_span = (0, 10)  # Intervalle de temps (s)
t_eval = np.linspace(t_span[0], t_span[1], 600)  # On respeccte bien les 60 fps

# Resolution
solution = solve_ivp(equa_diff, t_span, sol0, t_eval=t_eval)
print( f"solution : {len(solution.y)}")
sol = solution.y

xh, yh = sol[0], sol[1]
theta_st, theta_sw = sol[3], sol[4]

frame=0

while running:

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if color == "light grey":
                    color = "dark grey"
                else:
                    color = "light grey"

    screen.fill(color)

    #### On actualise le mouvement ####

    start_position_bar1 = pygame.Vector2(xh[frame], yh[frame])*meter_into_px
    start_position_circle = start_position_bar1
    start_position_bar2 = start_position_bar1

    angle_bar1 = np.pi/2 + theta_st[frame]
    angle_bar2 = np.pi/2 + theta_sw[frame]

    end_position_bar1 = start_position_bar1 + pygame.Vector2(bar_length_px*np.cos(angle_bar1),bar_length_px*np.sin(angle_bar1))
    end_position_bar2 = start_position_bar2 + pygame.Vector2(bar_length_px*np.cos(angle_bar2),bar_length_px*np.sin(angle_bar2))


    pygame.draw.rect(screen, color_ground,ground)

    pygame.draw.circle(screen, "black", start_position_circle, radius)
    #calcul de la position de la barre
   
    pygame.draw.line(screen, "red", start_position_bar1, end_position_bar1, width = 4)
    pygame.draw.line(screen, "blue", start_position_bar2, end_position_bar2, width = 4)

    
    pygame.display.flip()

    frame = frame + 1

    if frame == 200:
        running=False
   
    clock.tick(60)

pygame.quit()