"""Layanan bubble mengambang (Android, via pyjnius). Ketuk 'AI' untuk membuka panel tips cepat offline."""
import time

from jnius import PythonJavaClass, autoclass, java_method

import knowledge

PythonService = autoclass("org.kivy.android.PythonService")
ctx = PythonService.mService
Context = autoclass("android.content.Context")
Build = autoclass("android.os.Build$VERSION")
LP = autoclass("android.view.WindowManager$LayoutParams")
LLP = autoclass("android.widget.LinearLayout$LayoutParams")
LinearLayout, TextView, Button = (autoclass("android.widget.LinearLayout"), autoclass("android.widget.TextView"),
                                  autoclass("android.widget.Button"))
GradientDrawable, Color = autoclass("android.graphics.drawable.GradientDrawable"), autoclass("android.graphics.Color")
JString = autoclass("java.lang.String")
Handler, Looper = autoclass("android.os.Handler"), autoclass("android.os.Looper")

_keep = []  # cegah listener di-garbage-collect


class Run(PythonJavaClass):
    __javainterfaces__ = ["java/lang/Runnable"]
    __javacontext__ = "app"

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    @java_method("()V")
    def run(self):
        self.fn()


class Click(PythonJavaClass):
    __javainterfaces__ = ["android/view/View$OnClickListener"]
    __javacontext__ = "app"

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    @java_method("(Landroid/view/View;)V")
    def onClick(self, v):
        self.fn()


def build():
    d = ctx.getResources().getDisplayMetrics().density
    dp = lambda v: int(v * d)
    wm = ctx.getSystemService(Context.WINDOW_SERVICE)
    ltype = LP.TYPE_APPLICATION_OVERLAY if Build.SDK_INT >= 26 else LP.TYPE_PHONE
    params = LP(LP.WRAP_CONTENT, LP.WRAP_CONTENT, ltype, LP.FLAG_NOT_FOCUSABLE, -3)  # -3 = TRANSLUCENT
    params.gravity = 48 | 8388611  # TOP | START
    params.x, params.y = dp(8), dp(160)

    def shape(color, oval, radius=0):
        g = GradientDrawable()
        g.setShape(1 if oval else 0)
        g.setColor(Color.parseColor(color))
        if radius:
            g.setCornerRadius(float(dp(radius)))
        return g

    root = LinearLayout(ctx)
    root.setOrientation(1)

    bubble = TextView(ctx)
    bubble.setText(JString("AI"))
    bubble.setGravity(17)
    bubble.setTextColor(Color.parseColor("#FFFFFF"))
    bubble.setTextSize(16.0)
    bubble.setBackground(shape("#6C5CE7", True))
    bubble.setLayoutParams(LLP(dp(56), dp(56)))

    panel = LinearLayout(ctx)
    panel.setOrientation(1)
    panel.setPadding(dp(12), dp(10), dp(12), dp(10))
    panel.setBackground(shape("#2D2D3A", False, 14))
    panel.setVisibility(8)  # GONE
    tip = TextView(ctx)
    tip.setTextColor(Color.parseColor("#FFFFFF"))
    tip.setMaxWidth(dp(250))
    panel.addView(tip)
    state = {"i": 0}

    def next_tip():
        tip.setText(JString(knowledge.tip(state["i"])))
        state["i"] += 1

    def launch_app():
        it = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName())
        it.addFlags(0x10000000)  # FLAG_ACTIVITY_NEW_TASK
        ctx.startActivity(it)

    def close_all():
        wm.removeView(root)
        ctx.stopSelf()

    for label, fn in (("Tip lain", next_tip), ("Buka asisten", launch_app), ("Tutup bubble", close_all)):
        b = Button(ctx)
        b.setText(JString(label))
        c = Click(fn)
        _keep.append(c)
        b.setOnClickListener(c)
        panel.addView(b)

    root.addView(bubble)
    root.addView(panel)
    next_tip()

    class Drag(PythonJavaClass):
        __javainterfaces__ = ["android/view/View$OnTouchListener"]
        __javacontext__ = "app"
        px = py = sx = sy = 0
        moved = False

        @java_method("(Landroid/view/View;Landroid/view/MotionEvent;)Z")
        def onTouch(self, v, e):
            a = e.getActionMasked()
            if a == 0:
                self.px, self.py, self.sx, self.sy, self.moved = params.x, params.y, e.getRawX(), e.getRawY(), False
            elif a == 2:
                dx, dy = e.getRawX() - self.sx, e.getRawY() - self.sy
                if abs(dx) + abs(dy) > dp(8):
                    self.moved = True
                if self.moved:
                    params.x, params.y = int(self.px + dx), int(self.py + dy)
                    wm.updateViewLayout(root, params)
            elif a == 1 and not self.moved:
                panel.setVisibility(0 if panel.getVisibility() == 8 else 8)
            return True

    drag = Drag()
    _keep.append(drag)
    bubble.setOnTouchListener(drag)
    wm.addView(root, params)


# Operasi View wajib di main thread Android.
_runner = Run(build)
_keep.append(_runner)
Handler(Looper.getMainLooper()).post(_runner)

while True:  # jaga proses layanan tetap hidup
    time.sleep(3600)
