import glm


class Camera:
    def __init__(self, size) -> None:
        self.size = size
        self.pos = glm.vec3(0, 0, 10)
        self.dir = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)

    @property
    def target(self):
        return self.pos + self.dir

    def vp_matrix(self):
        m = glm.mat4(1)
        m = m * glm.perspectiveFov(glm.radians(60), self.size[0], self.size[1], .1, 100)
        m = m * glm.scale(glm.vec3(1, -1, 1))
        return m * glm.lookAtRH(self.pos, self.target, self.up)
