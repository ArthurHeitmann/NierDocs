# Bezier vec --> Hermit vec
h_p1 = (b_p1 - (0,0)) * 3
h_p2 = (b_p2 - (1,1)) * 3

# Hermit vec --> Bezier vec
b_p1 = h_p1 / 3
b_p2 = ((1,1) - h_p2) / 3

# Hermit 2D Vec --> Hermit 1D coefficient
        v_y2 - v_y1
hc(v) = -----------
        v_x2 - v_x1

# Hermit 1D coefficient --> hermit 2D Vec
_v(m) = (1, m)
v(m) = _v(m) / |_v|
