import hypatia.game
import hypatia.vfs

v = hypatia.vfs.VFS()
prov = hypatia.vfs.FilesystemProvider("demo")
v.mount("/game", prov)

g = hypatia.game.Game(v)

class TestStage(hypatia.game.Stage):
    def update(self):
        raise RuntimeError("This is a test!")

g.stage_jump(TestStage)
g.main_loop()