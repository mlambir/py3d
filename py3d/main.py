import pygame
import pygame.gfxdraw
import glm


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


class Cube(Mesh):
    def __init__(self) -> None:
        super().__init__()
        self.vertices = [
            glm.vec3(-1.0, -1.0, 1.0),
            glm.vec3(1.0, -1.0, 1.0),
            glm.vec3(1.0, 1.0, 1.0),
            glm.vec3(-1.0, 1.0, 1.0),
            glm.vec3(-1.0, -1.0, -1.0),
            glm.vec3(1.0, -1.0, -1.0),
            glm.vec3(1.0, 1.0, -1.0),
            glm.vec3(-1.0, 1.0, -1.0),
        ]


def main():
    pygame.init()
    pygame.display.set_caption("minimal program")
    size = width, height = (800, 600)
    screen = pygame.display.set_mode(size)
    mesh = Cube()
    mesh2 = Cube()
    mesh2.pos = glm.vec3(1, 1, 1)
    camera = Camera()
    camera.pos = glm.vec3(0, 0, -10)
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
            movement += camera.dir * .01
        if keys[pygame.K_s]:
            movement -= camera.dir * .01
        if keys[pygame.K_a]:
            movement += glm.normalize(glm.cross(camera.dir, camera.up)) * .01
        if keys[pygame.K_d]:
            movement -= glm.normalize(glm.cross(camera.dir, camera.up)) * .01
        if keys[pygame.K_SPACE]:
            movement += camera.up * .01
        if keys[pygame.K_LSHIFT]:
            movement -= camera.up * .01

        camera.pos += movement

        mesh.rot.x += 0.001
        mesh.rot.y += 0.002
        mesh.rot.z += 0.003

        screen.fill((0, 0, 0))

        vp_matrix = glm.mat4(1)
        vp_matrix = vp_matrix * glm.perspectiveFovLH(glm.radians(45), width, height, .1, 100)
        vp_matrix = vp_matrix * glm.lookAt(camera.pos, camera.target, camera.up)

        for m in mesh, mesh2:
            world_matrix = glm.mat4(1)
            world_matrix = glm.translate(world_matrix, m.pos)
            world_matrix = glm.rotate(world_matrix, m.rot.x, glm.vec3(1, 0, 0))
            world_matrix = glm.rotate(world_matrix, m.rot.y, glm.vec3(0, 1, 0))
            world_matrix = glm.rotate(world_matrix, m.rot.z, glm.vec3(0, 0, 1))
            world_matrix = glm.scale(world_matrix, m.scale)

            for v in m.vertices:
                point = glm.project(v, world_matrix, vp_matrix, glm.vec4(0, 0, width, height))
                if 0 < point.x < width and 0 < point.y < height:
                    pygame.gfxdraw.pixel(screen, int(point.x), int(point.y), (255, 255, 255))

        origin = glm.project(glm.vec3(0, 0, 0), glm.mat4(1), vp_matrix, glm.vec4(0, 0, width, height))
        for v in glm.vec3(1, 0, 0), glm.vec3(0, 1, 0), glm.vec3(0, 0, 1):
            p = glm.project(v, glm.mat4(1), vp_matrix, glm.vec4(0, 0, width, height))
            try:
                pygame.gfxdraw.line(screen, int(origin.x), int(origin.y), int(p.x), int(p.y),
                                    (v * glm.vec3(255, 255, 255)))
            except:
                pass

        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        screen.blit(font.render(f"camera pos: f{camera.pos}", True, (255, 255, 0)), (5, 5))
        screen.blit(font.render(f"camera target: f{camera.target}", True, (255, 255, 0)), (5, 20))

        pygame.display.flip()


if __name__ == "__main__":
    main()
