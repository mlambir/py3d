import glm
import pygame
import numpy as np

from camera import Camera


def interpolate(min_, max_, gradient):
    return min_ + (max_ - min_) * glm.clamp(gradient, 0, 1)


class Scene:
    def __init__(self, size, camera=None):
        self.camera = camera if camera else Camera(size)
        self.surface = pygame.Surface(size)
        self.zbuf = np.full(size, 2.)
        self.size = size

    def clear(self):
        self.surface.fill((0, 0, 0))
        self.zbuf = np.full(self.size, 2.)

    def project(self, v):
        v = glm.vec3(v.x, v.y, v.z)
        point = glm.project(v, glm.mat4(1), self.camera.vp_matrix(), glm.vec4(0, 0, self.size[0], self.size[1]))
        point.z = glm.length(v - self.camera.pos)
        return point

    def draw_mesh_points(self, mesh):
        width, height = self.size
        for v in mesh.world_vertices():
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

    def process_scanline(self, y, pa, pb, pc, pd, color):
        gradient1 = (y - pa.y) / (pb.y - pa.y) if pa.y != pb.y else 1.
        gradient2 = (y - pc.y) / (pd.y - pc.y) if pc.y != pd.y else 1.

        sx = int(interpolate(pa.x, pb.x, gradient1))
        ex = int(interpolate(pc.x, pd.x, gradient2))
        z1 = interpolate(pa.z, pb.z, gradient1)
        z2 = interpolate(pc.z, pd.z, gradient2)

        width, height = self.size
        for x in range(sx, ex):
            gradient = (x - sx) / (ex - sx)
            z = interpolate(z1, z2, gradient)
            if 0 < x < width and 0 < y < height and self.zbuf[x, y] > z / 100:
                self.zbuf[x, y] = z / 100
                self.surface.set_at((x, y), color)

    def draw_triangle(self, p1, p2, p3, color):
        if p1.y > p2.y:
            p1, p2 = p2, p1
        if p2.y > p3.y:
            p2, p3 = p3, p2
        if p1.y > p2.y:
            p1, p2 = p2, p1

        if p2.y - p1.y > 0:
            dP1P2 = (p2.x - p1.x) / (p2.y - p1.y)
        else:
            dP1P2 = 0

        if p3.y - p1.y > 0:
            dP1P3 = (p3.x - p1.x) / (p3.y - p1.y)
        else:
            dP1P3 = 0

        if dP1P2 > dP1P3:
            for y in range(int(p1.y), int(p3.y) + 1):
                if y < p2.y:
                    self.process_scanline(y, p1, p3, p1, p2, color)
                else:
                    self.process_scanline(y, p1, p3, p2, p3, color)
        else:
            for y in range(int(p1.y), int(p3.y) + 1):
                if y < p2.y:
                    self.process_scanline(y, p1, p2, p1, p3, color)
                else:
                    self.process_scanline(y, p2, p3, p1, p3, color)

    def draw_mesh_triangles_scan(self, mesh):
        light_position = glm.vec3(0, -10, 0)

        world_normals = mesh.world_normals()
        world_vertices = mesh.world_vertices()
        for i, face in enumerate(mesh.faces):
            a, b, c = (self.project(world_vertices[i]) for i in face)
            normal = world_normals[i].xyz

            center_point = (world_vertices[face[0]] + world_vertices[face[1]] + world_vertices[face[2]]) / 3

            if glm.dot(normal, center_point - self.camera.pos) < 0:
                continue

            light_direction = glm.normalize(light_position - center_point)
            light_intensity = int(max(0, glm.dot(normal, light_direction)) * 255)

            try:
                #color = (abs(int(normal.x * 255)), abs(int(normal.y * 255)), abs(int(normal.z * 255)))
                color = [light_intensity] * 3
            except:
                color = (255, 255, 255)

            self.draw_triangle(a, b, c, color)

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