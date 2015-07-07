# DTM2MESH
Stands for Digital Terrain Model To 3D Mesh, coded in **Python**.  
The mesh is exported in a [Collada](https://de.wikipedia.org/wiki/Collada_(Speicherformat)) file in order to be re-usable somewhere else.  
**Important Note :** This is not a Collada file viewer or any other kind of 3D mesh visualizer.  
**Less Important Note:** This project was made in 2 days, so be nice if you find mistakes...

![](https://raw.githubusercontent.com/jonathanlurie/DTM2MESH/master/doc/scheme.jpg)

## How to use

This is a Pythonic command-line tool.  

**The first argument** : *-input* , is the input DTM file, usually it's a TIFF (16bit) but it should work fine with any other format as long as it's a monoband (greyscale) file, and compatible with [OpenCV](https://github.com/Itseez/opencv). **This argument is mandatory**.  

**The second argument** : *-output* , is the output Collada file (.dae) which is actually some kind of super-fat XML. **This argument is mandatory**.  

**The third argument** : *-resolution* , is the ground resolution in meter/pixel. The default resolution is 90 (SRTM compliant), thus, **this argument is optional**.   
*Note :* If the ground resolution is lower than expected (ex: 50 with SRTM), it will result in an exaggerated relief. The opposite (ex: 150 with SRTM ) will induce a flattening effect.

*Example 1*

```shell
cd DTM2MESH
python DTM2MESH.py -input data/input/srtm_54_07_CROP_360.tif -output data/output/srtm_54_07_CROP_360.dae
```

*Example 2* : Big Mountains

```shell
cd DTM2MESH
python DTM2MESH.py -input data/input/srtm_54_07_CROP_360.tif -output data/output/srtm_54_07_CROP_360_BigMountains.dae -resolution 25
```

## Where to find DTM images

Good question. A lot of websites may provide that, coming from multiple sources. Though, A very convenient way to fetch [SRTM](https://en.wikipedia.org/wiki/Shuttle_Radar_Topography_Mission) tiles is from [Derek Watkins](https://twitter.com/dwtkns)'s [project](http://dwtkns.com/srtm). It's easy, and each archive comes with *header* files (with georeference among other things).  
You can also check Derek's [work](http://dwtkns.com/portfolio/) or [blog](http://blog.dwtkns.com/) if you are interested in map stuff.


## About Collada files

### Why in Collada?
Don't you think it's a bit frustrating to be able to generate a 3D mesh, and just visualize it in a window? The point is to **use** this mesh. Collada is an open format, compatible with famous 3D builders (3DS Max, Maya, Blender...). A terrain mesh could for example be used in a game or in a animation movie...

### How to visualize them
If you are using a Mac, this is part of it but it comes with very few options (none actually).  
I noticed [MeshLab](http://meshlab.sourceforge.net/) is not so bad but may jam when the file is too big.  
Since you have to use PyCollada, you can use the tinny Viewer inside this project. Again, if the file is too big, it might not work.  
Apparently SketchUp woks pretty fine as well, but I didn't try it.


## Limitations

### Performances
Since it's a pythonic tool, it is not focused on performances, even though Numpy and OpenCV both have low level core... So if you do not want to spend all night waiting for your Collada file, I advise you not to use input files bigger than 1500px by 1500px. (meaning you may have to crop your SRTM tiles...) 

### Algorithmic
I didn't look for a fancy algorithm to make a 3D mesh from greyscale 2D data, so I made it simple : **1 pixel =  2 triangles**, *(x, y)* in the image are *(x, y)* in the mesh, and grey value are the elevation, after being flattened by the *resolution factor*. If you follow, you will think: 

> « All right but if so, the last row and column must be missing in the 3D mesh! »  

**You would be pretty much right to think so!**



## Dependencies

- [OpenCV2](https://github.com/Itseez/opencv) (be sure Python bindings are activated)
- [PyCollada](https://github.com/pycollada/pycollada)


## Going further
*Collada* files, like *OBJ* files, are descriptive and simple text formats, meaning you could create them with more or less any language. To get better performances, DTM2MESH could be coded in C/C++.  Feel free to copy/paste the whole part about *vertices indexing* and *triangle index referencing*, because they are a lot of particular cases and you'd rather go play outside than spending an afternoon finding them...  

FYI, those two tricky parts are commented with:

```python
# PART 1:
# loops for computing the vertices positions
```

```python
# PART 2:
# loops for computing triangles.
# A triangle is made of 3 vertices, but we rather use indexes of vertices
# than vertices coordinates themselves (Collada specs are like that...)
```

Have fun.

