from vispy import app, scene
import numpy as np

canvas = scene.SceneCanvas(
    title='Nebula',
    bgcolor='#000008',
    size=(900, 600),
    show=True
)

view = canvas.central_widget.add_view()
view.camera = scene.TurntableCamera(fov=60, distance=8, elevation=15)

N = 4000

pos = (np.random.randn(N, 3) * 0.1).astype(np.float32)
vel = (np.random.randn(N, 3) * 0.03).astype(np.float32)  # faster

# Color by speed
speed = np.linalg.norm(vel, axis=1)
speed_norm = (speed - speed.min()) / (speed.max() - speed.min())

colors = np.zeros((N, 4), dtype=np.float32)
colors[:, 0] = speed_norm
colors[:, 2] = 1 - speed_norm
colors[:, 1] = 0.2
colors[:, 3] = 0.7

markers = scene.visuals.Markers(
    pos=pos,
    size=3,
    face_color=colors,
    edge_width=0,
    parent=view.scene
)

def on_timer(event):
    global pos

    # move particles
    pos += vel

    # gentle swirl (this makes it feel like a nebula)
    theta = 0.01
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    x = pos[:, 0].copy()
    y = pos[:, 1].copy()
    pos[:, 0] = cos_t * x - sin_t * y
    pos[:, 1] = sin_t * x + cos_t * y

    # wrap
    mask = np.abs(pos) > 5
    pos[mask] *= -0.5

    # update GPU
    markers.set_data(pos=pos, face_color=colors, size=3)

timer = app.Timer(1/60, connect=on_timer, start=True)

if __name__ == '__main__':
    app.run()