import pygame
import pygame.gfxdraw
import glm

from mesh import Mesh, Cube
from scene import Scene


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("minimal program")
    size = width, height = (320, 240)
    screen = pygame.display.set_mode((width * 4, height * 4))
    mesh = Mesh()
    mesh.load_obj("data/teapot.obj")
    mesh.scale = glm.vec3(.02, .02, .02)
    # mesh = Cube()
    # mesh.pos = glm.vec3(1, 1, 1)
    running = True

    scene = Scene(size)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_rel = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[0]:
            scene.camera.dir = glm.rotateY(scene.camera.dir, mouse_rel[0] * -0.01)
            scene.camera.dir = glm.rotateX(scene.camera.dir, mouse_rel[1] * -0.01)

        keys = pygame.key.get_pressed()
        movement = glm.vec3(0, 0, 0)
        if keys[pygame.K_w]:
            movement += scene.camera.dir * .1
        if keys[pygame.K_s]:
            movement -= scene.camera.dir * .1
        if keys[pygame.K_a]:
            movement -= glm.normalize(glm.cross(scene.camera.dir, scene.camera.up)) * .1
        if keys[pygame.K_d]:
            movement += glm.normalize(glm.cross(scene.camera.dir, scene.camera.up)) * .1
        if keys[pygame.K_SPACE]:
            movement += scene.camera.up * .1
        if keys[pygame.K_LSHIFT]:
            movement -= scene.camera.up * .1

        scene.camera.pos += movement

        mesh.rot.x += 0.01
        mesh.rot.y += 0.02
        mesh.rot.z += 0.03

        scene.clear()
        for m in mesh,:
            scene.draw_mesh_triangles_scan(m)

        scene.draw_origin()

        pygame.transform.scale(scene.surface, screen.get_size(), screen)

        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        screen.blit(font.render(str(int(clock.get_fps())), True, (255, 255, 0)), (5, 5))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
