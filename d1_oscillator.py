"""Day 1: 同一道题，三种数值积分 —— 谁稳、谁准、谁炸。
模型：m ẍ + 2ζωn ẋ + ωn² x = 0，状态 s=[x, v]，ωn = 2π (1 Hz)。
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

WN = 2 * np.pi
T_END = 10.0


def make_f(zeta):
    def f(s):                      # s = [x, v]
        x, v = s
        return np.array([v, -2 * zeta * WN * v - WN**2 * x])
    return f


def euler(s0, dt, n, f):
    s = np.array(s0, float)
    out = np.empty((n + 1, 2)); out[0] = s
    for i in range(n):
        s = s + dt * f(s)          # 只用「当前点」的斜率
        out[i + 1] = s
    return out


def symplectic_euler(s0, dt, n, f):
    """半隐式欧拉：先更新 v，再用【新的】v 更新 x —— 保结构，能量不漂移。"""
    x, v = np.array(s0, float)
    out = np.empty((n + 1, 2)); out[0] = [x, v]
    for i in range(n):
        a = f(np.array([x, v]))[1]
        v = v + dt * a
        x = x + dt * v             # ← 关键：这里用刚更新的 v
        out[i + 1] = [x, v]
    return out


def rk4(s0, dt, n, f):
    s = np.array(s0, float)
    out = np.empty((n + 1, 2)); out[0] = s
    for i in range(n):
        k1 = f(s)
        k2 = f(s + dt / 2 * k1)
        k3 = f(s + dt / 2 * k2)
        k4 = f(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[i + 1] = s
    return out


def exact_damped(zeta, ts):
    """解析解（x0=1, v0=0）：x = e^{-ζωn t}[cos(wd t) + (ζωn/wd) sin(wd t)]"""
    wd = WN * np.sqrt(1 - zeta**2)
    return np.exp(-zeta * WN * ts) * (np.cos(wd * ts) + (zeta * WN / wd) * np.sin(wd * ts))


def run():
    f0 = make_f(0.0)               # 无阻尼：显式欧拉应当「发散」
    f1 = make_f(0.1)               # 轻阻尼：用来测精度与收敛阶
    # --- A. 无阻尼，稳定性对比 ---
    dt = 0.01
    n = int(T_END / dt)
    ts = np.arange(n + 1) * dt                            # 与解数组长度严格对齐
    an = np.cos(WN * ts)                                  # 解析：振幅恒 1
    eu = euler([1, 0], dt, n, f0)
    sy = symplectic_euler([1, 0], dt, n, f0)
    r4 = rk4([1, 0], dt, n, f0)

    amp_eu = np.abs(eu[:, 0]).max()
    amp_sy = np.abs(sy[:, 0]).max()
    amp_r4 = np.abs(r4[:, 0]).max()
    err_r4 = np.abs(r4[:, 0] - an).max()

    # --- B. 有阻尼 (ζ=0.1)，RK4 收敛阶：Δt 减半，误差应缩到 ~1/16 ---
    n1, n2 = int(T_END / 0.04), int(T_END / 0.02)
    t1, t2 = np.arange(n1 + 1) * 0.04, np.arange(n2 + 1) * 0.02   # 各自对齐，别用切片
    e1 = np.abs(rk4([1, 0], 0.04, n1, f1)[:, 0] - exact_damped(0.1, t1)).max()
    e2 = np.abs(rk4([1, 0], 0.02, n2, f1)[:, 0] - exact_damped(0.1, t2)).max()
    ratio = e1 / e2

    # --- 出图 ---
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    ax[0].plot(ts, an, "k", lw=2, label="exact cos(w t)")
    ax[0].plot(ts, eu[:, 0], label="explicit Euler (blows up)")
    ax[0].plot(ts, sy[:, 0], "--", label="symplectic Euler")
    ax[0].set_title("undamped oscillator, dt=0.01"); ax[0].legend(fontsize=8); ax[0].grid(True)
    ax[1].plot(ts, exact_damped(0.1, ts), "k", lw=2, label="exact (zeta=0.1)")
    ax[1].plot(ts, rk4([1, 0], 0.01, 1000, f1)[:, 0], "--", label="RK4")
    ax[1].set_title("damped, zeta=0.1"); ax[1].legend(fontsize=8); ax[1].grid(True)
    fig.tight_layout(); fig.savefig("d1_result.png", dpi=110)

    # --- 自我验证：任何一行 [FAIL] 都说明脚本或环境有问题 ---
    print(f"[1] 显式欧拉 10s 振幅 = {amp_eu:.2f}   (解析=1.00, 预测≈7.1)  "
          f"{'[PASS]' if amp_eu > 3 else '[FAIL] 没发散 → 检查 f()/状态顺序'}")
    print(f"[2] 辛欧拉 10s 振幅   = {amp_sy:.2f}   应≈1.0            "
          f"{'[PASS]' if 0.9 < amp_sy < 1.15 else '[FAIL] 检查是否误用了旧 v'}")
    print(f"[3] RK4 10s 振幅      = {amp_r4:.2f}   应≈1.0            "
          f"{'[PASS]' if 0.99 < amp_r4 < 1.01 else '[FAIL] 检查 k1..k4 系数'}")
    print(f"[4] RK4 vs 解析最大误差 = {err_r4:.2e}  应 <1e-3          "
          f"{'[PASS]' if err_r4 < 1e-3 else '[FAIL] 检查 exact/时间数组是否对齐'}")
    print(f"[5] RK4 收敛阶比值(Δt 0.04→0.02) = {ratio:.1f}  应≈16       "
          f"{'[PASS]' if 8 < ratio < 32 else '[FAIL] 四阶没体现 → 看下面提示'}")
    print(f"图已保存：d1_result.png  ({matplotlib.get_backend()})")
    print("\n今天的数字结论（抄进 progress-tracker.md）：")
    print(f"  欧拉振幅 {amp_eu:.2f} ｜ RK4 误差 {err_r4:.2e} ｜ 收敛阶比 {ratio:.1f}")


if __name__ == "__main__":
    run()
    plt.show()        # 会弹出图形窗口；关掉窗口后脚本才结束