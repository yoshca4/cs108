import numpy as np
import matplotlib.pyplot as plt

np.random.seed(None)

# TRY CHANGING THESE!
NUM_ARMS = 6
STARS_PER_ARM = 2000
NOISE = 0.15
SPREAD = 0.12

fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
ax.set_facecolor('black')
ax.axis('off')

for arm in range(NUM_ARMS):
    offset = (2 * np.pi / NUM_ARMS) * arm

    theta = np.linspace(0.3, 4.5 * np.pi, STARS_PER_ARM)

    # Base spiral
    r = 0.12 * np.exp(0.25 * theta)

    # --- (4) Clumping ---
    clump_factor = np.random.normal(1, 0.25, STARS_PER_ARM)
    clump_factor = np.clip(clump_factor, 0.1, None)  # prevent negatives
    r *= clump_factor
    
    # --- (3) Arm distortion ---
    theta_distort = theta + 0.25 * np.sin(3 * theta + arm)

    # Spread + noise
    r += np.random.normal(0, SPREAD * r, STARS_PER_ARM)

    x = r * np.cos(theta_distort + offset)
    y = r * np.sin(theta_distort + offset)

    x += np.random.normal(0, NOISE * 0.1, STARS_PER_ARM)
    y += np.random.normal(0, NOISE * 0.1, STARS_PER_ARM)

    # --- (5) Dust lanes ---
    dust_mask = np.sin(theta * 2 + arm) > 0.85
    x = x[~dust_mask]
    y = y[~dust_mask]

    # Distance + brightness
    dist = np.sqrt(x**2 + y**2)
    brightness = np.clip(1 - dist / dist.max(), 0.05, 1)

    # --- (1) Color diversity ---
    star_types = np.random.choice(
        ['blue', 'white', 'yellow'],
        size=len(x),
        p=[0.2, 0.6, 0.2]
    )

    colors = []
    for i in range(len(x)):
        if star_types[i] == 'blue':
            colors.append((0.6, 0.8, 1.0, brightness[i]))
        elif star_types[i] == 'white':
            colors.append((1.0, 1.0, 1.0, brightness[i]))
        else:
            colors.append((1.0, 0.85, 0.6, brightness[i]))

    # --- (2) Size variation ---
    sizes = np.random.exponential(scale=0.6, size=len(x))
    sizes = np.clip(sizes, 0.1, 3.0)

    # --- (7) Glow effect ---
    ax.scatter(x, y, c=colors, s=sizes * 3, alpha=0.05, linewidths=0)
    ax.scatter(x, y, c=colors, s=sizes, alpha=0.85, linewidths=0)

# --- (8) Improved glowing core ---
for i in range(25):
    core = plt.Circle(
        (0, 0),
        0.02 * i,
        color=(1.0, 0.9, 0.7),
        alpha=0.025
    )
    ax.add_patch(core)

# --- (6) Bright hero stars ---
num_bright = 60
bx = np.random.uniform(-1.8, 1.8, num_bright)
by = np.random.uniform(-1.8, 1.8, num_bright)

ax.scatter(bx, by, c='white', s=12, alpha=0.9, linewidths=0)

# Background stars (slightly varied)
bg_x = np.random.uniform(-2, 2, 2000)
bg_y = np.random.uniform(-2, 2, 2000)
bg_sizes = np.random.uniform(0.05, 0.5, 2000)

ax.scatter(bg_x, bg_y, c='white', s=bg_sizes, alpha=0.25, linewidths=0)

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

plt.tight_layout()
plt.savefig('galaxy_enhanced.png', dpi=200, bbox_inches='tight', facecolor='black')
plt.show()
