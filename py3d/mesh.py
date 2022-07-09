import glm
import pygame
import pywavefront


def iterate_vertices_t2f_n3f_v3f(vertices):
    for i in range(0, len(vertices), 8):
        yield (glm.vec3(vertices[i + 5], vertices[i + 6], vertices[i + 7]),
               glm.vec3(vertices[i + 2], vertices[i + 3], vertices[i + 4]),
               glm.vec2(vertices[i + 0], vertices[i + 1]))


def iterate_vertices_v3f(vertices):
    for i in range(0, len(vertices), 3):
        yield (glm.vec3(vertices[i + 0], vertices[i + 1], vertices[i + 2]),
               None,
               glm.vec2())


class Texture:
    def __init__(self, filename):
        self.surface = pygame.image.load(filename).convert()
        self.width, self.height = self.size = self.surface.get_size()

    def map(self, tu, tv):
        u = abs(int(tu * self.width) % self.width)
        v = abs((self.height - int(tv * self.height)) % self.height)

        color = self.surface.get_at([u, v])
        return glm.vec4(*color).xyz / 255


class Mesh:
    def __init__(self) -> None:
        self.pos = glm.vec3()
        self.rot = glm.vec3()
        self.scale = glm.vec3(1)
        self.faces = []
        self.texture = None

    def load_obj(self, path, texture=None):
        if texture:
            self.texture = Texture(texture)

        o = pywavefront.Wavefront(path, create_materials=True, collect_faces=True)
        for mat_name, mat in o.materials.items():
            if mat.vertex_format == 'V3F':
                verts = iterate_vertices_v3f(mat.vertices)
            elif mat.vertex_format == 'T2F_N3F_V3F':
                verts = iterate_vertices_t2f_n3f_v3f(mat.vertices)
            else:
                return

            while True:
                try:
                    self.faces.append([next(verts), next(verts), next(verts)])
                except StopIteration:
                    break

            if not mat.has_normals:
                self.generate_normals()

    def generate_normals(self):
        for face in self.faces:
            v0, v1, v2 = [v for v, n, u in face]
            normal = glm.normalize(glm.cross(v1 - v0, v0 - v2))
            for i, (v, n, u) in enumerate(face):
                face[i] = (v, normal, u)

    def world_matrix(self):
        world_matrix = glm.mat4(1)
        world_matrix = glm.translate(world_matrix, self.pos)
        world_matrix = glm.rotate(world_matrix, self.rot.x, glm.vec3(1, 0, 0))
        world_matrix = glm.rotate(world_matrix, self.rot.y, glm.vec3(0, 1, 0))
        world_matrix = glm.rotate(world_matrix, self.rot.z, glm.vec3(0, 0, 1))
        return glm.scale(world_matrix, self.scale)

    def world_faces(self):
        world_matrix = self.world_matrix()
        for f in self.faces:
            yield [(world_matrix * v, glm.normalize((world_matrix * n).xyz), u) for v, n, u in f]
