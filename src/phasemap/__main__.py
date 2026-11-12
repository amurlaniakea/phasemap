"""Demo CLI: python -m phasemap (solo stdlib, sin instalar nada)."""
from . import PRESETS, scan_diagram, MiscibilityGap, R, __version__
from .models import water as w

def main():
    print(f"PHASEMAP v{__version__} - nucleo termodinamico (stdlib)")
    print("-" * 62)
    for pr in PRESETS.values():
        d = scan_diagram(pr.system(), rows=200, n=240)
        if d.eutectic:
            e = d.eutectic
            print(f"{pr.name:14s} eutectico  T_E = {e['T']:7.1f} K   x_E = {e['xE']:.3f}")
        else:
            print(f"{pr.name:14s} isomorfo   (lente sin eutectico)")
    g = MiscibilityGap(18000.0)
    print(f"Lacuna regular  T_c = Omega/2R = {g.Tc:.1f} K  (Omega = 18 kJ/mol)")
    print("-" * 62)
    print(f"Agua: P_vap(273.16 K) = {w.p_vap(w.Tt):.3f} Pa  (IAPWS: 611.657)")
    print(f"Agua: T_ebullicion(1 atm) = {w.boiling_temperature():.3f} K  (ref: 373.124)")
    L = w.clausius_latent(373.15) / 1000.0
    print(f"Agua: L_est(373.15 K) = {L:.2f} kJ/mol  (ref: 40.657; vapor ideal +1.6%)")
    print(f"Agua: fase a 300 K / 2 GPa = {w.classify(300.0, 2e9)}")

if __name__ == "__main__":
    main()
