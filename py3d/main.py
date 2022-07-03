import pygame
import pygame.gfxdraw
import glm
import pywavefront


class Camera:
    def __init__(self) -> None:
        self.pos = glm.vec3(0, 0, -10)
        self.dir = glm.vec3(0, 0, 1)
        self.up = glm.vec3(0, 1, 0)

    @property
    def target(self):
        return self.pos + self.dir


class Mesh:
    def __init__(self) -> None:
        self.pos = glm.vec3()
        self.rot = glm.vec3()
        self.scale = glm.vec3(1)
        self.vertices = []
        self.faces = []

    def load_obj(self, path):
        o = pywavefront.Wavefront(path)
        vert_arr = []
        for v in o.vertices:
            self.vertices.append(glm.vec3(*v))
        for mat_name, mat in o.materials.items():
            for i in range(0, len(mat.vertices), 9):
                v1 = (mat.vertices[i], mat.vertices[i+1], mat.vertices[i+2])
                v2 = (mat.vertices[i+3], mat.vertices[i+4], mat.vertices[i+5])
                v3 = (mat.vertices[i+6], mat.vertices[i+7], mat.vertices[i+8])
                self.faces.append((o.vertices.index(v1), o.vertices.index(v2), o.vertices.index(v3)))


class Cube(Mesh):
    def __init__(self) -> None:
        super().__init__()
        self.vertices = [glm.vec3(*v) for v in [
            (-1, 1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (1, -1, 1),
            (-1, 1, -1),
            (1, 1, -1),
            (1, -1, -1),
            (-1, -1, -1),
        ]]

        self.faces = [
            (0,1,2),
            (1,2,3),
            (1,3,6),
            (1,5,6),
            (0,1,4),
            (1,4,5),
            (2,3,7),
            (3,6,7),
            (0,2,7),
            (0,4,7),
            (4,5,6),
            (4,6,7)
        ]


def draw_mesh_points(surface, mesh, vp_matrix):
    width, height = surface.get_size()

    world_matrix = glm.mat4(1)
    world_matrix = glm.translate(world_matrix, mesh.pos)
    world_matrix = glm.rotate(world_matrix, mesh.rot.x, glm.vec3(1, 0, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.y, glm.vec3(0, 1, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.z, glm.vec3(0, 0, 1))
    world_matrix = glm.scale(world_matrix, mesh.scale)

    for v in mesh.vertices:
        point = glm.project(v, world_matrix, vp_matrix, glm.vec4(0, 0, width, height))
        if 0 < point.x < width and 0 < point.y < height:
            pygame.gfxdraw.pixel(surface, int(point.x), int(point.y), (255, 255, 255))

def draw_mesh_lines(surface, mesh, vp_matrix):
    width, height = surface.get_size()

    world_matrix = glm.mat4(1)
    world_matrix = glm.translate(world_matrix, mesh.pos)
    world_matrix = glm.rotate(world_matrix, mesh.rot.x, glm.vec3(1, 0, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.y, glm.vec3(0, 1, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.z, glm.vec3(0, 0, 1))
    world_matrix = glm.scale(world_matrix, mesh.scale)

    for face in mesh.faces:
        a,b,c = (glm.project(mesh.vertices[i], world_matrix, vp_matrix, glm.vec4(0, 0, width, height)) for i in face)
        pygame.gfxdraw.line(surface, int(a.x), int(a.y), int(b.x), int(b.y), (255, 255, 255))
        pygame.gfxdraw.line(surface, int(c.x), int(c.y), int(b.x), int(b.y), (255, 255, 255))
        pygame.gfxdraw.line(surface, int(a.x), int(a.y), int(c.x), int(c.y), (255, 255, 255))

def draw_mesh_triangles(surface, mesh, vp_matrix):
    width, height = surface.get_size()

    world_matrix = glm.mat4(1)
    world_matrix = glm.translate(world_matrix, mesh.pos)
    world_matrix = glm.rotate(world_matrix, mesh.rot.x, glm.vec3(1, 0, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.y, glm.vec3(0, 1, 0))
    world_matrix = glm.rotate(world_matrix, mesh.rot.z, glm.vec3(0, 0, 1))
    world_matrix = glm.scale(world_matrix, mesh.scale)

    for face in mesh.faces:
        a,b,c = (glm.project(mesh.vertices[i], world_matrix, vp_matrix, glm.vec4(0, 0, width, height)) for i in face)
        pygame.gfxdraw.filled_trigon(surface, int(a.x), int(a.y), int(b.x), int(b.y), int(c.x), int(c.y), (255, 255, 255, 40))


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("minimal program")
    size = width, height = (800, 600)
    screen = pygame.display.set_mode(size)
    #mesh = Cube()
    #mesh2 = Cube()
    #mesh2.pos = glm.vec3(1, 1, 1)
    mesh = Mesh()
    mesh.load_obj("data/teapot.obj")
    mesh.scale = glm.vec3(.02, .02, .02)
    camera = Camera()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_rel = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[0]:
            camera.dir = glm.rotateY(camera.dir, mouse_rel[0] * 0.01)
            camera.dir = glm.rotateX(camera.dir, mouse_rel[1] * 0.01)

        keys = pygame.key.get_pressed()
        movement = glm.vec3(0, 0, 0)
        if keys[pygame.K_w]:
            movement += camera.dir * .1
        if keys[pygame.K_s]:
            movement -= camera.dir * .1
        if keys[pygame.K_a]:
            movement += glm.normalize(glm.cross(camera.dir, camera.up)) * .1
        if keys[pygame.K_d]:
            movement -= glm.normalize(glm.cross(camera.dir, camera.up)) * .1
        if keys[pygame.K_SPACE]:
            movement += camera.up * .1
        if keys[pygame.K_LSHIFT]:
            movement -= camera.up * .1

        camera.pos += movement

        mesh.rot.x += 0.01
        mesh.rot.y += 0.02
        mesh.rot.z += 0.03

        screen.fill((0, 0, 0))

        vp_matrix = glm.mat4(1)
        vp_matrix = vp_matrix * glm.perspectiveFovLH(glm.radians(45), width, height, .1, 100)
        vp_matrix = vp_matrix * glm.lookAt(camera.pos, camera.target, camera.up)

        for m in mesh,:
            draw_mesh_triangles(screen, m, vp_matrix)

        origin = glm.project(glm.vec3(0, 0, 0), glm.mat4(1), vp_matrix, glm.vec4(0, 0, width, height))
        for v in glm.vec3(1, 0, 0), glm.vec3(0, 1, 0), glm.vec3(0, 0, 1):
            p = glm.project(v, glm.mat4(1), vp_matrix, glm.vec4(0, 0, width, height))
            try:
                pygame.gfxdraw.line(screen, int(origin.x), int(origin.y), int(p.x), int(p.y),
                                    (v * glm.vec3(255, 255, 255)))
            except:
                pass

        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        screen.blit(font.render(str(int(clock.get_fps())), True, (255, 255, 0)), (5, 5))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
