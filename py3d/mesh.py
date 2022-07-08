import glm
import pywavefront


def iterate_vertices_t2f_n3f_v3f(vertices):
    for i in range(0, len(vertices), 8):
        yield (glm.vec3(vertices[i + 5], vertices[i + 6], vertices[i + 7]),
               glm.vec3(vertices[i + 2], vertices[i + 3], vertices[i + 4]),
               glm.vec2(vertices[i + 0], vertices[i + 1]))


class Mesh:
    def __init__(self) -> None:
        self.pos = glm.vec3()
        self.rot = glm.vec3()
        self.scale = glm.vec3(1)
        self.faces = []

    def load_obj(self, path):
        o = pywavefront.Wavefront(path, create_materials=True, collect_faces=True)
        for mat_name, mat in o.materials.items():
            verts = iterate_vertices_t2f_n3f_v3f(mat.vertices)
            while True:
                try:
                    self.faces.append((next(verts), next(verts), next(verts)))
                except StopIteration:
                    break

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
