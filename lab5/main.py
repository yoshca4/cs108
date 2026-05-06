from vispy import app, scene
import numpy as np

canvas = scene.SceneCanvas(
    title='Quantum Field Bloom',
    bgcolor="#000000",
    size=(1000, 700),
    show=True
)

view = canvas.central_widget.add_view()
view.camera = scene.TurntableCamera(fov=55, distance=6, elevation=30)

# -------------------------------------------------
# GRID POINT CLOUD (dense 3D field)
# -------------------------------------------------
res = 55
lin = np.linspace(-2, 2, res)

x, y, z = np.meshgrid(lin, lin, lin)
pos0 = np.column_stack([x.ravel(), y.ravel(), z.ravel()]).astype(np.float32)

N = len(pos0)

# -------------------------------------------------
# VISUALS
# -------------------------------------------------
colors = np.zeros((N, 4), dtype=np.float32)

markers = scene.visuals.Markers(
    pos=pos0,
    size=2,
    face_color=colors,
    edge_width=0,
    parent=view.scene
)

markers.set_gl_state('translucent', blend=True, depth_test=False)

# -------------------------------------------------
# TIME STATE
# -------------------------------------------------
t = 0.0

# -------------------------------------------------
# FIELD FUNCTION (this is the "physics")
# -------------------------------------------------
def field(p, t):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]

    r = np.sqrt(x**2 + y**2 + z**2)

    # layered wave interference (key effect)
    f = (
        np.sin(3*x + t) +
        np.cos(3*y - t * 0.8) +
        np.sin(3*z + t * 1.2)
    )

    # radial collapse/expansion wave
    f += np.sin(r * 5 - t * 2)

    # vortex twist
    f += 0.5 * np.sin(x*y + t)

    return f

# -------------------------------------------------
# COLOR MAPPING (energy visualization)
# -------------------------------------------------
def colorize(f):
    f = (f - f.min()) / (f.max() - f.min() + 1e-6)

    c = np.zeros((N, 4), dtype=np.float32)

    c[:, 0] = f**2.2
    c[:, 1] = np.sin(f * 3.14)**2
    c[:, 2] = 1 - f

    c[:, 3] = 0.15 + f * 0.85

    return np.clip(c, 0, 1)

# -------------------------------------------------
# ANIMATION
# -------------------------------------------------
def on_timer(event):
    global t
    t += 0.03

    f = field(pos0, t)

    # deform space itself (this is what makes it “alive”)
    deformation = 0.3 * np.sin(f * 2 + t)

    pos = pos0.copy()
    pos[:, 0] += deformation * np.sin(t + pos[:, 1])
    pos[:, 1] += deformation * np.cos(t + pos[:, 2])
    pos[:, 2] += deformation * np.sin(t + pos[:, 0])

    markers.set_data(
        pos=pos,
        face_color=colorize(f),
        size=2
    )

    # camera slowly drifts through field
    view.camera.azimuth += 0.2
    view.camera.elevation = 30 + 10 * np.sin(t * 0.5)

    canvas.update()

timer = app.Timer(1/60, connect=on_timer, start=True)

if __name__ == '__main__':
    app.run()