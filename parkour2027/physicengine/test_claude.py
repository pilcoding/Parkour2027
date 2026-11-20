###############################################################
## deux_jambes.py                                            ##
##                                                           ##
## Bonhomme bâton à deux jambes, dynamique de Lagrange       ##
## générée automatiquement avec sympy + collisions avec le   ##
## sol (système hybride : phase de vol / phase d'appui).     ##
##                                                           ##
## Ressource : Underactuated Robotics, chapitre 4            ##
## "Simple Models of Walking and Running"                    ##
##                                                           ##
## Pour ajouter un membre : ajouter un angle dans `q`, une   ##
## ligne dans `corps` et (si c'est un pied) dans `pieds`.    ##
## Tout le reste (M, h, jacobiennes) est recalculé seul.     ##
###############################################################

import numpy as np
import pygame
import sympy as sp
from scipy.integrate import solve_ivp

###############################################################
## 1) PARAMETRES                                             ##
###############################################################

m, mh, a, b, g = 5.0, 10.0, 0.5, 0.5, 9.81   # masse jambe, masse hanche, géométrie, gravité
l = a + b                                     # longueur d'une jambe

LARGEUR, HAUTEUR = 800, 600
METER_INTO_PX = 100
Y_SOL = HAUTEUR * 3 / 4 / METER_INTO_PX      # hauteur du sol en mètres (y vers le bas)

FPS = 60
T_MAX = 10.0                                  # durée simulée (s)
ALPHA = 20.0                                  # stabilisation de la contrainte d'appui
MAX_PHASES = 200                              # garde-fou contre les rebonds infinis

# Conditions initiales : (X, Y, θ1, θ2, dX, dY, dθ1, dθ2)   (X, Y = hanche, en mètres)
# θ = angle de la jambe par rapport à la verticale (θ = 0 : jambe pendante)
Q0 = np.array([4.0, 3.0, -np.pi / 4, np.pi / 4])
DQ0 = np.array([0.0, -5.0, 0.7, 0.0])          # mettre dY0 < 0 pour lancer le bonhomme vers le haut

###############################################################
## 2) MODELE DE LAGRANGE GENERE AVEC SYMPY                   ##
###############################################################

X, Y, th1, th2 = sp.symbols("X Y th1 th2")
dX, dY, dth1, dth2 = sp.symbols("dX dY dth1 dth2")
q_sym = [X, Y, th1, th2]
dq_sym = [dX, dY, dth1, dth2]
q, dq = sp.Matrix(q_sym), sp.Matrix(dq_sym)


def vec_jambe(th, d):
    """Vecteur hanche -> point situé à la distance d sur la jambe d'angle th (y vers le bas)."""
    return sp.Matrix([-d * sp.sin(th), d * sp.cos(th)])


hanche = sp.Matrix([X, Y])

# (masse, position) de chaque corps : SEULE PARTIE A MODIFIER pour changer le bonhomme
corps = [(mh, hanche),
         (m, hanche + vec_jambe(th1, b)),
         (m, hanche + vec_jambe(th2, b))]

# positions des pieds (points qui peuvent toucher le sol)
pieds = [hanche + vec_jambe(th1, l),
         hanche + vec_jambe(th2, l)]

# Energies
T = sum(mi * (p.jacobian(q) * dq).dot(p.jacobian(q) * dq) / 2 for mi, p in corps)
V = sum(-mi * g * p[1] for mi, p in corps)    # y vers le bas -> énergie = -m g y
L = T - V

# Équations d'Euler-Lagrange :  M(q) ddq + h(q, dq) = 0
M_sym = sp.hessian(T, dq_sym)
dL_ddq = sp.Matrix([sp.diff(L, v) for v in dq_sym])
dL_dq = sp.Matrix([sp.diff(L, v) for v in q_sym])
h_sym = dL_ddq.jacobian(q) * dq - dL_dq

# Jacobiennes des pieds et terme J' * dq (nécessaire pour la contrainte d'appui)
J_syms = [p.jacobian(q) for p in pieds]
Jdq_syms = [(J * dq).jacobian(q) * dq for J in J_syms]

args = [q_sym, dq_sym]
M_f = sp.lambdify(args, M_sym, "numpy")
h_f = sp.lambdify(args, h_sym, "numpy")
pos_f = [sp.lambdify([q_sym], p, "numpy") for p in pieds]
J_f = [sp.lambdify([q_sym], J, "numpy") for J in J_syms]
Jdq_f = [sp.lambdify(args, Jd, "numpy") for Jd in Jdq_syms]
N_PIEDS = len(pieds)


def M_num(q_, dq_):
    return np.array(M_f(q_, dq_), dtype=float)


def h_num(q_, dq_):
    return np.array(h_f(q_, dq_), dtype=float).ravel()


def pied_pos(i, q_):
    return np.array(pos_f[i](q_), dtype=float).ravel()


###############################################################
## 3) DYNAMIQUE : VOL / APPUI (un ou deux pieds), IMPACT     ##
###############################################################
# `contacts` = dictionnaire {indice du pied: point d'ancrage au sol}.
# Un pied en contact est "cloué" au sol (pas de glissement).

def _contraintes(q_, dq_, contacts):
    """Empile J, J'dq et l'erreur de position des pieds en contact."""
    idx = sorted(contacts)
    J = np.vstack([np.array(J_f[i](q_), dtype=float) for i in idx])
    Jd = np.concatenate([np.array(Jdq_f[i](q_, dq_), dtype=float).ravel() for i in idx])
    err = np.concatenate([pied_pos(i, q_) - contacts[i] for i in idx])
    return J, Jd, err


def dynamique(q_, dq_, contacts):
    """
    Renvoie (ddq, F).
    - Sans contact : M ddq + h = 0                       (vol, F est vide)
    - Avec contacts : M ddq + h = Jᵀ F  et  J ddq + J'dq = 0   (+ stabilisation)
      F = forces sur les pieds, rangées [Fx, Fy] par pied (ordre des indices).
      Fy < 0 : le sol pousse le pied vers le haut (y vers le bas).
    """
    M = M_num(q_, dq_)
    h = h_num(q_, dq_)
    if not contacts:
        return np.linalg.solve(M, -h), np.zeros(0)
    J, Jd, err = _contraintes(q_, dq_, contacts)
    k = J.shape[0]
    A = np.block([[M, -J.T], [J, np.zeros((k, k))]])
    rhs = np.concatenate([-h, -Jd - 2 * ALPHA * (J @ dq_) - ALPHA**2 * err])
    sol = np.linalg.solve(A, rhs)
    return sol[:4], sol[4:]


def impact(q_, dq_, pieds_idx):
    """Choc inélastique : les pieds de pieds_idx perdent leur vitesse.
       dq+ = dq- - M⁻¹ Jᵀ (J M⁻¹ Jᵀ)⁻¹ J dq-"""
    M = M_num(q_, dq_)
    J = np.vstack([np.array(J_f[i](q_), dtype=float) for i in pieds_idx])
    Minv_Jt = np.linalg.solve(M, J.T)
    lam = np.linalg.solve(J @ Minv_Jt, J @ dq_)
    return dq_ - Minv_Jt @ lam


def relacher_si_besoin(q_, dq_, contacts):
    """Un pied ne peut que pousser le sol : si le sol devait 'tirer' (Fy > 0), on le libère."""
    contacts = dict(contacts)
    while contacts:
        _, F = dynamique(q_, dq_, contacts)
        idx = sorted(contacts)
        fy = F[1::2]
        k = int(np.argmax(fy))
        if fy[k] > 1e-9:
            del contacts[idx[k]]
        else:
            break
    return contacts


###############################################################
## 4) SIMULATION HYBRIDE (événements de solve_ivp)           ##
###############################################################

def event_pied_touche(i):
    """Le pied i (en l'air) atteint le sol en descendant."""
    def ev(t, x):
        return pied_pos(i, x[:4])[1] - Y_SOL
    ev.terminal, ev.direction = True, +1
    return ev


def event_decollage(i, contacts):
    """Le pied i (au sol) devrait être tiré par le sol (Fy >= 0) : il décolle."""
    pos = sorted(contacts).index(i)
    def ev(t, x):
        _, F = dynamique(x[:4], x[4:], contacts)
        return -F[2 * pos + 1]
    ev.terminal, ev.direction = True, -1
    return ev


def event_chute():
    """La hanche touche le sol : le bonhomme est tombé, on arrête la simulation."""
    def ev(t, x):
        return x[1] - Y_SOL
    ev.terminal, ev.direction = True, +1
    return ev


def simuler():
    """Renvoie (temps, états (n,8), masques (n,)) ; bit i du masque = pied i au sol."""
    t_frames = np.arange(0.0, T_MAX, 1.0 / FPS)
    x = np.concatenate([Q0, DQ0])
    t0, contacts = 0.0, {}
    premiere_phase = True
    T_out, X_out, M_out = [], [], []

    for _ in range(MAX_PHASES):
        masque = t_frames >= t0 if premiere_phase else t_frames > t0
        premiere_phase = False
        t_eval = t_frames[masque]
        if len(t_eval) == 0:
            break

        c = dict(contacts)
        def f(t, x, c=c):
            return np.concatenate([x[4:], dynamique(x[:4], x[4:], c)[0]])

        noms = [("touche", i) for i in range(N_PIEDS) if i not in c] + \
               [("decolle", i) for i in sorted(c)] + [("chute", None)]
        events = [event_pied_touche(i) if nom == "touche" else
                  event_decollage(i, c) if nom == "decolle" else event_chute()
                  for nom, i in noms]

        sol = solve_ivp(f, (t0, T_MAX), x, t_eval=t_eval, events=events,
                        rtol=1e-8, atol=1e-10, max_step=1.0 / FPS)

        if len(sol.t) > 0:           # (aucune image si l'événement est immédiat)
            bits = sum(1 << i for i in c)
            T_out.append(sol.t)
            X_out.append(np.asarray(sol.y).T)
            M_out.append(np.full(len(sol.t), bits))

        if sol.status != 1:          # pas d'événement : on a atteint T_MAX
            break

        k = next(k for k, te in enumerate(sol.t_events) if len(te) > 0)
        nom, i = noms[k]
        t0 = sol.t_events[k][0]
        x = sol.y_events[k][0].copy()
        q_, dq_ = x[:4], x[4:]

        if nom == "chute":
            print(f"Le bonhomme est tombé à t = {t0:.2f} s")
            break
        elif nom == "decolle":
            del contacts[i]
        else:                        # nom == "touche" : impact sur tous les pieds au sol + le nouveau
            x[4:] = impact(q_, dq_, sorted(contacts) + [i])
            contacts[i] = np.array([pied_pos(i, q_)[0], Y_SOL])
            contacts = relacher_si_besoin(x[:4], x[4:], contacts)

    return np.concatenate(T_out), np.vstack(X_out), np.concatenate(M_out)


###############################################################
## 5) AFFICHAGE PYGAME                                       ##
###############################################################

def main():
    print("Intégration en cours...")
    temps, etats, modes = simuler()
    print(f"{len(temps)} images simulées ({temps[-1]:.2f} s)")

    pygame.init()
    screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Bonhomme bâton à deux jambes")
    clock = pygame.time.Clock()

    color = "dark grey"
    color_ground = pygame.Color(50, 50, 50)
    y_sol_px = Y_SOL * METER_INTO_PX
    ground = pygame.Rect(0, y_sol_px, LARGEUR, HAUTEUR - y_sol_px)
    couleurs_jambes = ["red", "blue"]
    bar_length_px = l * METER_INTO_PX

    frame, running = 0, True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                color = "dark grey" if color == "light grey" else "light grey"

        screen.fill(color)
        pygame.draw.rect(screen, color_ground, ground)

        X_, Y_, th_1, th_2 = etats[frame][:4]
        hip = pygame.Vector2(X_, Y_) * METER_INTO_PX

        for i, th in enumerate((th_1, th_2)):
            angle = np.pi / 2 + th
            fin = hip + pygame.Vector2(bar_length_px * np.cos(angle), bar_length_px * np.sin(angle))
            pygame.draw.line(screen, couleurs_jambes[i], hip, fin, width=4)
            if (modes[frame] >> i) & 1:    # pied en contact avec le sol
                pygame.draw.circle(screen, "green", fin, 6)

        pygame.draw.circle(screen, "black", hip, 8)

        pygame.display.flip()
        clock.tick(FPS)

        frame += 1
        if frame >= len(temps):      # on rejoue la simulation en boucle
            frame = 0

    pygame.quit()


if __name__ == "__main__":
    main()