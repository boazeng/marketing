"""OKLCH -> sRGB hex. Shared by palette.py and contrast.py."""
import math

def _lin_to_srgb(c):
    c = 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055
    return max(0.0, min(1.0, c))

def _srgb_to_lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def oklch(L, C, H):
    """L 0..1, C chroma, H degrees -> '#RRGGBB' (clipped to sRGB gamut)."""
    h = math.radians(H)
    a, b = C*math.cos(h), C*math.sin(h)
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r =  4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    return '#%02X%02X%02X' % tuple(round(_lin_to_srgb(v)*255) for v in (r, g, bl))

def relative_luminance(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    r, g, b = _srgb_to_lin(r), _srgb_to_lin(g), _srgb_to_lin(b)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast_ratio(fg, bg):
    a, b = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)
