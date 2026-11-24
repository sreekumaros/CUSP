#!/usr/bin/env python3
"""
CUSP: Conformal near-vehicle kinematics for Uncertainty-aware SPeed decision.

Single-file reference implementation (NumPy only).

  Part A  core modules (usable with any detector/tracker)
          - LogRangeFilter : log-domain Kalman filter fusing ground-contact row
                             and box width  ->  range, inverse time-to-contact
          - LateralFilter  : constant-velocity filter on lateral offset
          - Conformal      : split-conformal quantiles + adaptive conformal
                             inference (ACI) driven by filter innovations
          - SpeedDecision  : cut-in probability, closed-form safe speed,
                             jerk-limited governor with emergency override
  Part B  dense-traffic simulator with a pinhole-camera measurement model
  Part C  experiment runner (baselines, ablations, latency benchmark)

Usage
  python cusp.py --episodes 200 --out results.json     # full experiment (about 16 min on 2 cores)
  python cusp.py --episodes 200 --seed0 500000         # same, on fresh test seeds
  python cusp.py --quick                               # smoke test
  python cusp.py --quick --save-cal cal.npz            # also export calibration scores
"""
from __future__ import annotations
import argparse, json, math, time
from dataclasses import dataclass, field
from multiprocessing import Pool
import numpy as np

SQRT2 = math.sqrt(2.0)


def phi(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / SQRT2))


# ----------------------------------------------------------------------------
# Part A.  Core modules
# ----------------------------------------------------------------------------
@dataclass
class Camera:
    f: float = 1000.0      # focal length [px]
    h: float = 1.30        # camera height above road [m]
    W_prior: float = 1.75  # class width prior [m] (initialisation only)


@dataclass
class FilterCfg:
    sigma_y: float = 1.5       # bottom-edge row noise [px]
    sigma_pitch: float = 2.0   # residual pitch/horizon noise [px]
    sigma_w: float = 2.0       # box-width noise [px]
    sigma_u: float = 2.0       # box-centre column noise [px]
    sigma_al: float = 2.5      # unknown lead acceleration [m/s^2]
    sigma_ay: float = 1.5      # unknown lateral acceleration [m/s^2]
    occ_inflate: float = 3.0   # std inflation for occluded bottom edge
    gate: float = 5.0          # innovation gate [sigma]
    z_blind: float = 1.5       # below this range a vehicle may be under the image edge [m]
    use_width: bool = True


class LogRangeFilter:
    """State x = [s, sdot, c];  s = ln Z,  sdot = Zdot/Z = -1/tau,
    c = ln(f W) (unknown physical width, estimated online).

    Measurements
        m1 = ln(f h / dy)  = s + e1,      var(e1) ~ (sigma_dy / dy)^2
        m2 = ln(w_px)      = c - s + e2,  var(e2) ~ (sigma_w / w_px)^2
    m2 is immune to pitch error; m1 anchors metric scale.
    """
    __slots__ = ("x", "P", "age", "cam", "cfg", "last_nu", "n_gated", "coast", "occ")

    def __init__(self, m1: float, m2: float, r1: float, cam: Camera, cfg: FilterCfg):
        self.cam, self.cfg = cam, cfg
        self.x = np.array([m1, 0.0, m1 + m2])
        self.P = np.diag([4.0 * r1, 0.3 ** 2, 4.0 * r1 + 0.02])
        self.P[0, 2] = self.P[2, 0] = 4.0 * r1
        self.age = 0
        self.last_nu = 0.0
        self.n_gated = 0     # consecutive gated measurements (lock-out detector)
        self.coast = 0       # consecutive frames without a detection
        self.occ = False

    def predict(self, dt: float, a_ego: float):
        s, sd, c = self.x
        Z = math.exp(s)
        # d/dt sdot = (a_lead - a_ego)/Z - sdot^2 ; a_lead ~ N(0, sigma_al^2)
        # floor at 0.2 m: a coasting near-field track must not run through zero range
        sd_new = min(8.0, max(-8.0, sd + (-a_ego / Z - sd * sd) * dt))
        self.x = np.array([max(s + sd * dt, math.log(0.2)), sd_new, c])
        F = np.array([[1.0, dt, 0.0],
                      [a_ego * dt / Z, 1.0 - 2.0 * sd * dt, 0.0],
                      [0.0, 0.0, 1.0]])
        qv = (self.cfg.sigma_al * dt / Z) ** 2
        Q = np.diag([0.25 * qv * dt * dt, qv, 1e-7])
        P = F @ self.P @ F.T + Q
        self.P = 0.5 * (P + P.T)
        self.age += 1

    def _scalar_update(self, H: np.ndarray, z: float, R: float) -> float:
        S = float(H @ self.P @ H) + R
        if not (S > 0.0 and math.isfinite(S)):           # numerical safeguard
            self.P = np.diag([4.0 * R, 0.3 ** 2, 4.0 * R + 0.02]); S = 5.0 * R
        nu = (z - float(H @ self.x)) / math.sqrt(S)
        if abs(nu) <= self.cfg.gate:
            K = (self.P @ H) / S
            self.x = self.x + K * (z - float(H @ self.x))
            A = np.eye(3) - np.outer(K, H)               # Joseph form keeps P symmetric PSD
            self.P = A @ self.P @ A.T + R * np.outer(K, K)
        return nu

    def update(self, dy, w_px: float, occluded: bool):
        """dy: bottom-edge row minus horizon row [px], or None when the bottom
        edge is cut off by the image border (width-only update).
        Returns the normalised m1 innovation, or None for a width-only update."""
        cfg = self.cfg
        if dy is None:
            self.coast = 0
            if cfg.use_width and not occluded and w_px > 4.0:
                self._scalar_update(np.array([-1.0, 0.0, 1.0]), math.log(w_px), (cfg.sigma_w / w_px) ** 2)
            return None
        dy = max(dy, 2.0)
        sd_y = math.hypot(cfg.sigma_y, cfg.sigma_pitch) * (cfg.occ_inflate if occluded else 1.0)
        m1 = math.log(self.cam.f * self.cam.h / dy)
        nu = self._scalar_update(np.array([1.0, 0.0, 0.0]), m1, (sd_y / dy) ** 2)
        self.n_gated = self.n_gated + 1 if abs(nu) > cfg.gate else 0
        self.coast, self.occ = 0, occluded
        if cfg.use_width and not occluded and w_px > 4.0:
            self._scalar_update(np.array([-1.0, 0.0, 1.0]), math.log(w_px), (cfg.sigma_w / w_px) ** 2)
        self.last_nu = nu
        return nu

    # convenient accessors
    @property
    def Z(self): return math.exp(self.x[0])
    @property
    def sig_s(self):
        """Std of ln Z: filter variance plus a systematic floor (pitch/occlusion
        bias is common-mode over time and is not averaged out by the filter)."""
        dy = self.cam.f * self.cam.h / self.Z
        b = self.cfg.sigma_pitch * (self.cfg.occ_inflate if self.occ else 1.0) / dy
        return math.sqrt(max(self.P[0, 0], 1e-12) + b * b)
    @property
    def sig_sd(self): return math.sqrt(max(self.P[1, 1], 1e-12))


class LateralFilter:
    """x = [X, Xdot] with measurement X = Z * (u - u0) / f."""
    __slots__ = ("x", "P", "cfg")

    def __init__(self, X0: float, r: float, cfg: FilterCfg):
        self.cfg = cfg
        self.x = np.array([X0, 0.0])
        self.P = np.diag([4.0 * r, 1.0])

    def predict(self, dt: float):
        F = np.array([[1.0, dt], [0.0, 1.0]])
        q = self.cfg.sigma_ay ** 2
        Q = q * np.array([[dt ** 4 / 4, dt ** 3 / 2], [dt ** 3 / 2, dt ** 2]])
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, Xm: float, r: float):
        S = self.P[0, 0] + r
        K = self.P[:, 0] / S
        self.x = self.x + K * (Xm - self.x[0])
        self.P = self.P - np.outer(K, self.P[0, :])

    def p_in_corridor(self, half_w: float, horizons=(0.0, 0.5, 1.0, 1.5)) -> float:
        """max over horizons of P(|X(T)| < half_w) under the Gaussian CV prediction."""
        best = 0.0
        X, V = self.x
        for T in horizons:
            mu = X + V * T
            var = self.P[0, 0] + 2 * T * self.P[0, 1] + T * T * self.P[1, 1]
            sd = math.sqrt(max(var, 1e-9))
            p = phi((half_w - mu) / sd) - phi((-half_w - mu) / sd)
            best = max(best, p)
        return best


class Conformal:
    """Split-conformal quantiles for the state bounds, with the miscoverage
    level adapted online by ACI on (label-free) innovation scores.

    cal_s   : one-sided scores (s_hat - s_true)/sigma_s     (range over-estimate)
    cal_sd  : one-sided scores (sd_hat - sd_true)/sigma_sd  (closing under-estimate)
    cal_nu  : |normalised m1 innovation|
    """

    def __init__(self, cal_s, cal_sd, cal_nu, alpha=0.05, gamma=0.005,
                 adaptive=True, a_min=0.005, a_max=None):
        self.cs, self.cv, self.cn = (np.sort(np.asarray(a, float)) for a in (cal_s, cal_sd, cal_nu))
        self.alpha, self.gamma, self.adaptive = alpha, gamma, adaptive
        # One-sided adaptation: alpha_t may fall below alpha (wider bounds when the
        # sensor degrades) but never rise above it, so the bounds are never
        # tighter than the offline calibration. a_max > alpha gives two-sided ACI.
        self.a_min, self.a_max = a_min, (alpha if a_max is None else a_max)
        self.alpha_t = alpha
        self._refresh()

    @staticmethod
    def _q(sorted_scores: np.ndarray, level: float) -> float:
        n = len(sorted_scores)
        k = min(n - 1, max(0, math.ceil((n + 1) * level) - 1))
        return float(sorted_scores[k])

    def _refresh(self):
        a = self.alpha_t
        self.q_s = max(0.0, self._q(self.cs, 1 - a / 2))    # Bonferroni split
        self.q_sd = max(0.0, self._q(self.cv, 1 - a / 2))
        self.q_nu = self._q(self.cn, 1 - a)

    def step(self, abs_nus):
        """ACI update, one per frame, pooled over all tracks (Gibbs & Candes 2021)."""
        if not self.adaptive or len(abs_nus) == 0:
            return
        err = float(np.mean([1.0 if v > self.q_nu else 0.0 for v in abs_nus]))
        self.alpha_t = min(self.a_max, max(self.a_min, self.alpha_t + self.gamma * (self.alpha - err)))
        self._refresh()


@dataclass
class DecisionCfg:
    v_des: float = 12.0     # free-flow target [m/s]
    b_ego: float = 5.0      # braking assumed available to ego in safe-speed law [m/s^2]
    b_lead: float = 8.0     # worst-case lead braking [m/s^2]
    b_max: float = 8.0      # emergency braking [m/s^2]
    a_max: float = 2.0
    rho: float = 0.30       # response time (perception + actuation) [s]
    d0: float = 2.0         # standstill margin [m]
    half_w: float = 1.8     # conflict corridor half width [m]
    T_g: float = 0.6        # governor time constant [s]
    j_max: float = 12.0     # comfort jerk limit [m/s^3]
    rho_act: float = 0.10   # actuation delay used in the emergency test [s]
    p_min: float = 0.05
    anticipate: bool = True


@dataclass
class TrackView:
    """What the decision layer needs from one track."""
    Z_hat: float; Z_lo: float; sd_lo: float; p_conf: float


def safe_speed(d_lo: float, v_lead_lo: float, c: DecisionCfg) -> float:
    """Largest ego speed v such that  v*rho + v^2/(2 b_e) <= d_lo + v_l^2/(2 b_l)."""
    d = max(d_lo, 0.0)
    disc = (c.b_ego * c.rho) ** 2 + 2 * c.b_ego * d + (c.b_ego / c.b_lead) * v_lead_lo ** 2
    return max(0.0, -c.b_ego * c.rho + math.sqrt(disc))


class SpeedDecision:
    def __init__(self, cfg: DecisionCfg):
        self.c = cfg
        self.a_prev = 0.0

    def decide(self, v_ego: float, tracks: list[TrackView], dt: float):
        c = self.c
        v_cap, emergency = c.v_des, False
        for t in tracks:
            p = t.p_conf if c.anticipate else (1.0 if t.p_conf >= 0.5 else 0.0)
            if p < c.p_min:
                continue
            v_lead_lo = max(0.0, v_ego + t.sd_lo * t.Z_hat)
            v_i = safe_speed(t.Z_lo - c.d0, v_lead_lo, c)
            v_cap = min(v_cap, p * v_i + (1 - p) * c.v_des)
            # emergency: deceleration required on the conservative bounds exceeds
            # what the jerk-limited governor is allowed to command (0.8 b_max)
            d_av = max(t.Z_lo - 0.5 * c.d0 - v_ego * c.rho_act, 0.05)
            a_req = max(0.0, v_ego ** 2 - v_lead_lo ** 2) / (2.0 * d_av)
            if p >= 0.5 and a_req > 0.8 * c.b_max:
                emergency = True
        if emergency:
            a = -c.b_max
        else:
            a_ref = min(c.a_max, max(-0.8 * c.b_max, (v_cap - v_ego) / c.T_g))
            a = min(self.a_prev + c.j_max * dt, max(self.a_prev - c.j_max * dt, a_ref))
        self.a_prev = a
        return a, v_cap, emergency


# ----------------------------------------------------------------------------
# Part B.  Dense-traffic simulator with camera measurement model
# ----------------------------------------------------------------------------
DENSITY = {  # cut-in rate [1/s], lead target speeds [m/s], hard-brake rate [1/s]
    "low":    dict(lam_cut=2 / 60, v_set=(8.0, 12.0), lam_brake=1 / 60),
    "medium": dict(lam_cut=5 / 60, v_set=(4.0, 10.0), lam_brake=1 / 40),
    "high":   dict(lam_cut=9 / 60, v_set=(0.5, 7.0),  lam_brake=1 / 25),
}
NOISE = {  # true sensor noise; "shift" is unseen at calibration time
    "nominal": dict(sy=1.5, sw=2.0, su=2.0, p_out=0.02, p_miss=0.03, k_pitch=0.001, s_road=1.5),
    "shift":   dict(sy=3.0, sw=4.0, su=3.0, p_out=0.06, p_miss=0.08, k_pitch=0.002, s_road=3.0),
}
VEH_LEN, DT = 4.5, 0.05


@dataclass
class Veh:
    vid: int; pos: float; v: float; X: float; W: float
    mode: str = "lane"          # lane | adj | cutin | feint
    t0: float = 0.0; T: float = 2.0; X0: float = 0.0; X1: float = 0.0
    v_tgt: float = 8.0; t_switch: float = 0.0; brake_until: float = -1.0; brake_a: float = 0.0
    occ_bias: float = 0.0


def idm_acc(v, v0, gap, dv, a=1.5, b=2.5, s0=2.0, T=1.0):
    s_star = s0 + max(0.0, v * T + v * dv / (2 * math.sqrt(a * b)))
    return a * (1 - (v / max(v0, 0.1)) ** 4 - (s_star / max(gap, 0.1)) ** 2)


class World:
    def __init__(self, seed: int, density: str, noise: str, T_end=40.0):
        self.rng = np.random.default_rng(seed)
        self.D, self.N = DENSITY[density], NOISE[noise]
        self.T_end, self.t = T_end, 0.0
        self.se, self.ve, self.ae = 0.0, 6.0, 0.0
        self.nid = 0
        self.vehs: list[Veh] = [self._new(15.0, 6.0, 0.0), self._new(32.0, 6.0, 0.0)]
        self.road_pitch = 0.0
        self.collided = False

    def _new(self, gap, v, X, mode="lane"):
        self.nid += 1
        r = self.rng
        return Veh(self.nid, self.se + gap, v, X, W=float(r.uniform(1.55, 2.0)), mode=mode,
                   v_tgt=float(r.uniform(*self.D["v_set"])), t_switch=self.t + float(r.uniform(3, 8)),
                   occ_bias=float(r.uniform(2, 8)))

    def _pred(self, me: Veh):
        """Nearest vehicle ahead of `me` in the ego lane."""
        best = None
        for o in self.vehs:
            if o is not me and abs(o.X) < 1.2 and o.pos > me.pos and (best is None or o.pos < best.pos):
                best = o
        return best

    def step(self, a_cmd: float):
        r, D, dt = self.rng, self.D, DT
        # ego: first-order actuator lag, no reversing
        self.ae += (a_cmd - self.ae) * dt / 0.10
        self.ve = max(0.0, self.ve + self.ae * dt)
        self.se += self.ve * dt
        # spawn adjacent vehicles
        if r.random() < D["lam_cut"] * dt:
            side = 1.0 if r.random() < 0.5 else -1.0
            g = float(r.uniform(max(5.0, 0.6 * self.ve), 16.0))
            v = max(0.0, self.ve + float(r.uniform(-2.0, 1.0)))
            nv = self._new(g, v, side * 3.3, mode="adj")
            nv.t0 = self.t + float(r.uniform(0.3, 1.5))
            nv.T = float(r.uniform(1.2, 3.0))
            if r.random() < 0.6:
                nv.mode, nv.X0, nv.X1 = "cutin", nv.X, float(r.uniform(-0.3, 0.3))
            else:
                nv.mode, nv.X0, nv.X1 = "feint", nv.X, side * float(r.uniform(1.9, 2.5))
            self.vehs.append(nv)
        # other vehicles
        for o in self.vehs:
            if o.mode == "lane":
                if self.t > o.t_switch:
                    o.v_tgt = float(r.uniform(*D["v_set"])); o.t_switch = self.t + float(r.uniform(3, 8))
                if r.random() < D["lam_brake"] * dt and o.v > 2.0:
                    o.brake_until = self.t + float(r.uniform(0.8, 2.0)); o.brake_a = -float(r.uniform(4.0, 7.0))
                p = self._pred(o)
                acc = idm_acc(o.v, o.v_tgt, (p.pos - o.pos - VEH_LEN) if p else 1e3, (o.v - p.v) if p else 0.0)
                if self.t < o.brake_until:
                    acc = o.brake_a
                o.v = max(0.0, o.v + max(acc, -8.0) * dt)
            else:
                gap = o.pos - self.se
                if o.mode == "cutin" and self.t >= o.t0 and gap < 1.0 and abs(o.X) > 1.8:
                    o.mode = "adj"                      # yields: ego is alongside
                if o.mode in ("cutin", "feint") and self.t >= o.t0:
                    u = min(1.0, (self.t - o.t0) / o.T)
                    if o.mode == "cutin":
                        o.X = o.X0 + (o.X1 - o.X0) * 0.5 * (1 - math.cos(math.pi * u))
                        if u >= 1.0:
                            o.mode = "lane"
                    else:
                        o.X = o.X0 + (o.X1 - o.X0) * math.sin(math.pi * u)
                        if u >= 1.0:
                            o.mode = "adj"
                o.v = max(0.0, o.v + float(r.normal(0, 0.3)) * dt)
            o.pos += o.v * dt
        self.vehs = [o for o in self.vehs if -8.0 < o.pos - self.se < 90.0]
        if not any(o.mode == "lane" for o in self.vehs):
            self.vehs.append(self._new(45.0, float(r.uniform(*D["v_set"])), 0.0))
        self.road_pitch += (-self.road_pitch / 1.0) * dt + self.N["s_road"] * math.sqrt(2 * dt / 1.0) * float(r.normal())
        self.t += dt
        for o in self.vehs:
            gap = o.pos - self.se
            if -VEH_LEN < gap <= 0.0 and abs(o.X) < 1.8:
                self.collided = True

    def observe(self, cam: Camera):
        """Box-level measurements: dict vid -> (dy, w_px, u_px, occluded)."""
        r, N = self.rng, self.N
        pitch_px = cam.f * N["k_pitch"] * self.ae + self.road_pitch   # braking => range over-estimate
        vis = sorted([o for o in self.vehs if 1.0 < o.pos - self.se <= 60.0], key=lambda o: o.pos)
        out = {}
        for i, o in enumerate(vis):
            if r.random() < N["p_miss"]:
                continue
            Z = o.pos - self.se
            occ = any(abs(n.X - o.X) < 1.5 for n in vis[:i])
            ny = float(r.normal(0, N["sy"])) * (6.0 if r.random() < N["p_out"] else 1.0)
            dy = cam.f * cam.h / Z + ny + pitch_px
            w = cam.f * o.W / Z + float(r.normal(0, N["sw"]))
            if occ:
                dy -= o.occ_bias; ny2 = float(r.normal(0, N["sy"])); dy += ny2
                w *= float(r.uniform(0.6, 0.95))
            u = cam.f * o.X / Z + float(r.normal(0, N["su"]))
            out[o.vid] = (dy, w, u, occ)
        return out

    def truth(self):
        return {o.vid: (o.pos - self.se, o.v - self.ve, o.X) for o in self.vehs}


# ----------------------------------------------------------------------------
# Part C.  Pipeline, baselines, experiment runner
# ----------------------------------------------------------------------------
METHODS = {
    # name: (bound, anticipate cut-ins, use width cue)
    "Point-KF":            ("none",  False, True),
    "CTH-ACC+AEB":         ("cth",   False, True),
    "Gaussian-KF":         ("gauss", True,  True),
    "Split-CP":            ("split", True,  True),
    "CUSP (full)":         ("aci",   True,  True),
    "CUSP w/o cut-in":     ("aci",   False, True),
    "CUSP w/o width cue":  ("aci",   True,  False),
    "Oracle perception":   ("oracle", True, True),
}
# data-collection policies used only for offline calibration (not reported)
_CAL = {"_cal_w": ("gauss", True, True), "_cal_nw": ("gauss", True, False)}
Z975 = 1.959964  # Gaussian quantile matching alpha/2 = 0.025


class Pipeline:
    """Per-frame perception-to-decision pipeline over tracker output."""

    def __init__(self, method: str, cal=None, cam=Camera(), alpha=0.05):
        self.bound, antic, use_w = {**METHODS, **_CAL}[method]
        self.cam = cam
        self.fcfg = FilterCfg(use_width=use_w)
        self.dcfg = DecisionCfg(anticipate=antic)
        self.dec = SpeedDecision(self.dcfg)
        self.tracks: dict[int, tuple[LogRangeFilter, LateralFilter]] = {}
        self.conf = None
        if self.bound in ("split", "aci"):
            key = "w" if use_w else "nw"
            self.conf = Conformal(cal[key]["s"], cal[key]["sd"], cal[key]["nu"], alpha=alpha,
                                  adaptive=(self.bound == "aci"))

    def quantiles(self):
        if self.bound in ("none", "cth", "oracle"):
            return 0.0, 0.0
        if self.bound == "gauss":
            return Z975, Z975
        return self.conf.q_s, self.conf.q_sd

    def perceive(self, obs: dict, a_ego: float, dt: float, v_ego: float = 0.0):
        cam, fc = self.cam, self.fcfg
        nus = []
        for vid in list(self.tracks):
            if vid not in obs:
                lf, xf = self.tracks[vid]
                lf.coast += 1
                if lf.Z < fc.z_blind:
                    # Blind zone: the vehicle cannot be observed, so absence of a
                    # detection is not evidence of absence. Hold the track without
                    # time-out and propagate it as a stationary obstacle (worst case).
                    Z = lf.Z
                    lf.x[1] = -v_ego / Z
                    lf.x[0] = max(lf.x[0] + lf.x[1] * dt, math.log(0.2))
                    continue
                lf.predict(dt, a_ego); xf.predict(dt)
                limit = 3.0 if lf.Z < 6.0 else 1.0      # near tracks are held longer
                if lf.coast * dt > limit or lf.Z > 80 or not np.isfinite(lf.P).all():
                    del self.tracks[vid]
        for vid, (dy, w, u, occ) in obs.items():
            if dy is None:                         # bottom edge outside the image
                if vid in self.tracks:
                    lf, xf = self.tracks[vid]
                    lf.predict(dt, a_ego); xf.predict(dt)
                    lf.update(None, w, occ)
                    Z = lf.Z
                    xf.update(Z * u / cam.f, (Z * fc.sigma_u / cam.f) ** 2 + (0.02 * abs(xf.x[0])) ** 2)
                continue                           # cannot initialise without ground contact
            dyc = max(dy, 2.0)
            if vid in self.tracks and self.tracks[vid][0].n_gated >= 3:
                del self.tracks[vid]               # filter lock-out: re-initialise
            if vid not in self.tracks:
                sd_y = math.hypot(fc.sigma_y, fc.sigma_pitch) * (fc.occ_inflate if occ else 1.0)
                m1 = math.log(cam.f * cam.h / dyc)
                lf = LogRangeFilter(m1, math.log(max(w, 4.0)), (sd_y / dyc) ** 2, cam, fc)
                Z = lf.Z
                xf = LateralFilter(Z * u / cam.f, (Z * fc.sigma_u / cam.f) ** 2, fc)
                if Z < 6.0:    # re-acquisition under a new id releases a blind-zone ghost
                    for gid, (glf, gxf) in list(self.tracks.items()):
                        if glf.coast > 0 and glf.Z < fc.z_blind and abs(gxf.x[0] - xf.x[0]) < 1.0:
                            del self.tracks[gid]
                self.tracks[vid] = (lf, xf)
                continue
            lf, xf = self.tracks[vid]
            lf.predict(dt, a_ego); xf.predict(dt)
            nus.append(abs(lf.update(dy, w, occ)))
            Z = lf.Z
            xf.update(Z * u / cam.f, (Z * fc.sigma_u / cam.f) ** 2 + (0.02 * abs(xf.x[0])) ** 2)
        if self.conf is not None:
            self.conf.step(nus)

    def views(self):
        qs, qv = self.quantiles()
        out = {}
        for vid, (lf, xf) in self.tracks.items():
            Z_lo = math.exp(lf.x[0] - qs * lf.sig_s)
            sd_lo = lf.x[1] - qv * lf.sig_sd
            hz = (0.0, 0.5, 1.0, 1.5) if self.dcfg.anticipate else (0.0,)
            out[vid] = TrackView(lf.Z, Z_lo, sd_lo, xf.p_in_corridor(self.dcfg.half_w, hz))
        return out

    def act(self, v_ego: float, dt: float, truth=None):
        c = self.dcfg
        if self.bound == "oracle":
            vs = []
            for vid, (Z, dv, X) in truth.items():
                if 0.0 < Z <= 60.0:
                    vs.append(TrackView(Z, Z, dv / Z, 1.0 if abs(X) < c.half_w else 0.0))
            a, _, _ = self.dec.decide(v_ego, vs, dt)
            return a
        views = self.views()
        if self.bound == "cth":            # constant time-headway ACC + TTC-triggered AEB
            lead = None
            for v in views.values():
                if v.p_conf >= 0.5 and (lead is None or v.Z_hat < lead.Z_hat):
                    lead = v
            if lead is None:
                a_ref = min(c.a_max, (c.v_des - v_ego) / c.T_g)
            else:
                zdot = lead.sd_lo * lead.Z_hat
                a_ref = 0.25 * (lead.Z_hat - c.d0 - 1.0 * v_ego) + 0.8 * zdot
                a_ref = min(a_ref, (c.v_des - v_ego) / c.T_g, c.a_max)
                a_ref = max(a_ref, -3.5)
                tau = -1.0 / lead.sd_lo if lead.sd_lo < -1e-6 else math.inf
                if tau < 1.4 and v_ego > 0.3:
                    self.dec.a_prev = -c.b_max
                    return -c.b_max
            a = min(self.dec.a_prev + c.j_max * dt, max(self.dec.a_prev - c.j_max * dt, a_ref))
            self.dec.a_prev = a
            return a
        a, _, _ = self.dec.decide(v_ego, list(views.values()), dt)
        return a


def run_episode(args):
    method, density, noise, seed, cal, collect = args
    w = World(seed, density, noise)
    pipe = Pipeline(method, cal)
    cam = pipe.cam
    a_cmd, a_last = 0.0, 0.0
    jerk2, n, hard, dist = 0.0, 0, 0, 0.0
    min_ttc, min_gap, unsafe = math.inf, math.inf, 0
    cov_s = cov_sd = cov_n = 0
    width_sum = 0.0
    alpha_sum = 0.0
    S, SD, NU = [], [], []
    in_hard = False
    while w.t < w.T_end and not w.collided:
        obs = w.observe(cam)
        pipe.perceive(obs, w.ae, DT, w.ve)
        truth = w.truth()
        a_new = pipe.act(w.ve, DT, truth)
        # --- evaluation against ground truth
        qs, qv = pipe.quantiles()
        for vid, (lf, xf) in pipe.tracks.items():
            if vid in truth and lf.age >= 5 and 1.0 < truth[vid][0] <= 60.0:
                Zt, dvt, Xt = truth[vid]
                st, sdt = math.log(Zt), dvt / Zt
                if collect and (n % 10 == 0):
                    S.append((lf.x[0] - st) / lf.sig_s); SD.append((lf.x[1] - sdt) / lf.sig_sd)
                    NU.append(abs(lf.last_nu))
                if abs(Xt) < 1.8:
                    cov_n += 1
                    cov_s += (lf.x[0] - qs * lf.sig_s) <= st
                    cov_sd += (lf.x[1] - qv * lf.sig_sd) <= sdt
                    width_sum += 1.0 - math.exp(-qs * lf.sig_s)
        for vid, (Zt, dvt, Xt) in truth.items():
            if abs(Xt) < 1.8 and Zt > 0:
                min_gap = min(min_gap, Zt)
                if dvt < -0.1:
                    min_ttc = min(min_ttc, Zt / -dvt)
                v_l = w.ve + dvt
                if Zt < w.ve * 0.3 + w.ve ** 2 / (2 * 8.0) - v_l ** 2 / (2 * 8.0):
                    unsafe += 1
        if pipe.conf is not None:
            alpha_sum += pipe.conf.alpha_t
        # --- actuate with one-frame processing delay
        w.step(a_cmd)
        a_cmd = a_new
        jerk2 += ((w.ae - a_last) / DT) ** 2
        if w.ae < -4.0 and not in_hard:
            hard += 1
        in_hard = w.ae < -4.0
        a_last = w.ae
        dist += w.ve * DT
        n += 1
    res = dict(col=int(w.collided), min_ttc=min_ttc, min_gap=min_gap, unsafe=unsafe, n=n,
               dist=dist, jerk2=jerk2, hard=hard, cov_s=int(cov_s), cov_sd=int(cov_sd), cov_n=cov_n,
               width_sum=width_sum, alpha_sum=alpha_sum)
    if collect:
        res.update(S=S, SD=SD, NU=NU)
    return res


def calibrate(pool, n_ep=120):
    """Offline split-conformal calibration on held-out nominal episodes
    (seeds disjoint from test). Ground truth plays the role of LiDAR labels."""
    cal = {}
    for key, method in (("w", "_cal_w"), ("nw", "_cal_nw")):
        jobs = [(method, d, "nominal", 900000 + i, None, True)
                for i in range(n_ep) for d in ("low", "medium", "high")]
        rs = pool.map(run_episode, jobs, chunksize=8)
        cal[key] = dict(s=np.concatenate([r["S"] for r in rs]),
                        sd=np.concatenate([r["SD"] for r in rs]),
                        nu=np.concatenate([r["NU"] for r in rs]))
    return cal


def summarise(rs):
    n_ep = len(rs)
    T = sum(r["n"] for r in rs)
    km = sum(r["dist"] for r in rs) / 1000.0
    ttc = np.array([min(r["min_ttc"], 20.0) for r in rs])
    cn = max(1, sum(r["cov_n"] for r in rs))
    col = sum(r["col"] for r in rs)
    p = col / n_ep
    return dict(
        episodes=n_ep, collisions=col, collision_pct=100 * p,
        collision_ci95=100 * 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / n_ep),
        ttc_p5=float(np.percentile(ttc, 5)), ttc_lt1_pct=100 * float(np.mean(ttc < 1.0)),
        unsafe_pct=100 * sum(r["unsafe"] for r in rs) / T,
        mean_speed=km * 1000 / (T * DT), rms_jerk=math.sqrt(sum(r["jerk2"] for r in rs) / T),
        hard_brakes_per_km=sum(r["hard"] for r in rs) / max(km, 1e-9),
        cov_range=100 * sum(r["cov_s"] for r in rs) / cn, cov_rate=100 * sum(r["cov_sd"] for r in rs) / cn,
        rel_margin_pct=100 * sum(r["width_sum"] for r in rs) / cn,
        mean_alpha_t=sum(r["alpha_sum"] for r in rs) / T)


def latency_benchmark(cal, counts=(5, 10, 20, 40), frames=400):
    """Wall-clock cost of filter + conformal + decision per frame (single core)."""
    rng = np.random.default_rng(0)
    cam = Camera()
    out = {}
    for k in counts:
        pipe = Pipeline("CUSP (full)", cal)
        Z = rng.uniform(5, 50, k); X = rng.uniform(-5, 5, k)
        ts = []
        for _ in range(frames):
            obs = {i: (cam.f * cam.h / Z[i] + rng.normal(0, 1.5), cam.f * 1.75 / Z[i] + rng.normal(0, 2),
                       cam.f * X[i] / Z[i] + rng.normal(0, 2), False) for i in range(k)}
            t0 = time.perf_counter()
            pipe.perceive(obs, 0.0, DT, 8.0)
            pipe.act(8.0, DT)
            ts.append((time.perf_counter() - t0) * 1e3)
        ts = np.array(ts[20:])
        out[k] = dict(mean_ms=float(ts.mean()), p99_ms=float(np.percentile(ts, 99)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--seed0", type=int, default=1000, help="first test seed (use a fresh value to re-validate)")
    ap.add_argument("--save-cal", default=None, help="write calibration scores (npz) for cusp_video.py")
    a = ap.parse_args()
    n_ep, n_cal = (20, 20) if a.quick else (a.episodes, 120)
    results = {}
    with Pool(a.workers) as pool:
        cal = calibrate(pool, n_cal)
        results["calibration"] = {k: dict(n=int(len(v["s"])),
                                          q_s_975=float(np.quantile(v["s"], 0.975)),
                                          q_sd_975=float(np.quantile(v["sd"], 0.975)),
                                          q_nu_95=float(np.quantile(v["nu"], 0.95))) for k, v in cal.items()}
        print("calibration:", json.dumps(results["calibration"], indent=1))
        if a.save_cal:
            np.savez(a.save_cal, **{k: np.sort(v) for k, v in cal["w"].items()})
        for noise in ("nominal", "shift"):
            for density in ("low", "medium", "high"):
                for m in METHODS:
                    jobs = [(m, density, noise, a.seed0 + i, cal, False) for i in range(n_ep)]
                    s = summarise(pool.map(run_episode, jobs, chunksize=8))
                    results[f"{noise}|{density}|{m}"] = s
                    print(f"{noise:8s} {density:6s} {m:20s} col={s['collision_pct']:5.1f}% "
                          f"ttc5={s['ttc_p5']:.2f}s unsafe={s['unsafe_pct']:.2f}% v={s['mean_speed']:.2f} "
                          f"jerk={s['rms_jerk']:.2f} hb/km={s['hard_brakes_per_km']:.2f} "
                          f"covZ={s['cov_range']:.1f} covR={s['cov_rate']:.1f} "
                          f"marg={s['rel_margin_pct']:.1f}% a_t={s['mean_alpha_t']:.3f}", flush=True)
    results["latency"] = latency_benchmark(cal)
    print("latency:", results["latency"])
    with open(a.out, "w") as f:
        json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
