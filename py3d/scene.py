import dataclasses

import glm
import pygame
import numpy as np

from camera import Camera

@dataclasses.dataclass
class ScanlineData:
    y = None
    ndotla = ndotlb = ndotlc = ndotld = None
    ua = ub = uc = ud = None
    va = vb = vc = vd = None

def calc_n_dot_l(vertex, normal, light_pos):
    light_direction = vertex - light_pos
    normal = glm.normalize(normal)
    light_direction = glm.normalize(light_direction)
    return max(0, (glm.dot(normal, light_direction) * .8 + .2))


class Scene:
    def __init__(self, size, camera=None):
        self.camera = camera if camera else Camera(size)
        self.surface = pygame.Surface(size)
        self.zbuf = np.full(size, 2.)
        self.size = size

    def clear(self):
        self.surface.fill((50, 0, 0))
        self.zbuf = np.full(self.size, 2.)

    def project(self, v):
        v = glm.vec4(v.x, v.y, v.z, 1)

        tmp = self.camera.vp_matrix() * v
        tmp /= tmp.w
        tmp = tmp * glm.vec4(1, 1, 1, 1) * 0.5 + 0.5
        tmp.x *= self.size[0]
        tmp.y *= self.size[1]
        tmp.z = glm.length(v.xyz - self.camera.pos)
        return tmp

    def draw_mesh_points(self, mesh):
        width, height = self.size
        for f in mesh.world_faces():
            for v, _, _ in f:
                point = self.project(v)
                if 0 < point.x < width and 0 < point.y < height:
                    pygame.gfxdraw.pixel(self.surface, int(point.x), int(point.y), (255, 255, 255))

    def draw_mesh_lines(self, mesh):
        world_vertices = mesh.world_vertices()
        for face in mesh.faces:
            a, b, c = (self.project(world_vertices[i]) for i in face)
            pygame.gfxdraw.line(self.surface, int(a.x), int(a.y), int(b.x), int(b.y), (255, 255, 255))
            pygame.gfxdraw.line(self.surface, int(c.x), int(c.y), int(b.x), int(b.y), (255, 255, 255))
            pygame.gfxdraw.line(self.surface, int(a.x), int(a.y), int(c.x), int(c.y), (255, 255, 255))

    def draw_mesh_triangles(self, mesh):
        world_vertices = mesh.world_vertices()
        for i, face in enumerate(mesh.faces):
            a, b, c = (self.project(world_vertices[i]) for i in face)
            pygame.gfxdraw.filled_trigon(self.surface, int(a.x), int(a.y), int(b.x), int(b.y), int(c.x), int(c.y),
                                         (255, 255, 255))

    def process_scanline(self, data, pa, pb, pc, pd, color, texture=None):
        gradient1 = (data.y - pa.y) / (pb.y - pa.y) if pa.y != pb.y else 1.
        gradient2 = (data.y - pc.y) / (pd.y - pc.y) if pc.y != pd.y else 1.

        sx = int(glm.lerp(pa.x, pb.x, gradient1))
        ex = int(glm.lerp(pc.x, pd.x, gradient2))
        z1 = glm.lerp(pa.z, pb.z, gradient1)
        z2 = glm.lerp(pc.z, pd.z, gradient2)

        snl = glm.lerp(data.ndotla, data.ndotlb, gradient1)
        enl = glm.lerp(data.ndotlc, data.ndotld, gradient2)

        su = glm.lerp(data.ua, data.ub, gradient1)
        eu = glm.lerp(data.uc, data.ud, gradient2)
        sv = glm.lerp(data.va, data.vb, gradient1)
        ev = glm.lerp(data.vc, data.vd, gradient2)

        width, height = self.size
        for x in range(sx, ex):
            gradient = (x - sx) / (ex - sx)
            z = glm.lerp(z1, z2, gradient)
            ndotl = max(0, glm.lerp(snl, enl, gradient))
            u = glm.lerp(su, eu, gradient)
            v = glm.lerp(sv, ev, gradient)

            if texture:
                texture_color = texture.map(u, v)
            else:
                texture_color = glm.vec3(1,1,1)

            if 0 < x < width and 0 < data.y < height and self.zbuf[x, data.y] > z / 100:
                self.zbuf[x, data.y] = z / 100
                self.surface.set_at((x, data.y), ((color * ndotl * texture_color) * 255))

    def draw_triangle(self, v1, v2, v3, light_pos, color, texture):
        p1, p2, p3 = [self.project(v[0]) for v in (v1, v2, v3)]
        if p1.y > p2.y:
            v1, v2 = v2, v1
            p1, p2 = p2, p1
        if p2.y > p3.y:
            v2, v3 = v3, v2
            p2, p3 = p3, p2
        if p1.y > p2.y:
            v1, v2 = v2, v1
            p1, p2 = p2, p1

        nl1, nl2, nl3 = [calc_n_dot_l(v, n, light_pos) for v,n,_ in (v1, v2, v3)]

        if p2.y - p1.y > 0:
            d_p1_p2 = (p2.x - p1.x) / (p2.y - p1.y)
        else:
            d_p1_p2 = 0

        if p3.y - p1.y > 0:
            d_p1_p3 = (p3.x - p1.x) / (p3.y - p1.y)
        else:
            d_p1_p3 = 0

        if d_p1_p2 > d_p1_p3:
            for y in range(int(p1.y), int(p3.y) + 1):
                if y < p2.y:
                    data = ScanlineData()
                    data.y = y
                    data.ndotla = nl1
                    data.ndotlb = nl3
                    data.ndotlc = nl1
                    data.ndotld = nl2

                    data.ua = v1[2].x
                    data.ub = v3[2].x
                    data.uc = v1[2].x
                    data.ud = v2[2].x

                    data.va = v1[2].y
                    data.vb = v3[2].y
                    data.vc = v1[2].y
                    data.vd = v2[2].y
                    self.process_scanline(data, p1, p3, p1, p2, color, texture)
                else:
                    data = ScanlineData()
                    data.y = y
                    data.ndotla = nl1
                    data.ndotlb = nl3
                    data.ndotlc = nl2
                    data.ndotld = nl3

                    data.ua = v1[2].x
                    data.ub = v3[2].x
                    data.uc = v2[2].x
                    data.ud = v3[2].x

                    data.va = v1[2].y
                    data.vb = v3[2].y
                    data.vc = v2[2].y
                    data.vd = v3[2].y
                    self.process_scanline(data, p1, p3, p2, p3, color, texture)
        else:
            for y in range(int(p1.y), int(p3.y) + 1):
                if y < p2.y:
                    data = ScanlineData()
                    data.y = y
                    data.ndotla = nl1
                    data.ndotlb = nl2
                    data.ndotlc = nl1
                    data.ndotld = nl3

                    data.ua = v1[2].x
                    data.ub = v2[2].x
                    data.uc = v1[2].x
                    data.ud = v3[2].x

                    data.va = v1[2].y
                    data.vb = v2[2].y
                    data.vc = v1[2].y
                    data.vd = v3[2].y
                    self.process_scanline(data, p1, p2, p1, p3, color, texture)
                else:
                    data = ScanlineData()
                    data.y = y
                    data.ndotla = nl2
                    data.ndotlb = nl3
                    data.ndotlc = nl1
                    data.ndotld = nl3

                    data.ua = v2[2].x
                    data.ub = v3[2].x
                    data.uc = v1[2].x
                    data.ud = v3[2].x

                    data.va = v2[2].y
                    data.vb = v3[2].y
                    data.vc = v1[2].y
                    data.vd = v3[2].y
                    self.process_scanline(data, p2, p3, p1, p3, color, texture)

    def draw_mesh_triangles_scan(self, mesh):
        light_position = glm.vec3(10, 10, 10)

        for i, face in enumerate(mesh.world_faces()):
            normal = glm.normalize((face[0][1] + face[1][1] + face[2][1]) / 3)
            center_point = (face[0][0] + face[1][0] + face[2][0]) / 3
            if glm.dot(normal, center_point - self.camera.pos) < 0:
                continue
            self.draw_triangle(*face, light_position, glm.vec3(1, 1, 1), mesh.texture)

    def draw_vertex_index(self, mesh):
        width, height = self.size
        font = pygame.font.Font(pygame.font.get_default_font(), 10)

        for i, v in enumerate(mesh.world_vertices()):
            point = self.project(v)

            if 0 < point.x < width and 0 < point.y < height:
                pygame.gfxdraw.pixel(self.surface, int(point.x), int(point.y), (0, 255, 255))
                self.surface.blit(font.render(str(i), True, (255, 0, 255)), (int(point.x), int(point.y)))

    def draw_origin(self):
        origin = self.project(glm.vec3(0, 0, 0))
        for v in glm.vec3(1, 0, 0), glm.vec3(0, 1, 0), glm.vec3(0, 0, 1):
            p = self.project(v)
            try:
                pygame.gfxdraw.line(self.surface, int(origin.x), int(origin.y), int(p.x), int(p.y),
                                    (v * glm.vec3(255, 255, 255)))
            except:
                pass
