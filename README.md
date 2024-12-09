# TileCropper

It is way easier to draw isometric tiles grouped together. But most game engines require separating the tiles. This Godot plugin does it automatically for you!  

![](docs/isometric_transformation.png)

## Installation and usage

TileCropper is installed as a regular Godot plugin.
Just copy the `addons/TileCropper` folder to your Godot project, and enable it on *Project*, *Project settings...*, *Plugins*.  

A new **TileCropper** dock will appear on the upper-left corner, next to the *Scene* and *Import* docks:  

![](docs/dock.png)

You can now drag here your input tileset, and a single tile to be used as a cropping mask. You should also specify the number of tiles per side, which is 4 by default. Click the *Crop!* button, and you are done!  

Note that the size of the input images must match the size of the corresponding tileset and tile. In other words, do not use margins in these images.  


## Contributing

If you want to contribute to this open source project, please check the [contributing guidelines](CONTRIBUTING.md).  

This project has contributions from:
- Pablo Gila (@gilapixel)
- u/pideon_pete
