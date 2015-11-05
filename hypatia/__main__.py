import hypatia.game
import hypatia.vfs
import hypatia.state

v = hypatia.vfs.VFS()
prov = hypatia.vfs.FilesystemProvider("demo")
v.mount("/game", prov)

g = hypatia.game.Game(v)


class TestState(hypatia.state.State):
    def update(self):
        raise RuntimeError("This is a test!")

g.state_jump(TestState)
g.main_loop()
