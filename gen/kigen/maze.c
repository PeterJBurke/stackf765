/* Grid maze-router kernel (A* over layer/x/y with 8-direction moves and vias).
 *
 * Occupancy grids (int32 per cell, per layer):
 *   0  = free,  n>0 = reserved for net n (other nets may not place a track
 *   centre here),  -1 = blocked for everybody.
 * 'hard' holds pads, board edge, holes, keep-outs.  'soft' holds routed
 * copper; in rip-up mode soft conflicts are allowed at a high cost.
 *
 * Build: gcc -O2 -shared -fPIC -o maze.so maze.c
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int32_t f; int32_t idx; } HeapItem;
static HeapItem *heap = 0; static int hn = 0, hcap = 0;
static void hpush(int32_t f, int32_t idx) {
    if (hn == hcap) { hcap = hcap ? hcap * 2 : 1 << 16; heap = realloc(heap, sizeof(HeapItem) * hcap); }
    int i = hn++;
    while (i > 0) { int p = (i - 1) / 2; if (heap[p].f <= f) break; heap[i] = heap[p]; i = p; }
    heap[i].f = f; heap[i].idx = idx;
}
static HeapItem hpop(void) {
    HeapItem top = heap[0]; HeapItem last = heap[--hn];
    int i = 0;
    for (;;) {
        int c = 2 * i + 1; if (c >= hn) break;
        if (c + 1 < hn && heap[c + 1].f < heap[c].f) c++;
        if (heap[c].f >= last.f) break;
        heap[i] = heap[c]; i = c;
    }
    heap[i] = last; return top;
}

static const int DX[8] = {1, 1, 0, -1, -1, -1, 0, 1};
static const int DY[8] = {0, 1, 1, 1, 0, -1, -1, -1};

typedef struct {
    int W, H, L, net;
    const int32_t *hard, *soft;
    const int *probe_t; int nprobe_t;
    const int *probe_v; int nprobe_v;
} Ctx;

/* 0 ok, 1 soft conflict, 2 hard conflict */
static inline int cell(const Ctx *c, int l, int x, int y, const int *probe, int np) {
    int res = 0;
    for (int i = 0; i < np; i++) {
        int px = x + probe[2 * i], py = y + probe[2 * i + 1];
        if (px < 0 || py < 0 || px >= c->W || py >= c->H) return 2;
        long k = ((long)l * c->H + py) * c->W + px;
        int32_t h = c->hard[k];
        if (h != 0 && h != c->net) return 2;
        int32_t s = c->soft[k];
        if (s != 0 && s != c->net) res = 1;
    }
    return res;
}

/* mode 0: reach any target cell.  mode 1: stop at any legal via site (cost includes via).
 * layer_cost[l] == 0 means the layer is not routable; otherwise per-step multiplier (x10 base).
 * Returns path length (number of (l,x,y) triples written, target first), 0 if none, -1 if overflow. */
int route(int W, int H, int L, const int32_t *hard, const int32_t *soft, const uint8_t *novia, const int32_t *hist,
          int net, const int *layer_cost,
          int nsrc, const int *src, int ntgt, const int *tgt, int mode,
          int via_cost, int soft_cost, int turn_cost,
          int nprobe_t, const int *probe_t, int nprobe_v, const int *probe_v,
          int max_expand, int *out_path, int max_path, int *out_cost)
{
    long N = (long)W * H * L;
    int32_t *g = malloc(sizeof(int32_t) * N);
    int32_t *par = malloc(sizeof(int32_t) * N);
    uint8_t *dir = malloc(N);          /* arrival direction 0..7, 8 = via, 9 = source */
    uint8_t *state = calloc(N, 1);     /* bit0 closed, bit1 target */
    uint8_t *viamemo = calloc((long)W * H, 1);
    if (!g || !par || !dir || !state || !viamemo) return 0;
    for (long i = 0; i < N; i++) g[i] = INT32_MAX;
    Ctx c = {W, H, L, net, hard, soft, probe_t, nprobe_t, probe_v, nprobe_v};
    hn = 0;
    int tx0 = W, tx1 = -1, ty0 = H, ty1 = -1;
    for (int i = 0; i < ntgt; i++) {
        int l = tgt[3 * i], x = tgt[3 * i + 1], y = tgt[3 * i + 2];
        if (x < 0 || y < 0 || x >= W || y >= H) continue;
        state[((long)l * H + y) * W + x] |= 2;
        if (x < tx0) tx0 = x; if (x > tx1) tx1 = x; if (y < ty0) ty0 = y; if (y > ty1) ty1 = y;
    }
    for (int i = 0; i < nsrc; i++) {
        int l = src[3 * i], x = src[3 * i + 1], y = src[3 * i + 2];
        if (x < 0 || y < 0 || x >= W || y >= H) continue;
        long k = ((long)l * H + y) * W + x;
        if (g[k] == 0) continue;
        g[k] = 0; par[k] = -1; dir[k] = 9;
        int hx = x < tx0 ? tx0 - x : (x > tx1 ? x - tx1 : 0);
        int hy = y < ty0 ? ty0 - y : (y > ty1 ? y - ty1 : 0);
        int h = mode == 1 ? 0 : 10 * (hx > hy ? hx : hy) + 4 * (hx < hy ? hx : hy);
        hpush(h, (int32_t)k);
    }
    long found = -1; int expanded = 0; int found_via = 0;
    while (hn > 0) {
        HeapItem it = hpop();
        long k = it.idx;
        if (state[k] & 1) continue;
        state[k] |= 1;
        int l = (int)(k / ((long)W * H)); int rem = (int)(k % ((long)W * H)); int y = rem / W, x = rem % W;
        if (mode == 0 && (state[k] & 2)) { found = k; break; }
        if (mode == 1 && dir[k] != 9) {
            uint8_t *vm = &viamemo[(long)y * W + x];
            if (*vm == 0) {
                int worst = novia[(long)y * W + x] ? 2 : 0;
                for (int ll = 0; ll < L && worst < 2; ll++) {
                    int r = cell(&c, ll, x, y, probe_v, nprobe_v); if (r > worst) worst = r;
                }
                *vm = (uint8_t)(worst + 1);
            }
            if (*vm == 1) { found = k; found_via = 1; break; }
        }
        if (++expanded > max_expand) break;
        int32_t gk = g[k];
        int d0 = dir[k];
        for (int d = 0; d < 8; d++) {
            int nx = x + DX[d], ny = y + DY[d];
            if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
            int tc = 0;
            if (d0 < 8) {
                int dd = (d - d0) & 7; if (dd > 4) dd = 8 - dd;
                if (dd > 2) continue;            /* no acute turns */
                tc = dd == 0 ? 0 : (dd == 1 ? turn_cost : 4 * turn_cost);
            }
            long nk = ((long)l * H + ny) * W + nx;
            if (state[nk] & 1) continue;
            int r = (state[nk] & 2) && mode == 0 ? 0 : cell(&c, l, nx, ny, probe_t, nprobe_t);
            if (r == 2) continue;
            if (r == 1 && soft_cost == 0) continue;
            int step = ((d & 1) ? 14 : 10) * layer_cost[l] / 10 + tc + (r == 1 ? soft_cost : 0) + (hist ? hist[nk] : 0);
            int32_t ng = gk + step;
            if (ng < g[nk]) {
                g[nk] = ng; par[nk] = (int32_t)k; dir[nk] = (uint8_t)d;
                int hx = nx < tx0 ? tx0 - nx : (nx > tx1 ? nx - tx1 : 0);
                int hy = ny < ty0 ? ty0 - ny : (ny > ty1 ? ny - ty1 : 0);
                int h = mode == 1 ? 0 : 10 * (hx > hy ? hx : hy) + 4 * (hx < hy ? hx : hy);
                hpush(ng + h, (int32_t)nk);
            }
        }
        if (mode == 0 && via_cost > 0) {
            uint8_t *vm = &viamemo[(long)y * W + x];
            if (*vm == 0) {
                int worst = novia[(long)y * W + x] ? 2 : 0;
                for (int ll = 0; ll < L && worst < 2; ll++) {
                    int r = cell(&c, ll, x, y, probe_v, nprobe_v); if (r > worst) worst = r;
                }
                *vm = (uint8_t)(worst + 1);
            }
            int vr = *vm - 1;
            if (vr < 2 && !(vr == 1 && soft_cost == 0)) {
                for (int nl = 0; nl < L; nl++) {
                    if (nl == l || layer_cost[nl] == 0) continue;
                    long nk = ((long)nl * H + y) * W + x;
                    if (state[nk] & 1) continue;
                    int r = cell(&c, nl, x, y, probe_t, nprobe_t);
                    if (r == 2 || (r == 1 && soft_cost == 0)) continue;
                    int32_t ng = gk + via_cost + (vr == 1 ? soft_cost * 4 : 0) + (r == 1 ? soft_cost : 0) + (hist ? hist[nk] : 0);
                    if (ng < g[nk]) {
                        g[nk] = ng; par[nk] = (int32_t)k; dir[nk] = 8;
                        int hx = x < tx0 ? tx0 - x : (x > tx1 ? x - tx1 : 0);
                        int hy = y < ty0 ? ty0 - y : (y > ty1 ? y - ty1 : 0);
                        hpush(ng + 10 * (hx > hy ? hx : hy) + 4 * (hx < hy ? hx : hy), (int32_t)nk);
                    }
                }
            }
        }
    }
    int n = 0;
    if (found >= 0) {
        *out_cost = g[found] + (found_via ? via_cost : 0);
        long k = found;
        while (k >= 0) {
            if (n >= max_path) { n = -1; break; }
            int l = (int)(k / ((long)W * H)); int rem = (int)(k % ((long)W * H));
            out_path[3 * n] = l; out_path[3 * n + 1] = rem % W; out_path[3 * n + 2] = rem / W; n++;
            k = par[k];
        }
    }
    free(g); free(par); free(dir); free(state); free(viamemo);
    return n;
}
