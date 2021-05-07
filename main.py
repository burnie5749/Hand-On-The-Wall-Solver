# NOTHING SHOULD GO ABOVE THIS#
from direct import task
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import *
from panda3d.physics import *
from characterController.PlayerController import *
import gltf, sys, os
from direct.showbase.ShowBase import ShowBase, PointLight, Filename, AmbientLight

# loading window configs
loadPrcFile("config/configs.prc")





class MyApp(ShowBase, DirectObject):
    def __init__(self):
        ShowBase.__init__(self)

        gltf.patch_loader(self.loader)  # allows use of .gltf files
        self.accept("escape", sys.exit)  # Escape quits
        self.player = None  # instantiate player
        self.cTrav = CollisionTraverser("base collision traverser")

        self.pusher = CollisionHandlerPusher()
        self.disable_mouse()  # disables mouse controls not actual mouse
        # setup path for models
        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()
        self.jsonDir = Filename(self.mydir, 'config/configs.json').toOsSpecific()
        self.set_background_color((.1, .1, .1, 1))
        self.enableParticles()
        self.setupGravity()
        self.loadPlayer()
        self.setupLights()
        self.loadGround()
        self.loadMaze()
        self.playerSpeed = -3
        self.move = self.taskMgr.add(self.movePlayer, "move",)

    def setupGravity(self):
        """
        This function sets up the gravity force within the world,
        this is to stop the player from floating in mid-air and helps bring player back down to the ground.

        """
        gravityFN = ForceNode('world-forces')
        gravityFNP = self.render.attachNewNode(gravityFN)
        gravityForce = LinearVectorForce(0, 0, -9.81)  # gravity forces
        gravityFN.addForce(gravityForce)
        self.physicsMgr.addLinearForce(gravityForce)

    def loadPlayer(self):
        """

        This function instantiates and loads the player using the player controller
        also sets up the collisions for the player

        """

        self.cTrav.setRespectPrevTransform(True)
        self.player = PlayerController(self.cTrav, self.jsonDir)
        self.player.startPlayer()
        self.startPos = self.player.setStartPos(LVecBase3(10, -100, -4))

        self.player.setStartHpr(LVecBase3(180, 0, 0))
        self.player.changeCameraSystem("firstperson")

    def loadGround(self):
        """
            This function loads the ground environment model with its textures from the texture file
            it also sets up the floor colliders so that the player can walk along the floor and not fall through
        """

        self.ground = self.loader.loadModel(self.mydir + "/my-models/environment")
        self.ground.setScale(20, 20, 20)
        self.ground.setPos(0, 0, -5)
        self.ground.reparentTo(self.render)
        # setup collider for the environement around the maze

        self.envBound = self.ground.getBounds()
        self.envRad = self.envBound.getRadius() * 0.7
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        collisionPlaneNP = self.ground.attachNewNode(CollisionNode('cNode'))
        collisionPlaneNP.node().addSolid(plane)

    def loadMaze(self):
        # load maze
        self.maze = self.loader.loadModel(self.mydir + "/my-models/HamptonCourtMaze.bam")
        self.maze.setPos(10, 30, -5)

        self.maze.reparentTo(self.render)

        # setup the colliders for around the maze so the player cant leave the environement

        mazeBounds = self.maze.getBounds()
        mazeCentre = mazeBounds.getCenter()
        mazeRadius = mazeBounds.getRadius()
        fromObject = self.maze.attachNewNode(CollisionNode('colNode'))
        self.pusher.addCollider(fromObject, self.maze)


        cNode = CollisionNode("AreaBounds")
        cNode.addSolid(CollisionInvSphere(mazeCentre, mazeRadius))  # this is the environment bounding box

        mazeCollide = self.render.attachNewNode(cNode)
        mazeCollide.show()

    def setupLights(self):
        # lights
        self.ambientLight = self.render.attachNewNode(AmbientLight('ambient'))
        self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1))
        self.render.setLight(self.ambientLight)
        # directional lights
        self.dirLight = self.render.attachNewNode(DirectionalLight('directional'))
        self.dirLight.node().setColorTemperature(6500)

        # setup light vector
        lightFromBack = .4
        lightFromLeft = .2
        lightFromBottom = 1
        lightVec3 = Vec3(lightFromBack, lightFromLeft, lightFromBottom)
        lightVec3.normalize()
        self.dirLight.node().setDirection(lightVec3)
        self.render.setLight(self.dirLight)

        # add spotlight for shadows
        self.spotLight = self.render.attachNewNode(Spotlight('spot'))
        self.spotLight.node().setColor((1, 1, 1, 1))
        self.spotLight.node().setShadowCaster(True, 1024, 1024)

        # fitting near and far planes for the light
        self.spotLight.node().getLens().setNearFar(0.1, 20)
        # setting the light cone to be narrower
        self.spotLight.node().getLens().setFov(25)
        # smoother falloff
        self.spotLight.node().setExponent(120)
        self.spotLight.set_pos(-8, 0, 8)
        self.spotLight.lookAt(self.player, 0, 0, 5)
        self.render.setLight(self.spotLight)

        self.plight = PointLight('plight')
        self.plight.setShadowCaster(True, 512, 512)
        self.plight.setColor((1.5, 1.5, 1.5, 1))
        self.plightNP = self.render.attachNewNode(self.plight)
        self.plightNP.setPos(10, 10, 0)

        self.render.setLight(self.plightNP)


    def movePlayer(self, task):
        dt = globalClock.getDt()
        #
        self.player.plugin_setPos()
        return task.cont






app = MyApp()
app.run()
